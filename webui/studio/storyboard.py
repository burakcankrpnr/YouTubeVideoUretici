"""Storyboard review and approval gate."""

from __future__ import annotations

import streamlit as st

from app.studio.agents.pipeline import generate_storyboard
from app.studio.db import get_session
from app.studio.models import Episode, Storyboard
from app.studio.publish import approve_storyboard
from app.studio.service import list_episodes


def render() -> None:
    st.subheader("Storyboard")
    st.caption("Full animation cannot start until the owner approves the storyboard version.")
    episodes = list_episodes()
    if not episodes:
        st.info("No episodes yet.")
        return
    ep_map = {f"{e['title']} [{e['status']}]": e["id"] for e in episodes}
    default = st.session_state.get("studio_selected_episode")
    labels = list(ep_map.keys())
    index = 0
    if default:
        for i, label in enumerate(labels):
            if ep_map[label] == default:
                index = i
                break
    label = st.selectbox("Episode", labels, index=index)
    episode_id = ep_map[label]
    st.session_state["studio_selected_episode"] = episode_id

    with get_session() as session:
        episode = session.get(Episode, episode_id)
        boards = (
            session.query(Storyboard)
            .filter(Storyboard.episode_id == episode_id)
            .order_by(Storyboard.version.desc())
            .all()
        )
        if st.button("Generate / regenerate storyboard"):
            board = generate_storyboard(session, episode)
            st.success(f"Storyboard v{board.version} ready")
            st.rerun()

        if not boards:
            st.info("No storyboard yet.")
            return

        board = boards[0]
        st.markdown(f"#### Version {board.version} — {'APPROVED' if board.approved else board.status}")
        st.caption(f"Checksum: `{board.checksum}`")
        for panel in board.panels or []:
            with st.expander(f"Panel {panel.get('index')}: {panel.get('title')}"):
                st.write(panel.get("action"))
                st.write(panel.get("dialogue"))
                st.caption(f"Duration ~{panel.get('duration_sec')}s · {panel.get('visual_prompt')}")

        c1, c2 = st.columns(2)
        if c1.button("Approve storyboard", type="primary", disabled=board.approved):
            approve_storyboard(session, episode, board.id)
            st.success("Storyboard approved — production may be queued")
            st.rerun()
        if c2.button("Request storyboard changes"):
            board.approved = False
            board.status = "needs_revision"
            st.warning("Marked needs revision — regenerate after edits")
