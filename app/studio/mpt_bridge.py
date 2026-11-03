"""Bridge: Animation Studio episodes → MoneyPrinterTurbo task.start pipeline."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4

from loguru import logger

from app.models.schema import VideoAspect, VideoParams
from app.studio.db import studio_asset_dir
from app.utils import utils


class MPTBridgeError(Exception):
    pass


def _default_voice(language: str) -> str:
    lang = (language or "en").lower()
    if lang.startswith("tr"):
        return "tr-TR-EmelNeural-Female"
    if lang.startswith("es"):
        return "es-ES-ElviraNeural-Female"
    if lang.startswith("de"):
        return "de-DE-KatjaNeural-Female"
    return "en-US-AnaNeural-Female"


def _script_for_mpt(episode_script: str, title: str, synopsis: str) -> str:
    """
    Convert studio script to narration-friendly text for MPT TTS.

    Keeps dialogue lines but strips SCENE headers and CTA markers that
    confuse stock-footage keyword search less when folded into plain prose.
    """
    lines: list[str] = []
    for raw in (episode_script or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        upper = line.upper()
        if upper.startswith("SCENE ") or upper.startswith("TITLE:"):
            continue
        if upper.startswith("[CTA]") or upper.startswith("CTA"):
            # Keep a gentle end invitation without bracket noise.
            line = line.split("]", 1)[-1].strip() or line
        # "Pip: hello" → keep spoken text with light attribution
        if ":" in line and len(line.split(":", 1)[0].split()) <= 3:
            speaker, speech = line.split(":", 1)
            speech = speech.strip()
            if speech:
                lines.append(speech)
            continue
        lines.append(line)
    text = " ".join(lines).strip()
    if text:
        return text
    return synopsis.strip() or title.strip() or "A gentle family adventure."


def build_video_params(
    *,
    title: str,
    script: str,
    synopsis: str = "",
    language: str = "en",
    content_format: str = "long_form",
    video_source: str | None = None,
) -> VideoParams:
    from app.config import config

    source = video_source or config.app.get("video_source") or "pexels"
    aspect = (
        VideoAspect.portrait
        if content_format == "shorts"
        else VideoAspect.landscape
    )
    safe_title = (title or "").strip() or (synopsis or "").strip() or "Soft Hill Friends Adventure"
    narration = _script_for_mpt(script, safe_title, synopsis)
    if not (narration or "").strip():
        narration = (
            f"{safe_title}. Friends explore together, learn something kind, "
            "and end the day feeling safe and happy."
        )
    # Keywords from title/synopsis help stock search when script is pre-filled.
    terms = ", ".join(
        part
        for part in [
            safe_title,
            synopsis[:120] if synopsis else "",
            "family animation friendly kids nature",
        ]
        if part
    )
    voice = config.app.get("studio_default_voice") or _default_voice(language)
    return VideoParams(
        video_subject=safe_title,
        video_script=narration.strip(),
        video_terms=terms,
        video_aspect=aspect,
        video_source=source,
        video_language=language or "",
        voice_name=voice,
        voice_rate=float(config.app.get("studio_voice_rate") or 1.0),
        subtitle_enabled=True,
        paragraph_number=1,
        video_count=1,
        video_clip_duration=int(config.app.get("studio_clip_duration") or 5),
        match_materials_to_script=True,
    )


def run_mpt_generation(
    *,
    episode_id: str,
    title: str,
    script: str,
    synopsis: str = "",
    language: str = "en",
    content_format: str = "long_form",
    video_source: str | None = None,
) -> dict[str, Any]:
    """
    Run MoneyPrinterTurbo's shared pipeline and copy the final MP4 into studio storage.
    """
    from app.services import task as tm
    from app.utils.utils import check_ffmpeg_ready

    if not check_ffmpeg_ready():
        raise MPTBridgeError(
            "FFmpeg is not ready. Install FFmpeg or set IMAGEIO_FFMPEG_EXE before producing Studio videos."
        )

    params = build_video_params(
        title=title,
        script=script,
        synopsis=synopsis,
        language=language,
        content_format=content_format,
        video_source=video_source,
    )
    task_id = f"studio-{episode_id[:8]}-{uuid4().hex[:8]}"
    logger.info(
        f"studio→MPT start: task_id={task_id}, source={params.video_source}, "
        f"aspect={params.video_aspect}, episode={episode_id}"
    )
    result = tm.start(task_id, params, stop_at="video")
    if not isinstance(result, dict):
        raise MPTBridgeError(f"MPT pipeline returned unexpected result: {type(result)}")

    # Failed tasks return error fields without videos.
    videos = result.get("videos") or []
    if not videos:
        error = result.get("error") or result.get("message") or "no videos produced"
        raise MPTBridgeError(f"MPT generation failed: {error}")

    source_path = Path(videos[0])
    if not source_path.is_file():
        raise MPTBridgeError(f"MPT final video missing on disk: {source_path}")

    out_dir = studio_asset_dir("renders", episode_id)
    dest = out_dir / f"final-{source_path.name}"
    shutil.copy2(source_path, dest)
    checksum = hashlib.sha256(dest.read_bytes()).hexdigest()

    return {
        "provider": "mpt_ffmpeg",
        "is_mock": False,
        "path": str(dest),
        "checksum": checksum,
        "duration_sec": result.get("audio_duration"),
        "mpt_task_id": task_id,
        "mpt_task_dir": utils.task_dir(task_id),
        "source_video": str(source_path),
        "videos": videos,
        "script_used": result.get("script") or params.video_script,
        "terms": result.get("terms"),
        "cost": None,
        "cost_label": "unknown",
    }


def upload_post_youtube_status() -> dict[str, Any]:
    from app.config import config
    from app.services.upload_post import upload_post_service

    platforms = list(config.app.get("upload_post_platforms") or [])
    youtube_enabled = any(str(p).startswith("youtube") for p in platforms)
    return {
        "configured": upload_post_service.is_configured(),
        "enabled": bool(config.app.get("upload_post_enabled")),
        "username": config.app.get("upload_post_username") or "",
        "has_api_key": bool(config.app.get("upload_post_api_key")),
        "platforms": platforms,
        "youtube_in_platforms": youtube_enabled,
        "privacy": upload_post_service.youtube_privacy_status,
        "made_for_kids_default": upload_post_service.youtube_made_for_kids,
        "ready_for_studio_publish": upload_post_service.is_configured() and youtube_enabled,
    }
