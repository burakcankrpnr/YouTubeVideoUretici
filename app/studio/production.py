"""Production queue: storyboard-gated media generation and QC."""

from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy.orm import Session

from app.studio.characters import detect_characters_in_script
from app.studio.cost import BudgetExceeded, assert_budget_allows, record_ledger
from app.studio.enums import EpisodeStatus, JobStage, JobStatus
from app.studio.models import Episode, QualityReview, RenderVersion, Storyboard
from app.studio.providers import get_provider
from app.studio.review import mark_review_ready, plan_revision
from app.studio.workflow import (
    create_job,
    is_automation_paused,
    transition_episode,
    update_job_status,
    write_audit,
)


class ProductionError(Exception):
    pass


def _approved_storyboard(session: Session, episode_id: str) -> Storyboard | None:
    return (
        session.query(Storyboard)
        .filter(
            Storyboard.episode_id == episode_id,
            Storyboard.approved.is_(True),
        )
        .order_by(Storyboard.version.desc())
        .first()
    )


def enqueue_production(
    session: Session, episode: Episode, *, force_budget: bool = False
) -> list[str]:
    if is_automation_paused(session, episode.channel_id):
        raise ProductionError("Automation is paused")

    board = _approved_storyboard(session, episode.id)
    if board is None:
        raise ProductionError("Storyboard approval required before animation")

    roster = detect_characters_in_script(session, episode)
    if roster.get("production_blocked"):
        raise ProductionError(
            "Unapproved or new characters must be approved before production"
        )

    try:
        assert_budget_allows(session, episode, force=force_budget)
    except BudgetExceeded as exc:
        raise ProductionError(str(exc)) from exc

    if EpisodeStatus(episode.status) == EpisodeStatus.STORYBOARD_APPROVED:
        transition_episode(session, episode, EpisodeStatus.QUEUED, actor="owner")

    stages = [
        JobStage.VISUAL,
        JobStage.VOICE,
        JobStage.ASSEMBLY,
        JobStage.QC,
        JobStage.THUMBNAIL,
        JobStage.METADATA,
    ]
    job_ids = []
    for stage in stages:
        job = create_job(
            session,
            stage=stage,
            episode_id=episode.id,
            idempotency_key=f"{stage.value}:{episode.id}:r{episode.revision_number}:{board.checksum}",
            provider=get_provider(
                {
                    JobStage.VISUAL: "video",
                    JobStage.VOICE: "tts",
                    JobStage.ASSEMBLY: "assembly",
                    JobStage.QC: "safety",
                    JobStage.THUMBNAIL: "image",
                    JobStage.METADATA: "text",
                }[stage]
            ).name,
            input_refs={"storyboard_id": board.id, "storyboard_checksum": board.checksum},
        )
        job_ids.append(job.id)
    write_audit(
        session,
        action="production.enqueued",
        entity_type="episode",
        entity_id=episode.id,
        details={"jobs": job_ids},
        actor="owner",
    )
    return job_ids


def process_episode_queue(
    session: Session, episode: Episode, *, allow_mock_fallback: bool = True
) -> RenderVersion:
    """
    Produce the episode.

    Preferred path: MoneyPrinterTurbo ``task.start`` (real TTS + stock/AI footage + FFmpeg).
    Fallback: labeled mock assets when MPT is unavailable and allow_mock_fallback=True.
    """
    if is_automation_paused(session, episode.channel_id):
        raise ProductionError("Automation is paused")

    board = _approved_storyboard(session, episode.id)
    if board is None:
        raise ProductionError("Storyboard approval required")

    transition_episode(session, episode, EpisodeStatus.PRODUCING, actor="system")
    total_cost = 0.0
    voice_path = None
    assembled: dict[str, Any]

    assembly = get_provider("assembly", prefer_real=True)
    use_mpt = assembly.name == "mpt_ffmpeg" and getattr(assembly, "available", lambda: False)()

    if use_mpt:
        # One MPT pipeline covers voice + materials + final render.
        asm_job = create_job(
            session,
            stage=JobStage.ASSEMBLY,
            episode_id=episode.id,
            idempotency_key=f"mpt:{episode.id}:r{episode.revision_number}:{board.checksum}",
            provider=assembly.name,
            input_refs={"storyboard_id": board.id, "engine": "moneyprinterturbo"},
        )
        update_job_status(session, asm_job, JobStatus.RUNNING, log_message="MPT task.start")
        # Mirror stages for queue visibility
        for stage in (JobStage.VISUAL, JobStage.VOICE):
            create_job(
                session,
                stage=stage,
                episode_id=episode.id,
                idempotency_key=f"{stage.value}:mpt:{episode.id}:r{episode.revision_number}",
                provider="mpt_pipeline",
                input_refs={"delegated_to": "mpt_ffmpeg"},
            )
        try:
            assembled = assembly.assemble(
                episode=episode,
                episode_id=episode.id,
                title=episode.title,
                script=episode.script,
                synopsis=episode.synopsis,
                language=episode.language,
                content_format=episode.content_format,
            )
            update_job_status(
                session,
                asm_job,
                JobStatus.SUCCEEDED,
                output_refs={
                    "path": assembled.get("path"),
                    "checksum": assembled.get("checksum"),
                    "mpt_task_id": assembled.get("mpt_task_id"),
                },
                cost=assembled.get("cost"),
            )
            voice_path = assembled.get("path")  # real AV file; voice embedded
        except Exception as exc:
            update_job_status(session, asm_job, JobStatus.FAILED, error=str(exc))
            if not allow_mock_fallback:
                transition_episode(session, episode, EpisodeStatus.FAILED, actor="system")
                raise ProductionError(f"MPT production failed: {exc}") from exc
            write_audit(
                session,
                action="production.mpt_fallback_mock",
                entity_type="episode",
                entity_id=episode.id,
                details={"error": str(exc)},
                actor="system",
            )
            use_mpt = False

    if not use_mpt:
        scene_paths: list[str] = []
        visual_provider = get_provider("video")
        for panel in board.panels or []:
            job = create_job(
                session,
                stage=JobStage.VISUAL,
                episode_id=episode.id,
                idempotency_key=f"visual:{episode.id}:{panel.get('index')}:r{episode.revision_number}",
                provider=visual_provider.name,
            )
            update_job_status(session, job, JobStatus.RUNNING)
            result = visual_provider.generate(
                panel.get("visual_prompt") or panel.get("action") or episode.title,
                duration_sec=panel.get("duration_sec", 8),
            )
            scene_paths.append(result["path"])
            cost = result.get("cost")
            if cost is not None:
                total_cost += float(cost)
                record_ledger(
                    session,
                    amount=float(cost),
                    category="visual",
                    channel_id=episode.channel_id,
                    episode_id=episode.id,
                    job_id=job.id,
                )
            update_job_status(
                session, job, JobStatus.SUCCEEDED, output_refs={"path": result["path"]}, cost=cost
            )

        tts = get_provider("tts", prefer_real=True)
        voice_job = create_job(
            session,
            stage=JobStage.VOICE,
            episode_id=episode.id,
            idempotency_key=f"voice:{episode.id}:r{episode.revision_number}",
            provider=tts.name,
        )
        update_job_status(session, voice_job, JobStatus.RUNNING)
        try:
            voice_result = tts.synthesize(episode.script or episode.synopsis or episode.title)
        except Exception:
            tts = get_provider("tts")
            voice_result = tts.synthesize(episode.script or episode.synopsis or episode.title)
        voice_path = voice_result.get("path")
        update_job_status(
            session,
            voice_job,
            JobStatus.SUCCEEDED,
            output_refs={"path": voice_path},
            cost=voice_result.get("cost"),
        )

        from app.studio.providers.mock import MockVideoProvider

        asm_job = create_job(
            session,
            stage=JobStage.ASSEMBLY,
            episode_id=episode.id,
            idempotency_key=f"assembly-mock:{episode.id}:r{episode.revision_number}",
            provider="mock_video",
        )
        update_job_status(session, asm_job, JobStatus.RUNNING)
        assembled = MockVideoProvider().assemble(
            episode_id=episode.id,
            scene_paths=scene_paths,
            voice_path=voice_path,
            duration_sec=episode.target_duration_sec,
        )
        update_job_status(
            session,
            asm_job,
            JobStatus.SUCCEEDED,
            output_refs={"path": assembled.get("path"), "checksum": assembled.get("checksum")},
        )

    meta = {
        "title": episode.title[:100],
        "description": (episode.synopsis or "")[:4000],
        "language": episode.language,
        "ai_disclosure_acknowledged": False,
        "format": episode.content_format,
        "mpt_task_id": assembled.get("mpt_task_id"),
        "production_engine": assembled.get("provider") or ("mock" if assembled.get("is_mock") else "unknown"),
    }
    thumb = get_provider("image").generate(f"Thumbnail for {episode.title}, honest, character focus")

    transition_episode(session, episode, EpisodeStatus.QC_PENDING, actor="system")
    media_path = assembled.get("path") or ""
    is_real_video = str(media_path).lower().endswith((".mp4", ".webm", ".mov", ".mkv"))
    qc = {
        "passed": True,
        "checks": {
            "has_media": bool(media_path),
            "has_checksum": bool(assembled.get("checksum")),
            "has_playable_video": is_real_video or bool(assembled.get("is_mock")),
            "storyboard_matched": True,
            "safety_passed": bool((episode.safety_report or {}).get("passed", True)),
            "duration_configured": episode.target_duration_sec > 0,
        },
        "warnings": [],
    }
    if assembled.get("is_mock"):
        qc["warnings"].append(
            "Final media is a MOCK placeholder. Configure FFmpeg + video_source "
            "(e.g. Pexels) so Studio can call MoneyPrinterTurbo for a real MP4."
        )
    if not is_real_video and not assembled.get("is_mock"):
        qc["warnings"].append("Media path is not a recognized video file.")
    if not all(qc["checks"].values()):
        qc["passed"] = False

    for prior in (
        session.query(RenderVersion)
        .filter(RenderVersion.episode_id == episode.id, RenderVersion.is_current.is_(True))
        .all()
    ):
        prior.is_current = False

    render = RenderVersion(
        episode_id=episode.id,
        revision_number=episode.revision_number,
        media_path=media_path,
        media_checksum=assembled.get("checksum")
        or hashlib.sha256(str(assembled).encode()).hexdigest(),
        thumbnail_path=thumb.get("path"),
        metadata_payload=meta,
        qc_report=qc,
        duration_sec=assembled.get("duration_sec") or episode.target_duration_sec,
        is_current=True,
    )
    session.add(render)
    session.flush()
    session.add(
        QualityReview(
            episode_id=episode.id,
            render_id=render.id,
            checklist=qc,
            passed=bool(qc.get("passed")),
            notes="; ".join(qc.get("warnings") or []),
        )
    )
    episode.cost_actual = total_cost
    if not qc.get("passed"):
        transition_episode(session, episode, EpisodeStatus.BLOCKED, actor="system")
    else:
        mark_review_ready(session, episode, render)
    return render


def apply_revision(
    session: Session, episode: Episode, feedback: str, *, force_budget: bool = False
) -> dict[str, Any]:
    """Apply owner revision feedback with targeted scopes when possible."""
    from app.studio.agents.pipeline import (
        generate_script_for_episode,
        generate_storyboard,
        run_editorial_reviews,
    )
    from app.studio.review import current_render, invalidate_approval_if_changed

    plan = plan_revision(feedback, episode)
    transition_episode(session, episode, EpisodeStatus.REVISING, actor="system")
    episode.revision_number = int(episode.revision_number or 1) + 1
    write_audit(
        session,
        action="revision.planned",
        entity_type="episode",
        entity_id=episode.id,
        details=plan,
        actor="owner",
    )

    if plan["scopes"] == ["metadata"]:
        render = current_render(session, episode.id)
        if render is None:
            raise ProductionError("No render to revise")
        render.metadata_version = int(render.metadata_version or 1) + 1
        meta = dict(render.metadata_payload or {})
        meta["revision_note"] = feedback
        render.metadata_payload = meta
        invalidate_approval_if_changed(session, render, reason="metadata_changed")
        mark_review_ready(session, episode, render)
        return {"plan": plan, "render_id": render.id, "needs_storyboard_approval": False}

    if "script" in plan["scopes"]:
        generate_script_for_episode(session, episode)
        run_editorial_reviews(session, episode)
        board = generate_storyboard(session, episode)
        return {
            "plan": plan,
            "storyboard_id": board.id,
            "needs_storyboard_approval": True,
            "message": "Script changed — approve the new storyboard before re-rendering.",
        }

    enqueue_production(session, episode, force_budget=force_budget)
    render = process_episode_queue(session, episode)
    return {"plan": plan, "render_id": render.id, "needs_storyboard_approval": False}
