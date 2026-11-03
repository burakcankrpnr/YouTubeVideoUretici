"""Durable episode/job state machine with audit logging."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.studio.enums import (
    EpisodeStatus,
    JobStage,
    JobStatus,
    can_transition,
)
from app.studio.models import AuditLog, Episode, Notification, ProductionJob


class WorkflowError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def write_audit(
    session: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    details: dict[str, Any] | None = None,
    actor: str = "owner",
) -> AuditLog:
    entry = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        actor=actor,
    )
    session.add(entry)
    return entry


def transition_episode(
    session: Session,
    episode: Episode,
    target: EpisodeStatus | str,
    *,
    actor: str = "system",
    details: dict[str, Any] | None = None,
) -> Episode:
    target_status = EpisodeStatus(target)
    current = EpisodeStatus(episode.status)
    if current == target_status:
        return episode
    if not can_transition(current, target_status):
        raise WorkflowError(
            f"illegal transition {current.value} -> {target_status.value} for episode {episode.id}"
        )
    episode.status = target_status.value
    episode.updated_at = _now()
    write_audit(
        session,
        action="episode.transition",
        entity_type="episode",
        entity_id=episode.id,
        details={"from": current.value, "to": target_status.value, **(details or {})},
        actor=actor,
    )
    return episode


def create_job(
    session: Session,
    *,
    stage: JobStage | str,
    episode_id: str | None = None,
    idempotency_key: str | None = None,
    provider: str = "mock",
    input_refs: dict[str, Any] | None = None,
    depends_on: list[str] | None = None,
    max_attempts: int = 3,
) -> ProductionJob:
    key = idempotency_key or f"{stage}:{episode_id or 'global'}:{uuid4()}"
    existing = (
        session.query(ProductionJob).filter(ProductionJob.idempotency_key == key).one_or_none()
    )
    if existing is not None:
        return existing
    job = ProductionJob(
        episode_id=episode_id,
        stage=JobStage(stage).value,
        status=JobStatus.QUEUED.value,
        idempotency_key=key,
        provider=provider,
        input_refs=input_refs or {},
        depends_on=depends_on or [],
        max_attempts=max_attempts,
        logs=[{"at": _now().isoformat(), "message": "queued"}],
    )
    session.add(job)
    write_audit(
        session,
        action="job.created",
        entity_type="production_job",
        entity_id=job.id,
        details={"stage": job.stage, "idempotency_key": key},
        actor="system",
    )
    return job


def update_job_status(
    session: Session,
    job: ProductionJob,
    status: JobStatus | str,
    *,
    error: str | None = None,
    output_refs: dict[str, Any] | None = None,
    cost: float | None = None,
    log_message: str | None = None,
) -> ProductionJob:
    job.status = JobStatus(status).value
    job.updated_at = _now()
    if error is not None:
        job.error_detail = error
    if output_refs is not None:
        job.output_refs = {**(job.output_refs or {}), **output_refs}
    if cost is not None:
        job.cost = cost
    logs = list(job.logs or [])
    logs.append(
        {
            "at": _now().isoformat(),
            "message": log_message or f"status={job.status}",
            "status": job.status,
        }
    )
    job.logs = logs
    write_audit(
        session,
        action="job.status",
        entity_type="production_job",
        entity_id=job.id,
        details={"status": job.status, "error": error},
        actor="system",
    )
    return job


def notify_owner(
    session: Session,
    *,
    kind: str,
    title: str,
    body: str,
    episode_id: str | None = None,
    channel_id: str | None = None,
    action_url: str = "",
    dedupe_key: str | None = None,
) -> Notification | None:
    if dedupe_key:
        existing = (
            session.query(Notification)
            .filter(Notification.dedupe_key == dedupe_key)
            .one_or_none()
        )
        if existing is not None:
            return existing
    note = Notification(
        kind=kind,
        title=title,
        body=body,
        episode_id=episode_id,
        channel_id=channel_id,
        action_url=action_url,
        dedupe_key=dedupe_key,
    )
    session.add(note)
    return note


def is_automation_paused(session: Session, channel_id: Optional[str] = None) -> bool:
    from app.studio.models import Channel, StudioSettings

    settings = session.query(StudioSettings).first()
    if settings and settings.global_pause:
        return True
    if channel_id:
        channel = session.get(Channel, channel_id)
        if channel and channel.pause_automation:
            return True
    return False
