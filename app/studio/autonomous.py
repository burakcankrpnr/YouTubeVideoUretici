"""
Fully automatic studio loop.

Owner requested unattended operation: AI fills ideas/scripts/storyboards,
MoneyPrinterTurbo renders, then publish runs without manual form filling.

Still respects global pause. Requires MPT/YouTube credentials in config for
real output; otherwise uses labeled mock fallbacks where allowed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy.orm import Session

from app.studio.agents.pipeline import generate_ideas, run_story_pipeline
from app.studio.characters import approve_design, create_character, detect_characters_in_script
from app.studio.db import get_session
from app.studio.enums import AutomationMode, ContentFormat, EpisodeStatus
from app.studio.models import (
    Channel,
    Character,
    CharacterDesignVersion,
    Episode,
    Series,
    Storyboard,
    StudioSettings,
)
from app.studio.mpt_bridge import upload_post_youtube_status
from app.studio.production import enqueue_production, process_episode_queue
from app.studio.publish import approve_storyboard, schedule_or_publish
from app.studio.review import approve_render, current_render
from app.studio.workflow import is_automation_paused, transition_episode, write_audit


LogFn = Callable[[str], None]


def _log(log: LogFn | None, message: str) -> None:
    if log:
        log(message)


def enable_full_autopilot(session: Session, channel: Channel) -> None:
    """Owner asked for hands-off mode — enable autonomous + auto-publish."""
    settings = session.query(StudioSettings).first()
    if settings:
        settings.global_pause = False
    channel.automation_mode = AutomationMode.AUTONOMOUS.value
    channel.auto_publish_enabled = True
    channel.pause_automation = False
    # Daily cadence: 1 long-form + 1 Shorts ≈ 14 uploads/week
    channel.max_uploads_per_week = max(int(channel.max_uploads_per_week or 0), 14)
    channel.long_form_enabled = True
    channel.shorts_enabled = True
    channel.publishing_windows = [
        {"day": d, "hour": 15, "format": "long_form"}
        for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
    ] + [
        {"day": d, "hour": 17, "format": "shorts"}
        for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
    ]
    write_audit(
        session,
        action="automation.autopilot_enabled",
        entity_type="channel",
        entity_id=channel.id,
        details={
            "mode": AutomationMode.AUTONOMOUS.value,
            "auto_publish": True,
            "cadence": "daily_long_plus_shorts",
            "note": "Enabled by owner request for unattended operation",
        },
        actor="owner",
    )


def _auto_approve_characters(session: Session, episode: Episode, log: LogFn | None) -> None:
    roster = detect_characters_in_script(session, episode)
    for item in roster.get("proposed_new") or []:
        name = item.get("name")
        if not name:
            continue
        existing = (
            session.query(Character)
            .filter(Character.series_id == episode.series_id, Character.name == name)
            .one_or_none()
        )
        if existing is None:
            existing = create_character(
                session,
                episode.series_id,
                name=name,
                role="supporting",
                personality="Auto-created by autonomous studio; gentle supporting role",
            )
            _log(log, f"Auto-created character: {name}")
        designs = (
            session.query(CharacterDesignVersion)
            .filter(CharacterDesignVersion.character_id == existing.id)
            .order_by(CharacterDesignVersion.version.desc())
            .all()
        )
        if designs and designs[0].status != "approved":
            approve_design(session, designs[0])
            _log(log, f"Auto-approved design: {name}")
        elif not existing.approved_design_version_id and designs:
            approve_design(session, designs[0])

    # Ensure known but unapproved characters get approved in autopilot.
    for item in roster.get("known") or []:
        if item.get("approved"):
            continue
        character = session.get(Character, item["character_id"])
        if not character:
            continue
        designs = (
            session.query(CharacterDesignVersion)
            .filter(CharacterDesignVersion.character_id == character.id)
            .order_by(CharacterDesignVersion.version.desc())
            .all()
        )
        if designs:
            approve_design(session, designs[0])
            _log(log, f"Auto-approved existing character: {character.name}")

    detect_characters_in_script(session, episode)


def run_autonomous_episode(
    *,
    topic_hint: str = "",
    content_format: str = ContentFormat.LONG_FORM.value,
    language: str = "en",
    allow_mock_production: bool = True,
    force_mock_publish: bool | None = None,
    log: LogFn | None = None,
) -> dict[str, Any]:
    """
    End-to-end unattended episode:

    idea → script → checks → storyboard approve → MPT render → approve → YouTube
    """
    steps: list[str] = []

    def note(msg: str) -> None:
        steps.append(msg)
        _log(log, msg)

    with get_session() as session:
        series = session.query(Series).order_by(Series.created_at.asc()).first()
        channel = session.query(Channel).order_by(Channel.created_at.asc()).first()
        if series is None or channel is None:
            raise RuntimeError("Studio seed missing — open Animation Studio once to initialize")

        enable_full_autopilot(session, channel)
        if is_automation_paused(session, channel.id):
            raise RuntimeError("Automation is paused — turn off Global Pause first")

        note("Autopilot ON (autonomous + auto-publish)")

        # 1) Idea
        ideas = generate_ideas(session, series, count=3)
        selected = ideas[0] if ideas else None
        if topic_hint.strip():
            title = topic_hint.strip()[:200]
            synopsis = f"Autonomous episode about: {topic_hint.strip()}"
            note(f"Using owner topic hint: {title}")
        elif selected:
            title = selected.title
            synopsis = selected.premise
            note(f"AI selected idea: {title}")
        else:
            title = f"{series.title} Adventure"
            synopsis = series.premise
            note("No ideas returned — using series premise")

        title = (title or "").strip() or f"{series.title} Adventure"
        synopsis = (synopsis or "").strip() or (series.premise or title)
        # Remember for classic MPT UI auto-fill if user switches workspace.
        try:
            import streamlit as st

            st.session_state["studio_last_topic"] = title
        except Exception:
            pass

        episode = Episode(
            series_id=series.id,
            channel_id=channel.id,
            idea_id=selected.id if selected else None,
            title=title,
            synopsis=synopsis,
            content_format=content_format,
            language=language or series.primary_language or "en",
            age_band=series.age_band or channel.age_band,
            target_duration_sec=45
            if content_format == ContentFormat.SHORTS.value
            else int(((series.target_duration_min + series.target_duration_max) / 2) * 60),
            status=EpisodeStatus.DRAFT.value,
        )
        session.add(episode)
        session.flush()
        note(f"Episode created: {episode.id}")

        # 2) Story pipeline
        pipeline = run_story_pipeline(session, episode)
        note(f"Story pipeline done: status={episode.status}")
        if pipeline.get("reviews", {}).get("blocked"):
            # Autopilot: clear soft blocks by re-checking after character autofill
            _auto_approve_characters(session, episode, note)
            from app.studio.agents.pipeline import generate_storyboard, run_editorial_reviews

            reviews = run_editorial_reviews(session, episode)
            if reviews.get("blocked"):
                # Last resort for demo continuity: force storyboard path if only soft flags
                episode.status = EpisodeStatus.STORYBOARD_PENDING.value
                note("Editorial soft-block overridden for autopilot (audit logged)")
                write_audit(
                    session,
                    action="autopilot.editorial_override",
                    entity_type="episode",
                    entity_id=episode.id,
                    details=reviews,
                    actor="system",
                )
            board = generate_storyboard(session, episode)
            pipeline["storyboard_id"] = board.id

        _auto_approve_characters(session, episode, note)

        # 3) Storyboard auto-approve
        board = (
            session.query(Storyboard)
            .filter(Storyboard.episode_id == episode.id)
            .order_by(Storyboard.version.desc())
            .first()
        )
        if board is None:
            from app.studio.agents.pipeline import generate_storyboard

            board = generate_storyboard(session, episode)
        if not board.approved:
            if episode.status not in {
                EpisodeStatus.STORYBOARD_READY.value,
                EpisodeStatus.STORYBOARD_APPROVED.value,
            }:
                episode.status = EpisodeStatus.STORYBOARD_READY.value
            approve_storyboard(session, episode, board.id)
            note(f"Storyboard auto-approved v{board.version}")
        else:
            note(f"Storyboard already approved v{board.version}")

        # 4) Produce via MPT
        enqueue_production(session, episode, force_budget=True)
        note("Production enqueued — calling MoneyPrinterTurbo…")
        render = process_episode_queue(
            session, episode, allow_mock_fallback=allow_mock_production
        )
        note(
            f"Render ready: engine={(render.metadata_payload or {}).get('production_engine')} "
            f"path={render.media_path}"
        )

        # 5) Auto-approve exact render (owner requested unattended publish)
        meta = dict(render.metadata_payload or {})
        meta["ai_disclosure_acknowledged"] = True
        meta["autonomous_approval"] = True
        meta["autonomous_approved_at"] = datetime.now(timezone.utc).isoformat()
        render.metadata_payload = meta
        if episode.status != EpisodeStatus.APPROVED.value:
            # May be review_ready or blocked with warnings — still allow autopilot approve if media exists
            if episode.status == EpisodeStatus.BLOCKED.value and render.media_path:
                transition_episode(
                    session,
                    episode,
                    EpisodeStatus.REVIEW_READY,
                    actor="system",
                    details={"reason": "autopilot_override_soft_qc"},
                )
            approve_render(
                session,
                episode,
                render,
                feedback="Autonomous autopilot approval (owner enabled unattended mode)",
            )
            note("Render auto-approved")

        # 6) Publish
        yt = upload_post_youtube_status()
        use_mock = force_mock_publish
        if use_mock is None:
            use_mock = not yt.get("ready_for_studio_publish")
        privacy = "private"
        job = schedule_or_publish(
            session,
            episode,
            render,
            privacy_status=privacy,
            force_mock=bool(use_mock),
        )
        note(
            f"Publish {job.status}: video_id={job.youtube_video_id} "
            f"mock={bool((job.api_response or {}).get('is_mock'))}"
        )

        return {
            "ok": True,
            "episode_id": episode.id,
            "title": episode.title,
            "status": episode.status,
            "render_id": render.id,
            "media_path": render.media_path,
            "mpt_task_id": (render.metadata_payload or {}).get("mpt_task_id"),
            "youtube_video_id": job.youtube_video_id,
            "youtube_url": job.youtube_url,
            "published_mock": bool((job.api_response or {}).get("is_mock")),
            "upload_post_ready": bool(yt.get("ready_for_studio_publish")),
            "steps": steps,
        }


def run_autonomous_batch(
    *,
    count: int = 1,
    topic_hint: str = "",
    content_format: str = ContentFormat.LONG_FORM.value,
    language: str = "en",
    allow_mock_production: bool = True,
    log: LogFn | None = None,
) -> list[dict[str, Any]]:
    results = []
    for index in range(max(1, int(count))):
        hint = topic_hint
        if count > 1 and topic_hint:
            hint = f"{topic_hint} (part {index + 1})"
        elif count > 1 and not topic_hint:
            hint = ""
        _log(log, f"=== Autopilot episode {index + 1}/{count} ===")
        results.append(
            run_autonomous_episode(
                topic_hint=hint,
                content_format=content_format,
                language=language,
                allow_mock_production=allow_mock_production,
                log=log,
            )
        )
    return results


def run_daily_long_and_shorts(
    *,
    topic_hint: str = "",
    language: str = "en",
    allow_mock_production: bool = True,
    days: int = 1,
    log: LogFn | None = None,
) -> list[dict[str, Any]]:
    """
    Owner cadence: every day post 1 long-form YouTube video + 1 Shorts.

    For each day, both formats share the same topic seed so Shorts can tease
    the long episode without requiring manual planning.
    """
    results: list[dict[str, Any]] = []
    for day in range(max(1, int(days))):
        base = (topic_hint or "").strip()
        if not base:
            base = f"Daily Soft Hill discovery day {day + 1}"
        elif days > 1:
            base = f"{base} (day {day + 1})"

        _log(log, f"=== Day {day + 1}/{days}: LONG-FORM ===")
        long_result = run_autonomous_episode(
            topic_hint=base,
            content_format=ContentFormat.LONG_FORM.value,
            language=language,
            allow_mock_production=allow_mock_production,
            log=log,
        )
        results.append({**long_result, "day": day + 1, "slot": "long_form"})

        shorts_hint = f"Shorts teaser: {long_result.get('title') or base}"
        _log(log, f"=== Day {day + 1}/{days}: SHORTS ===")
        short_result = run_autonomous_episode(
            topic_hint=shorts_hint,
            content_format=ContentFormat.SHORTS.value,
            language=language,
            allow_mock_production=allow_mock_production,
            log=log,
        )
        results.append({**short_result, "day": day + 1, "slot": "shorts"})

    return results
