"""Series Bible editor and arc planner."""

from __future__ import annotations

import json

import streamlit as st

from app.studio.continuity import get_current_bible, save_bible_version
from app.studio.db import get_session
from app.studio.models import Series, StoryArc
from app.studio.service import list_series


def render() -> None:
    st.subheader("Series Bible")
    series_rows = list_series()
    if not series_rows:
        st.warning("No series found.")
        return

    options = {f"{s['title']} ({s['id'][:8]})": s["id"] for s in series_rows}
    selected = st.selectbox("Series", list(options.keys()))
    series_id = options[selected]

    with get_session() as session:
        series = session.get(Series, series_id)
        bible = get_current_bible(session, series_id)
        arcs = session.query(StoryArc).filter(StoryArc.series_id == series_id).all()

        st.markdown(f"### {series.title}")
        premise = st.text_area("Premise", value=series.premise, height=100)
        age_band = st.text_input("Age band", value=series.age_band)
        tone = st.text_input("Tone", value=series.tone)
        themes = st.text_input("Themes (comma-separated)", value=", ".join(series.themes or []))
        boundaries = st.text_area(
            "Content boundaries (one per line)",
            value="\n".join(series.content_boundaries or []),
            height=100,
        )

        content_raw = st.text_area(
            "Bible content (JSON)",
            value=json.dumps((bible.content if bible else {}), indent=2),
            height=200,
        )
        memory_raw = st.text_area(
            "Continuity memory (JSON)",
            value=json.dumps((bible.continuity_memory if bible else {}), indent=2),
            height=200,
        )

        col1, col2 = st.columns(2)
        if col1.button("Save series + new bible version", type="primary"):
            try:
                content = json.loads(content_raw or "{}")
                memory = json.loads(memory_raw or "{}")
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: {exc}")
                return
            series.premise = premise
            series.age_band = age_band
            series.tone = tone
            series.themes = [t.strip() for t in themes.split(",") if t.strip()]
            series.content_boundaries = [b.strip() for b in boundaries.splitlines() if b.strip()]
            save_bible_version(session, series_id, content, memory, approve=False)
            st.success(f"Saved bible version {(bible.version + 1) if bible else 1}")
            st.rerun()
        if col2.button("Approve current bible"):
            if bible:
                bible.approved = True
                series.approved = True
                st.success("Bible approved")
            else:
                st.warning("No bible to approve")

        st.markdown("#### Story arc planner")
        for arc in arcs:
            with st.expander(f"{arc.title} ({'approved' if arc.approved else 'draft'})"):
                st.write(arc.premise)
                st.json(arc.milestones)
                st.write("Open questions:", arc.open_questions)
                new_milestones = st.text_area(
                    "Milestones JSON",
                    value=json.dumps(arc.milestones, indent=2),
                    key=f"arc_m_{arc.id}",
                )
                if st.button("Update milestones", key=f"arc_save_{arc.id}"):
                    arc.milestones = json.loads(new_milestones)
                    st.success("Arc updated")
