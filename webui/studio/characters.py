"""Character Design Studio UI."""

from __future__ import annotations

import json

import streamlit as st

from app.studio.characters import approve_design, create_character, create_design_version, reject_design
from app.studio.db import get_session
from app.studio.models import Character, CharacterDesignVersion, CharacterRelationship
from app.studio.service import list_series


def render() -> None:
    st.subheader("Character Design Studio")
    series_rows = list_series()
    if not series_rows:
        st.warning("No series found.")
        return
    options = {s["title"]: s["id"] for s in series_rows}
    series_id = options[st.selectbox("Series", list(options.keys()), key="char_series")]

    with get_session() as session:
        characters = (
            session.query(Character).filter(Character.series_id == series_id).order_by(Character.name).all()
        )
        st.markdown("#### Library")
        st.dataframe(
            [
                {
                    "name": c.name,
                    "role": c.role,
                    "status": c.status,
                    "approved_design": (c.approved_design_version_id or "")[:8],
                }
                for c in characters
            ],
            use_container_width=True,
        )

        with st.expander("Create character"):
            name = st.text_input("Name")
            role = st.selectbox("Role", ["main", "parent", "sibling", "friend", "supporting"])
            personality = st.text_area("Personality")
            if st.button("Create") and name.strip():
                create_character(
                    session,
                    series_id,
                    name=name.strip(),
                    role=role,
                    personality=personality,
                )
                st.success(f"Created {name}")
                st.rerun()

        if not characters:
            return

        selected = st.selectbox("Edit character", [c.name for c in characters], key="char_edit")
        character = next(c for c in characters if c.name == selected)
        st.write(character.personality)
        designs = (
            session.query(CharacterDesignVersion)
            .filter(CharacterDesignVersion.character_id == character.id)
            .order_by(CharacterDesignVersion.version.desc())
            .all()
        )
        current_attrs = designs[0].attributes if designs else {}
        attrs_raw = st.text_area(
            "Design attributes (JSON)",
            value=json.dumps(current_attrs, indent=2),
            height=180,
        )
        notes = st.text_input("Owner notes / natural-language feedback")
        c1, c2, c3 = st.columns(3)
        if c1.button("New design version"):
            create_design_version(
                session, character, json.loads(attrs_raw or "{}"), owner_notes=notes
            )
            st.success("Design version created (draft)")
            st.rerun()
        if designs:
            if c2.button("Approve latest design", type="primary"):
                approve_design(session, designs[0])
                st.success("Design approved and locked for production")
                st.rerun()
            if c3.button("Request design revision"):
                reject_design(session, designs[0], notes=notes)
                st.warning("Marked needs revision")
                st.rerun()

        rels = (
            session.query(CharacterRelationship)
            .filter(CharacterRelationship.from_character_id == character.id)
            .all()
        )
        st.markdown("#### Relationships")
        for rel in rels:
            other = session.get(Character, rel.to_character_id)
            st.write(f"- {rel.relationship_type}: {other.name if other else rel.to_character_id}")
