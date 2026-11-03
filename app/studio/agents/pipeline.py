"""Story/planning/script/safety/storyboard agent pipeline."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from sqlalchemy.orm import Session

from app.studio.characters import detect_characters_in_script
from app.studio.continuity import check_continuity, get_current_bible
from app.studio.enums import EpisodeStatus, JobStage
from app.studio.models import Episode, Scene, Series, Storyboard, StoryIdea
from app.studio.providers import get_provider
from app.studio.workflow import create_job, transition_episode, update_job_status, write_audit


def generate_ideas(session: Session, series: Series, count: int = 3) -> list[StoryIdea]:
    provider = get_provider("text")
    bible = get_current_bible(session, series.id)
    prompt = (
        f"Series: {series.title}\nPremise: {series.premise}\n"
        f"Age band: {series.age_band}\nThemes: {series.themes}\n"
        f"Bible: {json.dumps((bible.content if bible else {}), ensure_ascii=False)[:1500]}"
    )
    job = create_job(
        session,
        stage=JobStage.STORY,
        episode_id=None,
        idempotency_key=f"ideas:{series.id}:{hashlib.sha256(prompt.encode()).hexdigest()[:10]}",
        provider=provider.name,
        input_refs={"series_id": series.id},
    )
    update_job_status(session, job, "running", log_message="generating ideas")
    result = provider.generate(prompt, kind="ideas")
    ideas_data = result.get("ideas") or []
    created: list[StoryIdea] = []
    for item in ideas_data[:count]:
        idea = StoryIdea(
            series_id=series.id,
            title=item.get("title") or "Untitled idea",
            premise=item.get("premise") or "",
            educational_hooks=series.educational_domains or [],
            score_notes=f"provider={provider.name}; mock={provider.is_mock}",
        )
        session.add(idea)
        created.append(idea)
    update_job_status(
        session,
        job,
        "succeeded",
        output_refs={"idea_count": len(created)},
        cost=result.get("cost"),
    )
    return created


def generate_script_for_episode(session: Session, episode: Episode) -> Episode:
    series = session.get(Series, episode.series_id)
    provider = get_provider("text", prefer_real=True)
    # Prefer real LLM when available; fall back to mock on failure.
    try:
        result = provider.generate(
            episode.synopsis or episode.title,
            kind="script",
            title=episode.title,
            language=episode.language,
            subject=episode.synopsis or episode.title,
        )
    except Exception:
        provider = get_provider("text")
        result = provider.generate(
            episode.synopsis or episode.title,
            kind="script",
            title=episode.title,
            language=episode.language,
        )

    job = create_job(
        session,
        stage=JobStage.SCRIPT,
        episode_id=episode.id,
        idempotency_key=f"script:{episode.id}:r{episode.revision_number}",
        provider=provider.name,
    )
    update_job_status(session, job, "running")
    transition_episode(session, episode, EpisodeStatus.SCRIPTING, actor="system")
    text = result.get("text") or ""
    episode.script = text
    episode.cta_config = {
        "enabled": True,
        "style": "gentle_end_card",
        "text": "If you liked this adventure, you can like the video and subscribe for new stories.",
    }
    episode.parent_facing_info = {
        "synopsis": episode.synopsis,
        "age_band": episode.age_band,
        "themes": (series.themes if series else []),
        "skills": (series.educational_domains if series else []),
        "note": "Entertainment with gentle learning moments — not clinical advice.",
    }
    _split_scenes(session, episode)
    session.refresh(episode)
    detect_characters_in_script(session, episode)
    transition_episode(session, episode, EpisodeStatus.SCRIPT_READY, actor="system")
    update_job_status(
        session, job, "succeeded", output_refs={"chars": len(text)}, cost=result.get("cost")
    )
    return episode


def _split_scenes(session: Session, episode: Episode) -> list[Scene]:
    for old in list(episode.scenes or []):
        session.delete(old)
    session.flush()
    chunks = re.split(r"\n\s*SCENE\s+\d+[^\n]*\n", episode.script, flags=re.I)
    headers = re.findall(r"SCENE\s+\d+[^\n]*", episode.script, flags=re.I)
    body_parts = [c.strip() for c in chunks if c.strip()]
    # If script has no SCENE markers, create 3 equal-ish narrative beats.
    if not headers:
        paragraphs = [p.strip() for p in episode.script.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [episode.script or episode.synopsis or episode.title]
        body_parts = paragraphs[:6]
        headers = [f"Scene {i+1}" for i in range(len(body_parts))]
    scenes: list[Scene] = []
    duration = max(5.0, (episode.target_duration_sec or 390) / max(len(body_parts), 1))
    for index, (header, body) in enumerate(zip(headers, body_parts)):
        scene = Scene(
            episode_id=episode.id,
            index=index,
            title=header.strip()[:200],
            description=body[:500],
            dialogue=body,
            setting=header.strip(),
            action=body.split("\n")[0][:300] if body else "",
            duration_sec=duration,
            visual_prompt=f"{header}: {body[:280]}",
            audio_cue="gentle underscore",
            status="draft",
        )
        session.add(scene)
        scenes.append(scene)
    session.flush()
    return scenes


def run_editorial_reviews(session: Session, episode: Episode) -> dict[str, Any]:
    transition_episode(session, episode, EpisodeStatus.CONTINUITY_CHECK, actor="system")
    continuity = check_continuity(session, episode)

    transition_episode(session, episode, EpisodeStatus.SAFETY_CHECK, actor="system")
    safety_provider = get_provider("safety")
    safety = safety_provider.review(
        f"{episode.title}\n{episode.synopsis}\n{episode.script}",
        age_band=episode.age_band,
    )
    episode.safety_report = safety

    story_quality = {
        "has_beginning_middle_end": bool(episode.scenes) and len(episode.scenes) >= 2,
        "age_band": episode.age_band,
        "cta_gentle": "must subscribe" not in (episode.script or "").lower(),
        "passed": True,
        "notes": [],
    }
    if not story_quality["has_beginning_middle_end"]:
        story_quality["passed"] = False
        story_quality["notes"].append("Need clearer scene progression")
    if not story_quality["cta_gentle"]:
        story_quality["passed"] = False
        story_quality["notes"].append("CTA may be coercive")
    episode.story_quality_report = story_quality

    educational = {
        "domains": episode.parent_facing_info.get("skills")
        if episode.parent_facing_info
        else [],
        "lecture_free": "lesson:" not in (episode.script or "").lower(),
        "passed": True,
        "disclaimer": "Educational opportunities are narrative-based, not clinical claims.",
    }
    episode.educational_report = educational

    blocked = (
        not continuity.get("passed", True)
        or not safety.get("passed", True)
        or not story_quality.get("passed", True)
    )
    if blocked:
        transition_episode(
            session,
            episode,
            EpisodeStatus.BLOCKED,
            actor="system",
            details={"reason": "editorial_gate"},
        )
    else:
        transition_episode(session, episode, EpisodeStatus.STORYBOARD_PENDING, actor="system")
    return {
        "continuity": continuity,
        "safety": safety,
        "story_quality": story_quality,
        "educational": educational,
        "blocked": blocked,
    }


def generate_storyboard(session: Session, episode: Episode) -> Storyboard:
    if EpisodeStatus(episode.status) not in {
        EpisodeStatus.STORYBOARD_PENDING,
        EpisodeStatus.STORYBOARD_READY,
        EpisodeStatus.STORYBOARD_APPROVED,
    }:
        # Allow regeneration from script-ready path after reviews.
        if EpisodeStatus(episode.status) == EpisodeStatus.SCRIPT_READY:
            run_editorial_reviews(session, episode)

    job = create_job(
        session,
        stage=JobStage.STORYBOARD,
        episode_id=episode.id,
        idempotency_key=f"storyboard:{episode.id}:r{episode.revision_number}",
        provider="local",
    )
    update_job_status(session, job, "running")
    panels = []
    for scene in sorted(episode.scenes, key=lambda s: s.index):
        panels.append(
            {
                "scene_id": scene.id,
                "index": scene.index,
                "title": scene.title,
                "framing": "medium",
                "characters": scene.characters,
                "setting": scene.setting,
                "action": scene.action,
                "dialogue": scene.dialogue[:400],
                "duration_sec": scene.duration_sec,
                "visual_prompt": scene.visual_prompt,
            }
        )
    payload = json.dumps(panels, sort_keys=True).encode("utf-8")
    checksum = hashlib.sha256(payload).hexdigest()
    # Invalidate prior current storyboards' approval by creating a new version.
    prior = (
        session.query(Storyboard)
        .filter(Storyboard.episode_id == episode.id)
        .order_by(Storyboard.version.desc())
        .first()
    )
    version = (prior.version + 1) if prior else 1
    board = Storyboard(
        episode_id=episode.id,
        version=version,
        panels=panels,
        status="ready",
        approved=False,
        checksum=checksum,
    )
    session.add(board)
    session.flush()
    transition_episode(session, episode, EpisodeStatus.STORYBOARD_READY, actor="system")
    update_job_status(
        session, job, "succeeded", output_refs={"storyboard_id": board.id, "checksum": checksum}
    )
    write_audit(
        session,
        action="storyboard.generated",
        entity_type="storyboard",
        entity_id=board.id,
        details={"version": version},
        actor="system",
    )
    return board


def run_story_pipeline(
    session: Session, episode: Episode, *, generate_board: bool = True
) -> dict[str, Any]:
    generate_script_for_episode(session, episode)
    reviews = run_editorial_reviews(session, episode)
    board = None
    if generate_board and not reviews.get("blocked"):
        board = generate_storyboard(session, episode)
    return {"episode_id": episode.id, "reviews": reviews, "storyboard_id": board.id if board else None}
