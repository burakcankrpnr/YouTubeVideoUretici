"""Demo seed data for Animation Studio first launch."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.studio.db import get_session, init_studio_db
from app.studio.enums import AutomationMode, CharacterDesignStatus
from app.studio.models import (
    Channel,
    ChannelSeries,
    Character,
    CharacterDesignVersion,
    CharacterRelationship,
    ProviderConfig,
    Series,
    SeriesBible,
    StoryArc,
    StudioSettings,
)
from app.studio.workflow import write_audit


def _seed_providers(session: Session) -> None:
    if session.query(ProviderConfig).count():
        return
    defaults = [
        ("text", "mock_text", True),
        ("text", "mpt_llm", False),
        ("image", "mock_image", True),
        ("video", "mock_video", True),
        ("tts", "mock_tts", True),
        ("tts", "mpt_voice", False),
        ("audio", "mock_audio", True),
        ("safety", "mock_safety", True),
        ("youtube", "upload_post_youtube", False),
        ("youtube", "mock_youtube", True),
        ("assembly", "mpt_ffmpeg", False),
        ("assembly", "mock_video", True),
    ]
    for index, (category, provider_id, is_mock) in enumerate(defaults):
        session.add(
            ProviderConfig(
                category=category,
                provider_id=provider_id,
                enabled=True,
                is_mock=is_mock,
                priority=index * 10,
                settings={"label": provider_id},
            )
        )


def ensure_demo_seed() -> dict[str, str]:
    """Create DB schema and seed a global family-friendly demo series if empty."""
    init_studio_db()
    with get_session() as session:
        settings = session.query(StudioSettings).first()
        if settings is None:
            settings = StudioSettings()
            session.add(settings)

        _seed_providers(session)

        existing = session.query(Series).first()
        if existing is not None:
            channel = session.query(Channel).first()
            # Keep existing installs on the daily long + Shorts cadence
            if channel is not None:
                channel.max_uploads_per_week = max(int(channel.max_uploads_per_week or 0), 14)
                channel.long_form_enabled = True
                channel.shorts_enabled = True
                if not channel.publishing_windows or len(channel.publishing_windows) < 7:
                    channel.publishing_windows = [
                        {"day": d, "hour": 15, "format": "long_form"}
                        for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
                    ] + [
                        {"day": d, "hour": 17, "format": "shorts"}
                        for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
                    ]
                if float(channel.budget_monthly or 0) < 500:
                    channel.budget_monthly = 500.0
            return {
                "series_id": existing.id,
                "channel_id": channel.id if channel else "",
                "seeded": "false",
            }

        # Cadence: 1 long-form + 1 Shorts every day ≈ 14 uploads/week
        daily_windows = [
            {"day": d, "hour": 15, "format": "long_form"}
            for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
        ] + [
            {"day": d, "hour": 17, "format": "shorts"}
            for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
        ]
        channel = Channel(
            name="Pip & Friends (Demo Channel)",
            language="en",
            locale="en-US",
            timezone="UTC",
            description="Demo destination for Global AI Animation Studio.",
            audience_designation="made_for_kids",
            automation_mode=AutomationMode.ASSISTED.value,
            auto_publish_enabled=False,
            age_band="3-6",
            keywords=["family", "animation", "kids", "friendship"],
            publishing_windows=daily_windows,
            max_uploads_per_week=14,
            long_form_enabled=True,
            shorts_enabled=True,
            budget_per_episode=8.0,
            budget_monthly=500.0,
        )
        session.add(channel)
        session.flush()

        series = Series(
            title="Pip & the Soft Hill Friends",
            premise=(
                "Pip is a curious little cloud-fox who lives with their family on Soft Hill. "
                "Each episode follows a gentle discovery with friends and caregivers."
            ),
            age_band="3-6",
            tone="Warm, playful, calm, curious",
            themes=["friendship", "curiosity", "kindness", "everyday discovery"],
            educational_domains=["social_emotional", "language", "curiosity"],
            primary_language="en",
            target_duration_min=5,
            target_duration_max=8,
            approved=True,
            brand_kit={
                "palette": ["#F6E7C1", "#7EB6A4", "#F28C58"],
                "style": "soft 2D animation, rounded shapes, gentle lighting",
            },
            content_boundaries=[
                "no frightening cliffhangers",
                "no manipulative CTAs",
                "no dangerous imitation",
            ],
        )
        session.add(series)
        session.flush()

        session.add(ChannelSeries(channel_id=channel.id, series_id=series.id))

        bible = SeriesBible(
            series_id=series.id,
            version=1,
            is_current=True,
            approved=True,
            content={
                "locations": ["Soft Hill Meadow", "Moss Cottage", "Sky Puddle Pond"],
                "world_rules": [
                    "Magic is gentle and never frightening.",
                    "Caregivers are present and supportive.",
                ],
                "catchphrases": ["Soft paws, bright day!"],
            },
            continuity_memory={
                "episode_summaries": [],
                "character_state": {},
                "unresolved_arcs": ["What makes Soft Hill glow at dusk?"],
                "used_plots": [],
            },
        )
        session.add(bible)

        pip = Character(
            series_id=series.id,
            name="Pip",
            role="main",
            age_range="child",
            personality="Curious, kind, a little shy at first",
            motivations="Discover how things work and help friends",
            habits="Asks questions out loud; wiggles ears when thinking",
            strengths="Empathy, observation",
            flaws="Sometimes rushes before asking for help",
            speech_patterns="Short warm sentences; wonder aloud",
            backstory="Youngest cloud-fox of Moss Cottage",
            status=CharacterDesignStatus.APPROVED.value,
            voice_profile={"tone": "gentle child", "language": "en"},
        )
        mama = Character(
            series_id=series.id,
            name="Mira",
            role="parent",
            age_range="adult",
            personality="Calm, encouraging, playful",
            motivations="Support Pip's curiosity safely",
            habits="Hums while cooking moss tea",
            strengths="Patience",
            flaws="Sometimes explains a bit too much",
            speech_patterns="Warm caregiver voice",
            backstory="Pip's parent; keeper of Moss Cottage",
            status=CharacterDesignStatus.APPROVED.value,
            voice_profile={"tone": "warm adult", "language": "en"},
        )
        brio = Character(
            series_id=series.id,
            name="Brio",
            role="friend",
            age_range="child",
            personality="Cheerful beetle inventor",
            motivations="Build helpful gadgets from fallen leaves",
            habits="Sketches ideas in dirt",
            strengths="Creativity",
            flaws="Gadgets sometimes flop gently",
            speech_patterns="Excited, inventive",
            backstory="Pip's best friend from Meadow Path",
            status=CharacterDesignStatus.APPROVED.value,
            voice_profile={"tone": "bright child", "language": "en"},
        )
        session.add_all([pip, mama, brio])
        session.flush()

        for character, attrs in (
            (
                pip,
                {
                    "species": "cloud-fox",
                    "colors": {"fur": "#F6E7C1", "accents": "#F28C58"},
                    "features": "round ears, soft cloud-like tail tip",
                    "outfit": "leaf scarf",
                },
            ),
            (
                mama,
                {
                    "species": "cloud-fox",
                    "colors": {"fur": "#E8D4B0", "accents": "#7EB6A4"},
                    "features": "taller, gentle eyes",
                    "outfit": "woven meadow vest",
                },
            ),
            (
                brio,
                {
                    "species": "beetle",
                    "colors": {"shell": "#7EB6A4", "belly": "#F6E7C1"},
                    "features": "tiny goggles",
                    "outfit": "tool sash",
                },
            ),
        ):
            design = CharacterDesignVersion(
                character_id=character.id,
                version=1,
                status=CharacterDesignStatus.APPROVED.value,
                attributes=attrs,
                reference_assets=[],
                prompt_config={"style": series.brand_kit.get("style")},
            )
            session.add(design)
            session.flush()
            character.approved_design_version_id = design.id

        session.add_all(
            [
                CharacterRelationship(
                    from_character_id=pip.id,
                    to_character_id=mama.id,
                    relationship_type="child_of",
                    notes="Supportive parent-child bond",
                ),
                CharacterRelationship(
                    from_character_id=pip.id,
                    to_character_id=brio.id,
                    relationship_type="best_friend",
                    notes="Play and invent together",
                ),
            ]
        )

        session.add(
            StoryArc(
                series_id=series.id,
                title="Soft Hill Glow Mystery",
                premise="Pip and friends gently explore why Soft Hill glows at dusk.",
                milestones=[
                    {"episode_hint": 1, "beat": "Notice the glow"},
                    {"episode_hint": 4, "beat": "Find a friendly firefly clue"},
                    {"episode_hint": 8, "beat": "Learn the hill shares light with friends"},
                ],
                open_questions=["What makes Soft Hill glow at dusk?"],
                approved=True,
            )
        )

        write_audit(
            session,
            action="studio.seeded",
            entity_type="series",
            entity_id=series.id,
            details={"channel_id": channel.id, "demo": True},
            actor="system",
        )
        session.flush()
        return {"series_id": series.id, "channel_id": channel.id, "seeded": "true"}
