"""Provider adapters for Animation Studio."""

from app.studio.providers.base import (
    AudioGenerationProvider,
    ImageGenerationProvider,
    SafetyReviewProvider,
    TextGenerationProvider,
    TextToSpeechProvider,
    VideoAssemblyProvider,
    VideoGenerationProvider,
    YouTubeProvider,
    get_provider,
)
from app.studio.providers.mock import (
    MockAudioProvider,
    MockImageProvider,
    MockSafetyProvider,
    MockTextProvider,
    MockTTSProvider,
    MockVideoProvider,
    MockYouTubeProvider,
)
from app.studio.providers.mpt_adapters import (
    MPTAssemblyProvider,
    UploadPostYouTubeProvider,
)

__all__ = [
    "AudioGenerationProvider",
    "ImageGenerationProvider",
    "MPTAssemblyProvider",
    "MockAudioProvider",
    "MockImageProvider",
    "MockSafetyProvider",
    "MockTTSProvider",
    "MockTextProvider",
    "MockVideoProvider",
    "MockYouTubeProvider",
    "SafetyReviewProvider",
    "TextGenerationProvider",
    "TextToSpeechProvider",
    "UploadPostYouTubeProvider",
    "VideoAssemblyProvider",
    "VideoGenerationProvider",
    "YouTubeProvider",
    "get_provider",
]
