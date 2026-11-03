"""High-level studio operations used by the WebUI."""

from __future__ import annotations

from typing import Any

from app.studio.agents.pipeline import generate_ideas, run_story_pipeline
from app.studio.db import get_session, init_studio_db
from app.studio.enums import ContentFormat, EpisodeStatus
from app.studio.models import Channel, Episode, Series, StoryIdea
from app.studio.seed import ensure_demo_seed
from app.studio.workflow import write_audit


def bootstrap_studio() -> dict[str, str]:
    init_studio_db()
    return ensure_demo_seed()


def list_series() -> list[dict[str, Any]]:
    with get_session() as session:
        rows = session.query(Series).order_by(Series.created_at.desc()).all()
        return [
            {
                "id": s.id,
                "title": s.title,
                "premise": s.premise,
                "age_band": s.age_band,
                "approved": s.approved,
                "primary_language": s.primary_language,
                "duration": f"{s.target_duration_min}-{s.target_duration_max} min",
            }
            for s in rows
        ]


def list_channels() -> list[dict[str, Any]]:
    with get_session() as session:
        rows = session.query(Channel).order_by(Channel.created_at.desc()).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "language": c.language,
                "automation_mode": c.automation_mode,
                "auto_publish_enabled": c.auto_publish_enabled,
                "pause_automation": c.pause_automation,
                "oauth_connected": c.oauth_connected,
                "connection_health": c.connection_health,
                "age_band": c.age_band,
                "budget_per_episode": c.budget_per_episode,
                "budget_monthly": c.budget_monthly,
            }
            for c in rows
        ]


def list_episodes(series_id: str | None = None) -> list[dict[str, Any]]:
    with get_session() as session:
        q = session.query(Episode).order_by(Episode.updated_at.desc())
        if series_id:
            q = q.filter(Episode.series_id == series_id)
        rows = q.limit(100).all()
        return [
            {
                "id": e.id,
                "title": e.title,
                "status": e.status,
                "format": e.content_format,
                "language": e.language,
                "series_id": e.series_id,
                "channel_id": e.channel_id,
                "revision_number": e.revision_number,
                "cost_estimate": e.cost_estimate,
                "cost_actual": e.cost_actual,
            }
            for e in rows
        ]


def create_episode(
    *,
    series_id: str,
    title: str,
    synopsis: str = "",
    channel_id: str | None = None,
    content_format: str = ContentFormat.LONG_FORM.value,
    language: str = "en",
    age_band: str | None = None,
) -> str:
    with get_session() as session:
        series = session.get(Series, series_id)
        if series is None:
            raise ValueError("series not found")
        if not channel_id:
            channel = session.query(Channel).first()
            channel_id = channel.id if channel else None
        duration = 390 if content_format == ContentFormat.LONG_FORM.value else 45
        if content_format == ContentFormat.LONG_FORM.value:
            # Midpoint of 5–8 minutes default.
            duration = int(((series.target_duration_min + series.target_duration_max) / 2) * 60)
        episode = Episode(
            series_id=series_id,
            channel_id=channel_id,
            title=title.strip() or "Untitled episode",
            synopsis=synopsis,
            content_format=content_format,
            language=language,
            age_band=age_band or series.age_band,
            target_duration_sec=duration,
            status=EpisodeStatus.DRAFT.value,
        )
        session.add(episode)
        session.flush()
        write_audit(
            session,
            action="episode.created",
            entity_type="episode",
            entity_id=episode.id,
            details={"title": episode.title, "format": content_format},
        )
        return episode.id


def create_ideas_for_series(series_id: str) -> list[dict[str, Any]]:
    with get_session() as session:
        series = session.get(Series, series_id)
        if series is None:
            raise ValueError("series not found")
        ideas = generate_ideas(session, series)
        session.flush()
        return [{"id": i.id, "title": i.title, "premise": i.premise} for i in ideas]


def run_episode_story(episode_id: str) -> dict[str, Any]:
    with get_session() as session:
        episode = session.get(Episode, episode_id)
        if episode is None:
            raise ValueError("episode not found")
        return run_story_pipeline(session, episode)


def get_episode_detail(episode_id: str) -> dict[str, Any] | None:
    with get_session() as session:
        episode = session.get(Episode, episode_id)
        if episode is None:
            return None
        return {
            "id": episode.id,
            "title": episode.title,
            "synopsis": episode.synopsis,
            "script": episode.script,
            "status": episode.status,
            "format": episode.content_format,
            "language": episode.language,
            "age_band": episode.age_band,
            "revision_number": episode.revision_number,
            "continuity_report": episode.continuity_report,
            "safety_report": episode.safety_report,
            "story_quality_report": episode.story_quality_report,
            "educational_report": episode.educational_report,
            "parent_facing_info": episode.parent_facing_info,
            "character_roster": episode.character_roster,
            "cost_estimate": episode.cost_estimate,
            "cost_actual": episode.cost_actual,
            "cost_breakdown": episode.cost_breakdown,
            "metadata_draft": episode.metadata_draft,
            "channel_id": episode.channel_id,
            "series_id": episode.series_id,
            "scenes": [
                {
                    "id": s.id,
                    "index": s.index,
                    "title": s.title,
                    "dialogue": s.dialogue,
                    "duration_sec": s.duration_sec,
                }
                for s in sorted(episode.scenes, key=lambda x: x.index)
            ],
            "storyboards": [
                {
                    "id": b.id,
                    "version": b.version,
                    "approved": b.approved,
                    "status": b.status,
                    "panel_count": len(b.panels or []),
                    "checksum": b.checksum,
                }
                for b in episode.storyboards
            ],
            "renders": [
                {
                    "id": r.id,
                    "revision_number": r.revision_number,
                    "media_path": r.media_path,
                    "media_checksum": r.media_checksum,
                    "is_current": r.is_current,
                    "qc_report": r.qc_report,
                    "metadata_payload": r.metadata_payload,
                    "duration_sec": r.duration_sec,
                }
                for r in episode.renders
            ],
        }
