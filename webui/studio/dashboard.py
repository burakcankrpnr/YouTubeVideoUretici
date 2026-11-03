"""Studio dashboard."""

from __future__ import annotations

import streamlit as st

from app.studio.db import get_session
from app.studio.models import Episode, Notification, ProductionJob, StudioSettings
from app.studio.service import list_channels, list_episodes, list_series


def render() -> None:
    st.subheader("Dashboard")
    st.info(
        "Want zero manual work? Open the **Autopilot** page and press "
        "**START AUTOPILOT** — the AI runs the full episode loop for you."
    )
    series = list_series()
    channels = list_channels()
    episodes = list_episodes()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Series", len(series))
    c2.metric("Channels", len(channels))
    c3.metric("Episodes", len(episodes))
    review_ready = sum(1 for e in episodes if e["status"] == "review_ready")
    c4.metric("Awaiting review", review_ready)

    with get_session() as session:
        settings = session.query(StudioSettings).first()
        paused = bool(settings and settings.global_pause)
        st.session_state["studio_global_pause_banner"] = paused
        notes = (
            session.query(Notification)
            .filter(Notification.read.is_(False))
            .order_by(Notification.created_at.desc())
            .limit(8)
            .all()
        )
        jobs = (
            session.query(ProductionJob)
            .order_by(ProductionJob.updated_at.desc())
            .limit(8)
            .all()
        )

    if paused:
        st.error("Global automation pause is active.")

    st.markdown("#### Notifications")
    if not notes:
        st.info("No unread notifications.")
    else:
        for note in notes:
            st.write(f"**{note.title}** — {note.body}")

    st.markdown("#### Recent episodes")
    if episodes:
        st.dataframe(episodes, use_container_width=True)
    else:
        st.info("No episodes yet. Create one under Episodes.")

    st.markdown("#### Recent jobs")
    if jobs:
        st.dataframe(
            [
                {
                    "id": j.id[:8],
                    "stage": j.stage,
                    "status": j.status,
                    "provider": j.provider,
                    "episode": (j.episode_id or "")[:8],
                }
                for j in jobs
            ],
            use_container_width=True,
        )
