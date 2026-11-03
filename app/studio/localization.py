"""Localization adaptation workflow (not literal translation)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.studio.enums import JobStage
from app.studio.models import Episode, LocalizedEpisode
from app.studio.providers import get_provider
from app.studio.workflow import create_job, update_job_status, write_audit


def create_localized_episode(
    session: Session,
    source: Episode,
    *,
    language: str,
    locale: str = "",
    channel_id: str | None = None,
) -> LocalizedEpisode:
    provider = get_provider("text")
    job = create_job(
        session,
        stage=JobStage.LOCALIZE,
        episode_id=source.id,
        idempotency_key=f"localize:{source.id}:{language}:r{source.revision_number}",
        provider=provider.name,
    )
    update_job_status(session, job, "running")
    result = provider.generate(
        source.script or source.synopsis,
        kind="localize",
        language=language,
    )
    localized = LocalizedEpisode(
        source_episode_id=source.id,
        channel_id=channel_id or source.channel_id,
        language=language,
        locale=locale or language,
        script=result.get("text") or "",
        metadata_payload={
            "title": f"{source.title} [{language}]",
            "description": source.synopsis,
            "adaptation_notes": "Preserve character names, tone, and canon; adapt idioms.",
            "provider": provider.name,
            "is_mock": provider.is_mock,
        },
        status="draft",
        asset_refs={},
    )
    session.add(localized)
    session.flush()
    update_job_status(
        session,
        job,
        "succeeded",
        output_refs={"localized_episode_id": localized.id},
        cost=result.get("cost"),
    )
    write_audit(
        session,
        action="localization.created",
        entity_type="localized_episode",
        entity_id=localized.id,
        details={"language": language, "source_episode_id": source.id},
        actor="owner",
    )
    return localized
