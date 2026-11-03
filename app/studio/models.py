"""SQLAlchemy models for Global AI Animation Studio."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class StudioSettings(Base, TimestampMixin):
    __tablename__ = "studio_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    global_pause: Mapped[bool] = mapped_column(Boolean, default=False)
    default_timezone: Mapped[str] = mapped_column(String(64), default="Europe/Istanbul")
    default_language: Mapped[str] = mapped_column(String(16), default="en")
    default_age_band: Mapped[str] = mapped_column(String(32), default="3-6")
    default_duration_min: Mapped[int] = mapped_column(Integer, default=5)
    default_duration_max: Mapped[int] = mapped_column(Integer, default=8)
    owner_pin_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    extra: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class Channel(Base, TimestampMixin):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200))
    language: Mapped[str] = mapped_column(String(16), default="en")
    locale: Mapped[str] = mapped_column(String(32), default="en-US")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    target_markets: Mapped[list[Any]] = mapped_column(JSON, default=list)
    keywords: Mapped[list[Any]] = mapped_column(JSON, default=list)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    audience_designation: Mapped[str] = mapped_column(String(64), default="made_for_kids")
    youtube_channel_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    oauth_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    oauth_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    connection_health: Mapped[str] = mapped_column(String(32), default="disconnected")
    automation_mode: Mapped[str] = mapped_column(String(32), default="assisted")
    auto_publish_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    pause_automation: Mapped[bool] = mapped_column(Boolean, default=False)
    max_uploads_per_week: Mapped[int] = mapped_column(Integer, default=14)
    publishing_windows: Mapped[list[Any]] = mapped_column(JSON, default=list)
    budget_daily: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_monthly: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_per_episode: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    age_band: Mapped[str] = mapped_column(String(32), default="3-6")
    long_form_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    shorts_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_defaults: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    series_links: Mapped[list["ChannelSeries"]] = relationship(back_populates="channel")
    episodes: Mapped[list["Episode"]] = relationship(back_populates="channel")


class Series(Base, TimestampMixin):
    __tablename__ = "series"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(200))
    premise: Mapped[str] = mapped_column(Text, default="")
    age_band: Mapped[str] = mapped_column(String(32), default="3-6")
    tone: Mapped[str] = mapped_column(Text, default="")
    themes: Mapped[list[Any]] = mapped_column(JSON, default=list)
    educational_domains: Mapped[list[Any]] = mapped_column(JSON, default=list)
    primary_language: Mapped[str] = mapped_column(String(16), default="en")
    target_duration_min: Mapped[int] = mapped_column(Integer, default=5)
    target_duration_max: Mapped[int] = mapped_column(Integer, default=8)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    brand_kit: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    content_boundaries: Mapped[list[Any]] = mapped_column(JSON, default=list)

    bible_versions: Mapped[list["SeriesBible"]] = relationship(back_populates="series")
    characters: Mapped[list["Character"]] = relationship(back_populates="series")
    episodes: Mapped[list["Episode"]] = relationship(back_populates="series")
    channel_links: Mapped[list["ChannelSeries"]] = relationship(back_populates="series")
    arcs: Mapped[list["StoryArc"]] = relationship(back_populates="series")


class ChannelSeries(Base, TimestampMixin):
    __tablename__ = "channel_series"
    __table_args__ = (UniqueConstraint("channel_id", "series_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"))
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    channel: Mapped[Channel] = relationship(back_populates="series_links")
    series: Mapped[Series] = relationship(back_populates="channel_links")


class SeriesBible(Base, TimestampMixin):
    __tablename__ = "series_bibles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    continuity_memory: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    series: Mapped[Series] = relationship(back_populates="bible_versions")


class Character(Base, TimestampMixin):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"))
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(64), default="main")
    age_range: Mapped[str] = mapped_column(String(32), default="")
    personality: Mapped[str] = mapped_column(Text, default="")
    motivations: Mapped[str] = mapped_column(Text, default="")
    habits: Mapped[str] = mapped_column(Text, default="")
    strengths: Mapped[str] = mapped_column(Text, default="")
    flaws: Mapped[str] = mapped_column(Text, default="")
    voice_profile: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    speech_patterns: Mapped[str] = mapped_column(Text, default="")
    backstory: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="draft")
    approved_design_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    series: Mapped[Series] = relationship(back_populates="characters")
    designs: Mapped[list["CharacterDesignVersion"]] = relationship(back_populates="character")
    relationships_from: Mapped[list["CharacterRelationship"]] = relationship(
        back_populates="from_character",
        foreign_keys="CharacterRelationship.from_character_id",
    )


class CharacterDesignVersion(Base, TimestampMixin):
    __tablename__ = "character_design_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    attributes: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    reference_assets: Mapped[list[Any]] = mapped_column(JSON, default=list)
    prompt_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    owner_notes: Mapped[str] = mapped_column(Text, default="")
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    character: Mapped[Character] = relationship(back_populates="designs")


class CharacterRelationship(Base, TimestampMixin):
    __tablename__ = "character_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    from_character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"))
    to_character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"))
    relationship_type: Mapped[str] = mapped_column(String(64))
    notes: Mapped[str] = mapped_column(Text, default="")

    from_character: Mapped[Character] = relationship(
        back_populates="relationships_from",
        foreign_keys=[from_character_id],
    )


class StoryArc(Base, TimestampMixin):
    __tablename__ = "story_arcs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"))
    title: Mapped[str] = mapped_column(String(200))
    premise: Mapped[str] = mapped_column(Text, default="")
    milestones: Mapped[list[Any]] = mapped_column(JSON, default=list)
    open_questions: Mapped[list[Any]] = mapped_column(JSON, default=list)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)

    series: Mapped[Series] = relationship(back_populates="arcs")


class StoryIdea(Base, TimestampMixin):
    __tablename__ = "story_ideas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"))
    title: Mapped[str] = mapped_column(String(200))
    premise: Mapped[str] = mapped_column(Text, default="")
    educational_hooks: Mapped[list[Any]] = mapped_column(JSON, default=list)
    selected: Mapped[bool] = mapped_column(Boolean, default=False)
    score_notes: Mapped[str] = mapped_column(Text, default="")


class Episode(Base, TimestampMixin):
    __tablename__ = "episodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"))
    channel_id: Mapped[Optional[str]] = mapped_column(ForeignKey("channels.id"), nullable=True)
    idea_id: Mapped[Optional[str]] = mapped_column(ForeignKey("story_ideas.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    synopsis: Mapped[str] = mapped_column(Text, default="")
    script: Mapped[str] = mapped_column(Text, default="")
    content_format: Mapped[str] = mapped_column(String(32), default="long_form")
    language: Mapped[str] = mapped_column(String(16), default="en")
    age_band: Mapped[str] = mapped_column(String(32), default="3-6")
    target_duration_sec: Mapped[int] = mapped_column(Integer, default=390)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    revision_number: Mapped[int] = mapped_column(Integer, default=1)
    continuity_report: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    safety_report: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    story_quality_report: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    educational_report: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    parent_facing_info: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    cta_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    cost_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_actual: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    character_roster: Mapped[list[Any]] = mapped_column(JSON, default=list)
    metadata_draft: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    proposed_publish_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    series: Mapped[Series] = relationship(back_populates="episodes")
    channel: Mapped[Optional[Channel]] = relationship(back_populates="episodes")
    scenes: Mapped[list["Scene"]] = relationship(back_populates="episode")
    storyboards: Mapped[list["Storyboard"]] = relationship(back_populates="episode")
    renders: Mapped[list["RenderVersion"]] = relationship(back_populates="episode")
    jobs: Mapped[list["ProductionJob"]] = relationship(back_populates="episode")
    localized: Mapped[list["LocalizedEpisode"]] = relationship(back_populates="source_episode")


class Scene(Base, TimestampMixin):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"))
    index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    dialogue: Mapped[str] = mapped_column(Text, default="")
    characters: Mapped[list[Any]] = mapped_column(JSON, default=list)
    setting: Mapped[str] = mapped_column(Text, default="")
    action: Mapped[str] = mapped_column(Text, default="")
    duration_sec: Mapped[float] = mapped_column(Float, default=10.0)
    visual_prompt: Mapped[str] = mapped_column(Text, default="")
    audio_cue: Mapped[str] = mapped_column(Text, default="")
    asset_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")

    episode: Mapped[Episode] = relationship(back_populates="scenes")


class Storyboard(Base, TimestampMixin):
    __tablename__ = "storyboards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    panels: Mapped[list[Any]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    episode: Mapped[Episode] = relationship(back_populates="storyboards")


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    kind: Mapped[str] = mapped_column(String(64))
    path: Mapped[str] = mapped_column(Text)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    rights: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    provider: Mapped[str] = mapped_column(String(64), default="local")
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    episode_id: Mapped[Optional[str]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    character_id: Mapped[Optional[str]] = mapped_column(ForeignKey("characters.id"), nullable=True)


class RenderVersion(Base, TimestampMixin):
    __tablename__ = "render_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"))
    revision_number: Mapped[int] = mapped_column(Integer, default=1)
    media_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    thumbnail_version: Mapped[int] = mapped_column(Integer, default=1)
    metadata_version: Mapped[int] = mapped_column(Integer, default=1)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    qc_report: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    duration_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)

    episode: Mapped[Episode] = relationship(back_populates="renders")
    reviews: Mapped[list["OwnerReviewDecision"]] = relationship(back_populates="render")


class ProductionJob(Base, TimestampMixin):
    __tablename__ = "production_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    episode_id: Mapped[Optional[str]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    stage: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    input_refs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_refs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    provider_request_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logs: Mapped[list[Any]] = mapped_column(JSON, default=list)
    depends_on: Mapped[list[Any]] = mapped_column(JSON, default=list)
    timeout_sec: Mapped[int] = mapped_column(Integer, default=600)

    episode: Mapped[Optional[Episode]] = relationship(back_populates="jobs")


class PublishJob(Base, TimestampMixin):
    __tablename__ = "publish_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"))
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"))
    render_id: Mapped[str] = mapped_column(ForeignKey("render_versions.id"))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    youtube_video_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    privacy_status: Mapped[str] = mapped_column(String(32), default="private")
    made_for_kids: Mapped[bool] = mapped_column(Boolean, default=True)
    disclosure_set: Mapped[bool] = mapped_column(Boolean, default=False)
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_response: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class QualityReview(Base, TimestampMixin):
    __tablename__ = "quality_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"))
    render_id: Mapped[Optional[str]] = mapped_column(ForeignKey("render_versions.id"), nullable=True)
    checklist: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default="")


class OwnerReviewDecision(Base, TimestampMixin):
    __tablename__ = "owner_review_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"))
    render_id: Mapped[str] = mapped_column(ForeignKey("render_versions.id"))
    decision: Mapped[str] = mapped_column(String(32))
    scope: Mapped[str] = mapped_column(String(64), default="final_render")
    feedback: Mapped[str] = mapped_column(Text, default="")
    media_checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    metadata_version: Mapped[int] = mapped_column(Integer, default=1)
    valid: Mapped[bool] = mapped_column(Boolean, default=True)
    invalidated_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    render: Mapped[RenderVersion] = relationship(back_populates="reviews")


class LocalizedEpisode(Base, TimestampMixin):
    __tablename__ = "localized_episodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    source_episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"))
    channel_id: Mapped[Optional[str]] = mapped_column(ForeignKey("channels.id"), nullable=True)
    language: Mapped[str] = mapped_column(String(16))
    locale: Mapped[str] = mapped_column(String(32), default="")
    script: Mapped[str] = mapped_column(Text, default="")
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    asset_refs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    source_episode: Mapped[Episode] = relationship(back_populates="localized")


class ProviderConfig(Base, TimestampMixin):
    __tablename__ = "provider_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    category: Mapped[str] = mapped_column(String(64))
    provider_id: Mapped[str] = mapped_column(String(64))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    priority: Mapped[int] = mapped_column(Integer, default=100)


class BudgetLedger(Base, TimestampMixin):
    __tablename__ = "budget_ledger"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    channel_id: Mapped[Optional[str]] = mapped_column(ForeignKey("channels.id"), nullable=True)
    episode_id: Mapped[Optional[str]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    job_id: Mapped[Optional[str]] = mapped_column(ForeignKey("production_jobs.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    category: Mapped[str] = mapped_column(String(64), default="unknown")
    note: Mapped[str] = mapped_column(Text, default="")
    estimated: Mapped[bool] = mapped_column(Boolean, default=False)


class AnalyticsSnapshot(Base, TimestampMixin):
    __tablename__ = "analytics_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"))
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    recommendations: Mapped[list[Any]] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(String(64), default="mock")
    sample_size: Mapped[int] = mapped_column(Integer, default=0)


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    kind: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="")
    episode_id: Mapped[Optional[str]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    channel_id: Mapped[Optional[str]] = mapped_column(ForeignKey("channels.id"), nullable=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[str] = mapped_column(String(200), default="")
    dedupe_key: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, unique=True)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    action: Mapped[str] = mapped_column(String(128))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    actor: Mapped[str] = mapped_column(String(64), default="owner")


class ContentCatalogItem(Base, TimestampMixin):
    __tablename__ = "content_catalog"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    channel_id: Mapped[Optional[str]] = mapped_column(ForeignKey("channels.id"), nullable=True)
    episode_id: Mapped[Optional[str]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    format: Mapped[str] = mapped_column(String(32), default="long_form")
    language: Mapped[str] = mapped_column(String(16), default="en")
    youtube_video_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    tags: Mapped[list[Any]] = mapped_column(JSON, default=list)
