"""Character design studio, versioning, and script roster detection."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.studio.enums import CharacterDesignStatus
from app.studio.models import Character, CharacterDesignVersion, Episode
from app.studio.workflow import write_audit


def create_character(
    session: Session,
    series_id: str,
    *,
    name: str,
    role: str = "supporting",
    **fields: Any,
) -> Character:
    character = Character(series_id=series_id, name=name.strip(), role=role, **fields)
    session.add(character)
    session.flush()
    design = CharacterDesignVersion(
        character_id=character.id,
        version=1,
        status=CharacterDesignStatus.DRAFT.value,
        attributes=fields.get("attributes") or {},
    )
    session.add(design)
    session.flush()
    write_audit(
        session,
        action="character.created",
        entity_type="character",
        entity_id=character.id,
        details={"name": name},
    )
    return character


def create_design_version(
    session: Session,
    character: Character,
    attributes: dict[str, Any],
    *,
    owner_notes: str = "",
    prompt_config: dict[str, Any] | None = None,
) -> CharacterDesignVersion:
    latest = (
        session.query(CharacterDesignVersion)
        .filter(CharacterDesignVersion.character_id == character.id)
        .order_by(CharacterDesignVersion.version.desc())
        .first()
    )
    version = (latest.version + 1) if latest else 1
    design = CharacterDesignVersion(
        character_id=character.id,
        version=version,
        status=CharacterDesignStatus.DRAFT.value,
        attributes=attributes,
        owner_notes=owner_notes,
        prompt_config=prompt_config or {},
        reference_assets=[],
    )
    session.add(design)
    session.flush()
    character.status = CharacterDesignStatus.DRAFT.value
    write_audit(
        session,
        action="character.design_created",
        entity_type="character_design",
        entity_id=design.id,
        details={"character_id": character.id, "version": version},
    )
    return design


def approve_design(session: Session, design: CharacterDesignVersion) -> CharacterDesignVersion:
    design.status = CharacterDesignStatus.APPROVED.value
    design.approved_at = datetime.now(timezone.utc)
    character = session.get(Character, design.character_id)
    if character:
        character.approved_design_version_id = design.id
        character.status = CharacterDesignStatus.APPROVED.value
    write_audit(
        session,
        action="character.design_approved",
        entity_type="character_design",
        entity_id=design.id,
        details={"character_id": design.character_id},
    )
    return design


def reject_design(
    session: Session, design: CharacterDesignVersion, notes: str = ""
) -> CharacterDesignVersion:
    design.status = CharacterDesignStatus.NEEDS_REVISION.value
    if notes:
        design.owner_notes = notes
    character = session.get(Character, design.character_id)
    if character:
        character.status = CharacterDesignStatus.NEEDS_REVISION.value
    write_audit(
        session,
        action="character.design_rejected",
        entity_type="character_design",
        entity_id=design.id,
        details={"notes": notes},
    )
    return design


def detect_characters_in_script(session: Session, episode: Episode) -> dict[str, Any]:
    characters = (
        session.query(Character).filter(Character.series_id == episode.series_id).all()
    )
    known = {c.name: c for c in characters}
    known_lower = {c.name.lower(): c for c in characters}
    script = episode.script or ""
    corpus = f"{episode.title}\n{episode.synopsis}\n{script}"
    found_known: list[dict[str, Any]] = []
    for name, character in known.items():
        if re.search(rf"\b{re.escape(name)}\b", corpus, re.I):
            found_known.append(
                {
                    "character_id": character.id,
                    "name": character.name,
                    "approved": character.status == CharacterDesignStatus.APPROVED.value,
                    "design_version_id": character.approved_design_version_id,
                }
            )

    # Only treat dialogue speaker labels ("Name:") as new-character candidates.
    speaker_names = set(re.findall(r"(?m)^([A-Z][a-zA-Z]{1,20})\s*:", script))
    proposed: list[dict[str, str]] = []
    for name in sorted(speaker_names):
        if name.lower() in known_lower or name in {"Narrator", "Title", "Scene", "CTA"}:
            continue
        proposed.append({"name": name, "status": "needs_profile"})

    roster = {
        "known": found_known,
        "proposed_new": proposed,
        "production_blocked": any(not item["approved"] for item in found_known)
        or bool(proposed),
    }
    episode.character_roster = roster
    write_audit(
        session,
        action="character.roster_detected",
        entity_type="episode",
        entity_id=episode.id,
        details={
            "known": len(found_known),
            "proposed_new": len(proposed),
            "blocked": roster["production_blocked"],
        },
        actor="system",
    )
    return roster


def ensure_proposed_characters(session: Session, episode: Episode) -> list[Character]:
    roster = episode.character_roster or detect_characters_in_script(session, episode)
    created: list[Character] = []
    for item in roster.get("proposed_new") or []:
        name = item.get("name")
        if not name:
            continue
        existing = (
            session.query(Character)
            .filter(Character.series_id == episode.series_id, Character.name == name)
            .one_or_none()
        )
        if existing:
            continue
        created.append(
            create_character(
                session,
                episode.series_id,
                name=name,
                role="supporting",
                personality="Proposed from script; awaiting owner design approval",
            )
        )
    if created:
        detect_characters_in_script(session, episode)
    return created
