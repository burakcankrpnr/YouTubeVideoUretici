"""Series bible access and continuity checks."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.studio.models import Character, Episode, Series, SeriesBible
from app.studio.workflow import write_audit


def get_current_bible(session: Session, series_id: str) -> SeriesBible | None:
    return (
        session.query(SeriesBible)
        .filter(SeriesBible.series_id == series_id, SeriesBible.is_current.is_(True))
        .one_or_none()
    )


def save_bible_version(
    session: Session,
    series_id: str,
    content: dict[str, Any],
    continuity_memory: dict[str, Any] | None = None,
    *,
    approve: bool = False,
) -> SeriesBible:
    current = get_current_bible(session, series_id)
    next_version = (current.version + 1) if current else 1
    if current:
        current.is_current = False
    bible = SeriesBible(
        series_id=series_id,
        version=next_version,
        content=content,
        continuity_memory=continuity_memory
        or (current.continuity_memory if current else {}),
        is_current=True,
        approved=approve,
    )
    session.add(bible)
    write_audit(
        session,
        action="bible.saved",
        entity_type="series_bible",
        entity_id=bible.id,
        details={"version": next_version, "approved": approve},
    )
    return bible


def check_continuity(session: Session, episode: Episode) -> dict[str, Any]:
    """Flag likely continuity issues; does not claim perfect detection."""
    series = session.get(Series, episode.series_id)
    bible = get_current_bible(session, episode.series_id)
    characters = (
        session.query(Character).filter(Character.series_id == episode.series_id).all()
    )
    known_names = {c.name.lower() for c in characters}
    script = episode.script or ""
    flags: list[dict[str, str]] = []

    memory = (bible.continuity_memory if bible else {}) or {}
    used_plots = [str(p).lower() for p in memory.get("used_plots", [])]
    synopsis_l = (episode.synopsis or "").lower()
    for plot in used_plots:
        if plot and plot in synopsis_l:
            flags.append(
                {
                    "severity": "medium",
                    "code": "plot_reuse",
                    "message": f"Synopsis may reuse prior plot: {plot}",
                }
            )

    # Dialogue speakers not present in the approved character library.
    speakers = set(re.findall(r"(?m)^([A-Z][a-zA-Z]{1,20})\s*:", script))
    unknown = sorted(
        n
        for n in speakers
        if n.lower() not in known_names and n not in {"Narrator", "Title", "Scene", "CTA"}
    )
    if unknown:
        flags.append(
            {
                "severity": "high",
                "code": "unknown_character",
                "message": f"Possible new characters mentioned: {', '.join(unknown)}",
            }
        )

    boundaries = (series.content_boundaries if series else []) or []
    for boundary in boundaries:
        if "frightening" in boundary.lower() and re.search(
            r"\b(scary|terrified|nightmare|monster attack)\b", script, re.I
        ):
            flags.append(
                {
                    "severity": "high",
                    "code": "boundary",
                    "message": f"May violate boundary: {boundary}",
                }
            )

    unresolved = memory.get("unresolved_arcs") or []
    report = {
        "passed": not any(f["severity"] == "high" for f in flags),
        "flags": flags,
        "unresolved_arcs": unresolved,
        "bible_version": bible.version if bible else None,
        "disclaimer": "Continuity checks are heuristic signals, not guarantees.",
    }
    episode.continuity_report = report
    write_audit(
        session,
        action="continuity.checked",
        entity_type="episode",
        entity_id=episode.id,
        details={"passed": report["passed"], "flag_count": len(flags)},
        actor="system",
    )
    return report


def update_memory_after_publish(session: Session, episode: Episode) -> None:
    bible = get_current_bible(session, episode.series_id)
    if not bible:
        return
    memory = dict(bible.continuity_memory or {})
    summaries = list(memory.get("episode_summaries") or [])
    summaries.append(
        {
            "episode_id": episode.id,
            "title": episode.title,
            "synopsis": episode.synopsis,
        }
    )
    used = list(memory.get("used_plots") or [])
    if episode.synopsis:
        used.append(episode.synopsis[:120])
    memory["episode_summaries"] = summaries[-50:]
    memory["used_plots"] = used[-50:]
    bible.continuity_memory = memory
    write_audit(
        session,
        action="continuity.memory_updated",
        entity_type="series_bible",
        entity_id=bible.id,
        details={"episode_id": episode.id},
        actor="system",
    )
