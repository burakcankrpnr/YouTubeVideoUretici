"""Analytics snapshots and recommendations."""

from __future__ import annotations

import streamlit as st

from app.studio.analytics import latest_snapshot, refresh_analytics
from app.studio.db import get_session
from app.studio.models import Channel
from app.studio.service import list_channels


def render() -> None:
    st.subheader("Analytics")
    st.caption(
        "Recommendations are explainable hypotheses. They never guarantee views, "
        "virality, or monetization. Private competitor analytics are not available."
    )
    channels = list_channels()
    if not channels:
        st.info("No channels.")
        return
    channel_map = {c["name"]: c["id"] for c in channels}
    channel_id = channel_map[st.selectbox("Channel", list(channel_map.keys()), key="an_ch")]

    with get_session() as session:
        channel = session.get(Channel, channel_id)
        if st.button("Refresh analytics snapshot"):
            snap = refresh_analytics(session, channel, use_mock=not channel.oauth_connected)
            st.success(f"Snapshot {snap.id[:8]} ({snap.source})")
        snap = latest_snapshot(session, channel_id)
        if not snap:
            st.info("No snapshots yet.")
            return
        st.write(
            f"Period: {snap.period_start} → {snap.period_end} · sample_size={snap.sample_size} · source={snap.source}"
        )
        st.json(snap.metrics)
        st.markdown("#### Recommendations (require owner approval before applying)")
        for rec in snap.recommendations or []:
            st.write(f"- **{rec.get('action')}**")
            st.caption(
                f"Evidence: {rec.get('evidence')} · confidence={rec.get('confidence')} · "
                f"requires_owner_approval={rec.get('requires_owner_approval')}"
            )
        age = st.text_input("Owner-configurable age band", value=channel.age_band)
        if st.button("Apply age band (owner confirmed)"):
            channel.age_band = age
            st.success("Age band updated")
