"""Adapters that reuse MoneyPrinterTurbo LLM/voice/assembly/YouTube upload."""

from __future__ import annotations

import hashlib
from typing import Any

from loguru import logger

from app.studio.db import studio_asset_dir
from app.studio.providers.base import (
    TextGenerationProvider,
    TextToSpeechProvider,
    VideoAssemblyProvider,
    YouTubeProvider,
)


class MPTTextProvider(TextGenerationProvider):
    name = "mpt_llm"
    is_mock = False

    def available(self) -> bool:
        try:
            from app.config import config

            provider = config.app.get("llm_provider")
            if not provider:
                return False
            key_name = f"{provider}_api_key"
            return bool(config.app.get(key_name) or provider in {"ollama", "openai_compatible"})
        except Exception:
            return False

    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        from app.services import llm

        kind = kwargs.get("kind", "generic")
        try:
            subject = kwargs.get("title") or kwargs.get("subject") or prompt[:200]
            text = llm.generate_script(
                video_subject=subject,
                language=kwargs.get("language", "en-US"),
                paragraph_number=kwargs.get("paragraphs", 3 if kind == "script" else 2),
            )
            return {"provider": self.name, "is_mock": False, "text": text, "cost": None}
        except Exception as exc:
            logger.warning(f"MPT text provider failed, caller should fallback: {exc}")
            raise


class MPTTTSProvider(TextToSpeechProvider):
    name = "mpt_voice"
    is_mock = False

    def available(self) -> bool:
        return True

    def synthesize(self, text: str, **kwargs: Any) -> dict[str, Any]:
        from app.services import voice

        out_dir = studio_asset_dir("assets", "audio")
        path = out_dir / f"mpt-tts-{hashlib.sha256(text.encode()).hexdigest()[:12]}.mp3"
        voice_name = kwargs.get("voice_name") or "en-US-AnaNeural"
        try:
            sub_maker = voice.tts(
                text=text,
                voice_name=voice_name,
                voice_rate=kwargs.get("voice_rate", 1.0),
                voice_file=str(path),
            )
            duration = voice.get_audio_duration(str(path)) if path.exists() else None
            return {
                "provider": self.name,
                "is_mock": False,
                "path": str(path),
                "duration_sec": duration,
                "sub_maker": bool(sub_maker),
                "cost": None,
            }
        except Exception as exc:
            logger.warning(f"MPT TTS failed: {exc}")
            raise


class MPTAssemblyProvider(VideoAssemblyProvider):
    """Runs the real MoneyPrinterTurbo task.start pipeline for an episode."""

    name = "mpt_ffmpeg"
    is_mock = False

    def available(self) -> bool:
        try:
            from app.utils.utils import check_ffmpeg_ready

            return bool(check_ffmpeg_ready())
        except Exception:
            return False

    def assemble(self, **kwargs: Any) -> dict[str, Any]:
        from app.studio.mpt_bridge import MPTBridgeError, run_mpt_generation

        episode = kwargs.get("episode")
        episode_id = kwargs.get("episode_id") or (getattr(episode, "id", None) if episode else None)
        if not episode_id:
            raise RuntimeError("MPT assembly requires episode_id")

        title = kwargs.get("title") or getattr(episode, "title", "") or "Studio episode"
        script = kwargs.get("script") or getattr(episode, "script", "") or ""
        synopsis = kwargs.get("synopsis") or getattr(episode, "synopsis", "") or ""
        language = kwargs.get("language") or getattr(episode, "language", "en") or "en"
        content_format = (
            kwargs.get("content_format")
            or getattr(episode, "content_format", "long_form")
            or "long_form"
        )
        try:
            return run_mpt_generation(
                episode_id=str(episode_id),
                title=title,
                script=script,
                synopsis=synopsis,
                language=language,
                content_format=content_format,
                video_source=kwargs.get("video_source"),
            )
        except MPTBridgeError:
            raise
        except Exception as exc:
            logger.exception(f"MPT assembly failed: {exc}")
            raise RuntimeError(f"MPT assembly failed: {exc}") from exc


class UploadPostYouTubeProvider(YouTubeProvider):
    """Publish via MoneyPrinterTurbo's existing Upload-Post YouTube integration."""

    name = "upload_post_youtube"
    is_mock = False

    def available(self) -> bool:
        from app.studio.mpt_bridge import upload_post_youtube_status

        return bool(upload_post_youtube_status().get("ready_for_studio_publish"))

    def upload(self, **kwargs: Any) -> dict[str, Any]:
        from app.services.upload_post import UploadPostService

        media_path = kwargs.get("media_path") or ""
        title = (kwargs.get("title") or "Studio episode")[:100]
        description = kwargs.get("description") or ""
        privacy = kwargs.get("privacy_status") or "private"
        made_for_kids = bool(kwargs.get("made_for_kids", True))

        service = UploadPostService()
        if not self.available():
            raise RuntimeError(
                "Upload-Post YouTube is not ready. In MoneyPrinterTurbo settings enable "
                "Upload-Post, set API key + username, and include 'youtube' in platforms."
            )

        result = service.upload_video(
            video_path=media_path,
            title=title,
            platforms=["youtube"],
            youtube_extra={
                "youtube_title": title,
                "youtube_description": description,
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": made_for_kids,
                "containsSyntheticMedia": True,
                "tags": list(kwargs.get("tags") or []),
            },
        )
        if not result.get("success"):
            raise RuntimeError(result.get("error") or "Upload-Post YouTube upload failed")

        video_id, url = _extract_youtube_identity(result)
        return {
            "provider": self.name,
            "is_mock": False,
            "youtube_video_id": video_id,
            "youtube_url": url,
            "status": "uploaded",
            "raw": result,
            "request_id": result.get("request_id"),
        }


class YouTubeDataApiProvider(YouTubeProvider):
    name = "youtube_data_api"
    is_mock = False

    def available(self) -> bool:
        # Prefer Upload-Post for this project; native Data API OAuth is a later path.
        return False

    def upload(self, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError(
            "Native YouTube Data API OAuth is not configured. "
            "Use Upload-Post YouTube (upload_post_youtube) from MPT settings."
        )


def _extract_youtube_identity(result: dict[str, Any]) -> tuple[str | None, str | None]:
    """Best-effort parse of Upload-Post response shapes for YouTube ids/urls."""
    video_id = None
    url = None

    results = result.get("results")
    entries: list[Any] = []
    if isinstance(results, dict):
        entries = list(results.values())
        yt = results.get("youtube") or results.get("YouTube")
        if isinstance(yt, dict):
            entries.insert(0, yt)
    elif isinstance(results, list):
        entries = results

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        platform = str(entry.get("platform") or "").lower()
        if platform and "youtube" not in platform:
            continue
        video_id = (
            entry.get("video_id")
            or entry.get("id")
            or entry.get("youtube_video_id")
            or video_id
        )
        url = entry.get("url") or entry.get("youtube_url") or url
        if video_id or url:
            break

    if not video_id:
        video_id = result.get("youtube_video_id") or result.get("video_id")
    if not url:
        url = result.get("youtube_url") or result.get("url")
    if video_id and not url:
        url = f"https://www.youtube.com/watch?v={video_id}"
    return video_id, url
