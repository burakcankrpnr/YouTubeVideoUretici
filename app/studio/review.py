"""Owner review decisions bound to exact render versions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.studio.enums import EpisodeStatus
from app.studio.models import Episode, OwnerReviewDecision, RenderVersion
from app.studio.workflow import notify_owner, transition_episode, write_audit


class ReviewError(Exception):
    pass


def current_render(session: Session, episode_id: str) -> RenderVersion | None:
    return (
        session.query(RenderVersion)
        .filter(RenderVersion.episode_id == episode_id, RenderVersion.is_current.is_(True))
        .order_by(RenderVersion.revision_number.desc())
        .first()
    )


def mark_review_ready(session: Session, episode: Episode, render: RenderVersion) -> None:
    transition_episode(session, episode, EpisodeStatus.REVIEW_READY, actor="system")
    notify_owner(
        session,
        kind="review_ready",
        title="Your new video is ready to review",
        body=f"“{episode.title}” is ready. Watch and approve when you are ready.",
        episode_id=episode.id,
        channel_id=episode.channel_id,
        action_url=f"review:{episode.id}",
        dedupe_key=f"review_ready:{render.id}",
    )


def approve_render(
    session: Session,
    episode: Episode,
    render: RenderVersion,
    *,
    feedback: str = "",
) -> OwnerReviewDecision:
    if EpisodeStatus(episode.status) not in {
        EpisodeStatus.REVIEW_READY,
        EpisodeStatus.APPROVED,
    }:
        raise ReviewError(f"episode status {episode.status} cannot be approved")
    if not render.media_checksum:
        raise ReviewError("render missing checksum")
    if not render.is_current:
        raise ReviewError("can only approve the current render version")

    decision = OwnerReviewDecision(
        episode_id=episode.id,
        render_id=render.id,
        decision="approved",
        scope="final_render",
        feedback=feedback,
        media_checksum=render.media_checksum,
        metadata_version=render.metadata_version,
        valid=True,
    )
    session.add(decision)
    transition_episode(session, episode, EpisodeStatus.APPROVED, actor="owner")
    write_audit(
        session,
        action="review.approved",
        entity_type="render",
        entity_id=render.id,
        details={"checksum": render.media_checksum, "revision": render.revision_number},
        actor="owner",
    )
    return decision


def request_revision(
    session: Session,
    episode: Episode,
    render: RenderVersion,
    feedback: str,
) -> OwnerReviewDecision:
    if not feedback.strip():
        raise ReviewError("revision feedback is required")
    decision = OwnerReviewDecision(
        episode_id=episode.id,
        render_id=render.id,
        decision="revision_requested",
        scope="final_render",
        feedback=feedback,
        media_checksum=render.media_checksum,
        metadata_version=render.metadata_version,
        valid=False,
    )
    session.add(decision)
    # Invalidate any prior approvals for this render.
    for prior in (
        session.query(OwnerReviewDecision)
        .filter(
            OwnerReviewDecision.render_id == render.id,
            OwnerReviewDecision.decision == "approved",
            OwnerReviewDecision.valid.is_(True),
        )
        .all()
    ):
        prior.valid = False
        prior.invalidated_reason = "revision_requested"
    transition_episode(session, episode, EpisodeStatus.REVISION_REQUESTED, actor="owner")
    write_audit(
        session,
        action="review.revision_requested",
        entity_type="render",
        entity_id=render.id,
        details={"feedback": feedback[:500]},
        actor="owner",
    )
    return decision


def reject_render(
    session: Session, episode: Episode, render: RenderVersion, reason: str = ""
) -> OwnerReviewDecision:
    decision = OwnerReviewDecision(
        episode_id=episode.id,
        render_id=render.id,
        decision="rejected",
        scope="final_render",
        feedback=reason,
        media_checksum=render.media_checksum,
        metadata_version=render.metadata_version,
        valid=False,
    )
    session.add(decision)
    transition_episode(session, episode, EpisodeStatus.REJECTED, actor="owner")
    write_audit(
        session,
        action="review.rejected",
        entity_type="render",
        entity_id=render.id,
        details={"reason": reason},
        actor="owner",
    )
    return decision


def invalidate_approval_if_changed(
    session: Session, render: RenderVersion, *, reason: str
) -> None:
    priors = (
        session.query(OwnerReviewDecision)
        .filter(
            OwnerReviewDecision.render_id == render.id,
            OwnerReviewDecision.decision == "approved",
            OwnerReviewDecision.valid.is_(True),
        )
        .all()
    )
    for prior in priors:
        if prior.media_checksum != render.media_checksum or prior.metadata_version != render.metadata_version:
            prior.valid = False
            prior.invalidated_reason = reason
            write_audit(
                session,
                action="review.approval_invalidated",
                entity_type="owner_review",
                entity_id=prior.id,
                details={"reason": reason},
                actor="system",
            )


def get_valid_approval(session: Session, render: RenderVersion) -> OwnerReviewDecision | None:
    return (
        session.query(OwnerReviewDecision)
        .filter(
            OwnerReviewDecision.render_id == render.id,
            OwnerReviewDecision.decision == "approved",
            OwnerReviewDecision.valid.is_(True),
            OwnerReviewDecision.media_checksum == render.media_checksum,
            OwnerReviewDecision.metadata_version == render.metadata_version,
        )
        .order_by(OwnerReviewDecision.created_at.desc())
        .first()
    )


def plan_revision(feedback: str, episode: Episode) -> dict[str, Any]:
    text = feedback.lower()
    scopes = []
    if any(w in text for w in ("voice", "dialogue", "speak", "audio")):
        scopes.append("voice")
    if any(w in text for w in ("scene", "shot", "visual", "face", "character look")):
        scopes.append("visual")
    if any(w in text for w in ("music", "bgm", "sound")):
        scopes.append("audio")
    if any(w in text for w in ("title", "thumbnail", "description", "metadata")):
        scopes.append("metadata")
    if any(w in text for w in ("script", "story", "joke")):
        scopes.append("script")
    if not scopes:
        scopes = ["visual"]
    return {
        "feedback": feedback,
        "scopes": scopes,
        "reuse_unaffected": True,
        "episode_id": episode.id,
        "restatement": f"Understood: adjust {', '.join(scopes)} based on your notes.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
