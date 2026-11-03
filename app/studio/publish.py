"""Publication gate and YouTube publish jobs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.studio.continuity import update_memory_after_publish
from app.studio.enums import EpisodeStatus
from app.studio.models import Channel, ContentCatalogItem, Episode, PublishJob, RenderVersion
from app.studio.providers import get_provider
from app.studio.review import get_valid_approval
from app.studio.workflow import is_automation_paused, transition_episode, write_audit


class PublishError(Exception):
    pass


def publication_gate_check(
    session: Session, episode: Episode, render: RenderVersion
) -> dict[str, Any]:
    blockers: list[str] = []
    approval = get_valid_approval(session, render)
    if approval is None:
        blockers.append("Owner approval required for this exact render version")
    if not render.media_checksum:
        blockers.append("Render checksum missing")
    if approval and approval.media_checksum != render.media_checksum:
        blockers.append("Approved checksum does not match current render")
    if not episode.channel_id:
        blockers.append("No destination channel selected")
    else:
        channel = session.get(Channel, episode.channel_id)
        if channel is None:
            blockers.append("Channel not found")
        else:
            if is_automation_paused(session, channel.id):
                blockers.append("Automation paused globally or for this channel")
            if channel.audience_designation == "made_for_kids" and not True:
                blockers.append("Made for Kids designation incomplete")
            # Disclosure: if API cannot set it, block autonomous; assisted path warns.
            if not (render.metadata_payload or {}).get("ai_disclosure_acknowledged"):
                blockers.append(
                    "AI/synthetic disclosure must be acknowledged before publish "
                    "(set in metadata if API field unavailable — complete in YouTube Studio)"
                )
    qc = render.qc_report or {}
    if qc and not qc.get("passed", False):
        blockers.append("QC checks have not passed")
    safety = episode.safety_report or {}
    if safety and not safety.get("passed", True):
        blockers.append("Safety review has not passed")

    return {"allowed": not blockers, "blockers": blockers, "approval_id": approval.id if approval else None}


def schedule_or_publish(
    session: Session,
    episode: Episode,
    render: RenderVersion,
    *,
    scheduled_at: datetime | None = None,
    privacy_status: str = "private",
    force_mock: bool = False,
) -> PublishJob:
    gate = publication_gate_check(session, episode, render)
    if not gate["allowed"]:
        raise PublishError("; ".join(gate["blockers"]))

    channel = session.get(Channel, episode.channel_id)
    assert channel is not None

    key = f"publish:{episode.id}:{render.id}:{render.media_checksum}"
    existing = session.query(PublishJob).filter(PublishJob.idempotency_key == key).one_or_none()
    if existing and existing.status in {"published", "scheduled", "publishing"}:
        return existing

    if scheduled_at:
        transition_episode(session, episode, EpisodeStatus.SCHEDULED, actor="owner")
    else:
        transition_episode(session, episode, EpisodeStatus.PUBLISHING, actor="owner")

    job = existing or PublishJob(
        episode_id=episode.id,
        channel_id=channel.id,
        render_id=render.id,
        status="publishing",
        idempotency_key=key,
        scheduled_at=scheduled_at,
        privacy_status=privacy_status,
        made_for_kids=channel.audience_designation == "made_for_kids",
        disclosure_set=bool((render.metadata_payload or {}).get("ai_disclosure_acknowledged")),
    )
    if existing is None:
        session.add(job)
        session.flush()

    # Prefer Upload-Post YouTube (MPT settings). Mock only when forced or nothing real is ready.
    provider = get_provider("youtube", prefer_real=not force_mock)
    if force_mock:
        from app.studio.providers.mock import MockYouTubeProvider

        provider = MockYouTubeProvider()

    media_path = render.media_path or ""
    if not getattr(provider, "is_mock", False) and not str(media_path).lower().endswith(
        (".mp4", ".webm", ".mov", ".mkv")
    ):
        raise PublishError(
            "Real YouTube publish requires a real video file from MoneyPrinterTurbo. "
            "Current render is not an MP4/WebM."
        )

    try:
        result = provider.upload(
            title=(render.metadata_payload or {}).get("title") or episode.title,
            description=(render.metadata_payload or {}).get("description") or episode.synopsis,
            media_path=media_path,
            privacy_status=privacy_status,
            made_for_kids=job.made_for_kids,
            scheduled_at=scheduled_at.isoformat() if scheduled_at else None,
            tags=(render.metadata_payload or {}).get("tags") or [],
        )
    except Exception as exc:
        job.status = "failed"
        job.error_detail = str(exc)
        if force_mock:
            from app.studio.providers.mock import MockYouTubeProvider

            result = MockYouTubeProvider().upload()
            job.error_detail = f"forced_mock_after_error:{exc}"
        else:
            transition_episode(session, episode, EpisodeStatus.FAILED, actor="system")
            write_audit(
                session,
                action="publish.failed",
                entity_type="publish_job",
                entity_id=job.id,
                details={"error": str(exc), "provider": getattr(provider, "name", "?")},
            )
            raise PublishError(str(exc)) from exc

    job.youtube_video_id = result.get("youtube_video_id")
    job.youtube_url = result.get("youtube_url")
    job.api_response = result
    job.status = "scheduled" if scheduled_at else "published"
    if job.status == "published":
        transition_episode(session, episode, EpisodeStatus.PUBLISHED, actor="system")
        update_memory_after_publish(session, episode)
        session.add(
            ContentCatalogItem(
                channel_id=channel.id,
                episode_id=episode.id,
                title=episode.title,
                format=episode.content_format,
                language=episode.language,
                youtube_video_id=job.youtube_video_id,
                status="published",
            )
        )
    write_audit(
        session,
        action="publish.completed",
        entity_type="publish_job",
        entity_id=job.id,
        details={
            "youtube_video_id": job.youtube_video_id,
            "mock": result.get("is_mock", False),
            "status": job.status,
        },
        actor="owner",
    )
    return job


def approve_storyboard(session: Session, episode: Episode, storyboard_id: str) -> None:
    from app.studio.models import Storyboard

    board = session.get(Storyboard, storyboard_id)
    if board is None or board.episode_id != episode.id:
        raise PublishError("storyboard not found")
    board.approved = True
    board.approved_at = datetime.now(timezone.utc)
    board.status = "approved"
    transition_episode(session, episode, EpisodeStatus.STORYBOARD_APPROVED, actor="owner")
    write_audit(
        session,
        action="storyboard.approved",
        entity_type="storyboard",
        entity_id=board.id,
        details={"checksum": board.checksum},
        actor="owner",
    )
