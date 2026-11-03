"""Automation modes, pause controls, budgets."""

from __future__ import annotations

import streamlit as st

from app.studio.db import get_session
from app.studio.enums import AutomationMode
from app.studio.models import Channel, StudioSettings
from app.studio.service import list_channels
from app.studio.workflow import write_audit


def render() -> None:
    st.subheader("Automation & Safety Controls")
    st.caption("Default mode is Assisted. Autonomous publishing requires explicit opt-in.")

    with get_session() as session:
        settings = session.query(StudioSettings).first()
        if settings is None:
            settings = StudioSettings()
            session.add(settings)
            session.flush()

        global_pause = st.toggle("GLOBAL PAUSE automation", value=bool(settings.global_pause))
        if global_pause != settings.global_pause:
            settings.global_pause = global_pause
            write_audit(
                session,
                action="automation.global_pause",
                entity_type="studio_settings",
                entity_id=settings.id,
                details={"global_pause": global_pause},
            )
            st.session_state["studio_global_pause_banner"] = global_pause
            st.success("Global pause updated")

        channels = list_channels()
        if not channels:
            st.info("No channels.")
            return

        channel_map = {c["name"]: c["id"] for c in channels}
        channel_id = channel_map[st.selectbox("Channel", list(channel_map.keys()))]
        channel = session.get(Channel, channel_id)

        mode = st.selectbox(
            "Mode",
            [AutomationMode.MANUAL.value, AutomationMode.ASSISTED.value, AutomationMode.AUTONOMOUS.value],
            index=[AutomationMode.MANUAL.value, AutomationMode.ASSISTED.value, AutomationMode.AUTONOMOUS.value].index(
                channel.automation_mode
                if channel.automation_mode
                in {
                    AutomationMode.MANUAL.value,
                    AutomationMode.ASSISTED.value,
                    AutomationMode.AUTONOMOUS.value,
                }
                else AutomationMode.ASSISTED.value
            ),
        )
        pause_channel = st.toggle("Pause this channel", value=bool(channel.pause_automation))
        auto_publish = st.toggle(
            "Auto-publish (dangerous opt-in)",
            value=bool(channel.auto_publish_enabled),
        )
        if auto_publish:
            st.error(
                "Auto-publish bypasses per-video owner approval. Keep this OFF unless you fully understand the risk."
            )
        budget_ep = st.number_input(
            "Per-episode budget",
            value=float(channel.budget_per_episode or 0),
            min_value=0.0,
        )
        budget_mo = st.number_input(
            "Monthly budget",
            value=float(channel.budget_monthly or 0),
            min_value=0.0,
        )
        max_uploads = st.number_input(
            "Max uploads / week",
            value=int(channel.max_uploads_per_week or 3),
            min_value=0,
            max_value=21,
        )
        if st.button("Save channel automation", type="primary"):
            channel.automation_mode = mode
            channel.pause_automation = pause_channel
            channel.auto_publish_enabled = auto_publish
            channel.budget_per_episode = budget_ep or None
            channel.budget_monthly = budget_mo or None
            channel.max_uploads_per_week = int(max_uploads)
            write_audit(
                session,
                action="automation.channel_updated",
                entity_type="channel",
                entity_id=channel.id,
                details={
                    "mode": mode,
                    "pause": pause_channel,
                    "auto_publish": auto_publish,
                },
            )
            st.success("Saved")
