"""Provider interfaces and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TextGenerationProvider(ABC):
    name: str = "text"
    is_mock: bool = False

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class ImageGenerationProvider(ABC):
    name: str = "image"
    is_mock: bool = False

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class VideoGenerationProvider(ABC):
    name: str = "video"
    is_mock: bool = False

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class TextToSpeechProvider(ABC):
    name: str = "tts"
    is_mock: bool = False

    @abstractmethod
    def synthesize(self, text: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class AudioGenerationProvider(ABC):
    name: str = "audio"
    is_mock: bool = False

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class VideoAssemblyProvider(ABC):
    name: str = "assembly"
    is_mock: bool = False

    @abstractmethod
    def assemble(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class SafetyReviewProvider(ABC):
    name: str = "safety"
    is_mock: bool = False

    @abstractmethod
    def review(self, content: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class YouTubeProvider(ABC):
    name: str = "youtube"
    is_mock: bool = False

    @abstractmethod
    def upload(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


def get_provider(category: str, prefer_real: bool = False):
    from app.studio.providers import mock as mock_providers
    from app.studio.providers import mpt_adapters

    registry: dict[str, list] = {
        "text": [mpt_adapters.MPTTextProvider(), mock_providers.MockTextProvider()],
        "image": [mock_providers.MockImageProvider()],
        "video": [mock_providers.MockVideoProvider()],
        "tts": [mpt_adapters.MPTTTSProvider(), mock_providers.MockTTSProvider()],
        "audio": [mock_providers.MockAudioProvider()],
        "assembly": [mpt_adapters.MPTAssemblyProvider(), mock_providers.MockVideoProvider()],
        "safety": [mock_providers.MockSafetyProvider()],
        "youtube": [
            mpt_adapters.UploadPostYouTubeProvider(),
            mpt_adapters.YouTubeDataApiProvider(),
            mock_providers.MockYouTubeProvider(),
        ],
    }
    options = registry.get(category) or []
    if prefer_real:
        for option in options:
            if not getattr(option, "is_mock", True) and getattr(option, "available", lambda: True)():
                return option
    for option in options:
        if getattr(option, "available", lambda: True)():
            return option
    return options[0] if options else mock_providers.MockTextProvider()
