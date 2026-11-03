"""Clearly labeled mock providers for offline demos."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.studio.db import studio_asset_dir
from app.studio.providers.base import (
    AudioGenerationProvider,
    ImageGenerationProvider,
    SafetyReviewProvider,
    TextGenerationProvider,
    TextToSpeechProvider,
    VideoGenerationProvider,
    YouTubeProvider,
)


class MockTextProvider(TextGenerationProvider):
    name = "mock_text"
    is_mock = True

    def available(self) -> bool:
        return True

    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        kind = kwargs.get("kind", "generic")
        if kind == "ideas":
            ideas = [
                {
                    "title": "The Glowing Puddle",
                    "premise": "Pip and Brio find a puddle that reflects sunset early.",
                },
                {
                    "title": "Mira's Quiet Song",
                    "premise": "Pip learns a calming song when the wind feels too busy.",
                },
                {
                    "title": "Leaf Map Adventure",
                    "premise": "A fallen leaf map leads friends to a new picnic spot.",
                },
            ]
            return {"provider": self.name, "is_mock": True, "ideas": ideas, "cost": 0.0}
        if kind == "script":
            title = kwargs.get("title", "Untitled")
            script = (
                f"Title: {title}\n\n"
                "SCENE 1 — Soft Hill Meadow\n"
                "Pip: Soft paws, bright day! What is that shimmer?\n"
                "Brio: Maybe my leaf gadget can listen to it.\n"
                "Mira: Let's look together — slowly and safely.\n\n"
                "SCENE 2 — Sky Puddle Pond\n"
                "Pip: It is only sunlight dancing. Still wonderful!\n"
                "Brio: My gadget learned a new sparkle song.\n"
                "Mira: Curiosity plus care makes Soft Hill glow for friends.\n\n"
                "[CTA] If you liked this adventure, you can like the video and subscribe "
                "for new stories. See you next time!"
            )
            return {"provider": self.name, "is_mock": True, "text": script, "cost": 0.0}
        if kind == "localize":
            language = kwargs.get("language", "en")
            return {
                "provider": self.name,
                "is_mock": True,
                "text": f"[{language} adaptation]\n{prompt[:2000]}",
                "cost": 0.0,
            }
        return {"provider": self.name, "is_mock": True, "text": f"[mock] {prompt[:1500]}", "cost": 0.0}


class MockImageProvider(ImageGenerationProvider):
    name = "mock_image"
    is_mock = True

    def available(self) -> bool:
        return True

    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        out_dir = studio_asset_dir("assets", "images")
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
        path = out_dir / f"mock-image-{digest}.json"
        payload = {"prompt": prompt, "note": "Mock image placeholder — not a real render."}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return {
            "provider": self.name,
            "is_mock": True,
            "path": str(path),
            "cost": None,
            "cost_label": "unknown",
        }


class MockVideoProvider(VideoGenerationProvider):
    name = "mock_video"
    is_mock = True

    def available(self) -> bool:
        return True

    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        out_dir = studio_asset_dir("renders", "clips")
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
        path = out_dir / f"mock-clip-{digest}.json"
        path.write_text(
            json.dumps({"prompt": prompt, "note": "Mock video clip placeholder"}, indent=2),
            encoding="utf-8",
        )
        return {
            "provider": self.name,
            "is_mock": True,
            "path": str(path),
            "duration_sec": kwargs.get("duration_sec", 8),
            "cost": 0.0,
        }

    def assemble(self, **kwargs: Any) -> dict[str, Any]:
        # Also used as mock assembly fallback.
        out_dir = studio_asset_dir("renders")
        episode_id = kwargs.get("episode_id", "unknown")
        path = out_dir / f"mock-final-{episode_id}.json"
        payload = {
            "episode_id": episode_id,
            "scenes": kwargs.get("scene_paths") or [],
            "note": "Mock final render placeholder. Replace with real assembly when providers available.",
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        return {
            "provider": self.name,
            "is_mock": True,
            "path": str(path),
            "checksum": checksum,
            "duration_sec": kwargs.get("duration_sec", 390),
            "cost": 0.0,
        }


class MockTTSProvider(TextToSpeechProvider):
    name = "mock_tts"
    is_mock = True

    def available(self) -> bool:
        return True

    def synthesize(self, text: str, **kwargs: Any) -> dict[str, Any]:
        out_dir = studio_asset_dir("assets", "audio")
        path = out_dir / f"mock-tts-{uuid4().hex[:10]}.txt"
        path.write_text(text, encoding="utf-8")
        return {
            "provider": self.name,
            "is_mock": True,
            "path": str(path),
            "duration_sec": max(3.0, len(text.split()) * 0.4),
            "cost": 0.0,
        }


class MockAudioProvider(AudioGenerationProvider):
    name = "mock_audio"
    is_mock = True

    def available(self) -> bool:
        return True

    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        out_dir = studio_asset_dir("assets", "audio")
        path = out_dir / f"mock-bgm-{uuid4().hex[:10]}.json"
        path.write_text(json.dumps({"prompt": prompt, "is_mock": True}), encoding="utf-8")
        return {"provider": self.name, "is_mock": True, "path": str(path), "cost": 0.0}


class MockSafetyProvider(SafetyReviewProvider):
    name = "mock_safety"
    is_mock = True

    def available(self) -> bool:
        return True

    def review(self, content: str, **kwargs: Any) -> dict[str, Any]:
        lowered = content.lower()
        flags = []
        for term, code in (
            ("kill", "violence"),
            ("blood", "violence"),
            ("nightmare", "fear"),
            ("you must subscribe", "manipulative_cta"),
            ("or else", "coercion"),
        ):
            if term in lowered:
                flags.append({"code": code, "term": term, "severity": "high"})
        return {
            "provider": self.name,
            "is_mock": True,
            "passed": not flags,
            "flags": flags,
            "age_band": kwargs.get("age_band", "3-6"),
            "disclaimer": "Heuristic mock safety review — not infallible.",
            "cost": 0.0,
        }


class MockYouTubeProvider(YouTubeProvider):
    name = "mock_youtube"
    is_mock = True

    def available(self) -> bool:
        return True

    def upload(self, **kwargs: Any) -> dict[str, Any]:
        video_id = f"mock_{uuid4().hex[:11]}"
        return {
            "provider": self.name,
            "is_mock": True,
            "youtube_video_id": video_id,
            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
            "status": "uploaded_mock",
            "note": "Mock upload — no real YouTube API call was made.",
        }
