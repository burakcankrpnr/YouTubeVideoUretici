"""Episode ideas, scripts, and pipeline controls."""

from __future__ import annotations

import streamlit as st

from app.studio.db import get_session
from app.studio.enums import ContentFormat
from app.studio.models import Episode, StoryIdea
from app.studio.service import (
    create_episode,
    create_ideas_for_series,
    get_episode_detail,
    list_channels,
    list_episodes,
    list_series,
    run_episode_story,
)


def render() -> None:
    st.subheader("Episodes & Ideas")
    series_rows = list_series()
    channels = list_channels()
    if not series_rows:
        st.warning("No series found.")
        return

    series_map = {s["title"]: s["id"] for s in series_rows}
    series_title = st.selectbox("Series", list(series_map.keys()), key="ep_series")
    series_id = series_map[series_title]
    channel_map = {c["name"]: c["id"] for c in channels}
    channel_id = channel_map[st.selectbox("Channel", list(channel_map.keys()), key="ep_channel")] if channel_map else None

    tab_ideas, tab_create, tab_list = st.tabs(["Ideas", "Create episode", "Episode list"])

    with tab_ideas:
        if st.button("Generate episode ideas"):
            ideas = create_ideas_for_series(series_id)
            st.session_state["studio_ideas"] = ideas
        ideas = st.session_state.get("studio_ideas") or []
        with get_session() as session:
            db_ideas = (
                session.query(StoryIdea)
                .filter(StoryIdea.series_id == series_id)
                .order_by(StoryIdea.created_at.desc())
                .limit(20)
                .all()
            )
            ideas = ideas or [{"id": i.id, "title": i.title, "premise": i.premise} for i in db_ideas]
        for idea in ideas:
            st.markdown(f"**{idea['title']}**")
            st.write(idea["premise"])
            if st.button(f"Create episode from idea: {idea['title']}", key=f"idea_{idea['id']}"):
                eid = create_episode(
                    series_id=series_id,
                    title=idea["title"],
                    synopsis=idea["premise"],
                    channel_id=channel_id,
                )
                st.success(f"Created episode {eid}")
                st.session_state["studio_selected_episode"] = eid

    with tab_create:
        title = st.text_input("Title", value="A Soft Hill Discovery")
        synopsis = st.text_area("Synopsis")
        fmt = st.selectbox("Format", [ContentFormat.LONG_FORM.value, ContentFormat.SHORTS.value])
        language = st.text_input("Language", value="en")
        age_band = st.text_input("Age band override", value="")
        if st.button("Create draft episode", type="primary"):
            eid = create_episode(
                series_id=series_id,
                title=title,
                synopsis=synopsis,
                channel_id=channel_id,
                content_format=fmt,
                language=language,
                age_band=age_band or None,
            )
            st.success(f"Created {eid}")
            st.session_state["studio_selected_episode"] = eid

    with tab_list:
        episodes = list_episodes(series_id)
        st.dataframe(episodes, use_container_width=True)
        if episodes:
            ep_map = {f"{e['title']} [{e['status']}]": e["id"] for e in episodes}
            choice = st.selectbox("Open episode", list(ep_map.keys()))
            episode_id = ep_map[choice]
            st.session_state["studio_selected_episode"] = episode_id
            detail = get_episode_detail(episode_id)
            if detail:
                st.markdown(f"### {detail['title']}")
                st.caption(f"Status: `{detail['status']}` · rev {detail['revision_number']} · {detail['format']}")
                st.text_area("Script", value=detail.get("script") or "", height=240, disabled=True)
                if st.button("Run story pipeline (script → continuity → safety → storyboard)"):
                    with st.spinner("Running agents..."):
                        result = run_episode_story(episode_id)
                    st.success(result)
                    st.rerun()
                st.json(
                    {
                        "continuity": detail.get("continuity_report"),
                        "safety": detail.get("safety_report"),
                        "story_quality": detail.get("story_quality_report"),
                        "roster": detail.get("character_roster"),
                        "parent_info": detail.get("parent_facing_info"),
                    }
                )
