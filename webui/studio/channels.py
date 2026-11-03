"""Channel list and onboarding wizard."""

from __future__ import annotations

import streamlit as st

from app.studio.db import get_session
from app.studio.enums import AutomationMode
from app.studio.localization import create_localized_episode
from app.studio.models import Channel, ChannelSeries, Episode
from app.studio.service import list_channels, list_episodes, list_series
from app.studio.workflow import write_audit


def render() -> None:
    st.subheader("Channels / Markets")
    channels = list_channels()
    st.dataframe(channels, use_container_width=True)

    from app.studio.mpt_bridge import upload_post_youtube_status

    yt = upload_post_youtube_status()
    st.markdown("#### MoneyPrinterTurbo → YouTube (Upload-Post)")
    st.json(yt)
    if yt.get("ready_for_studio_publish"):
        st.success("Studio can publish approved videos to YouTube through Upload-Post.")
    else:
        st.warning(
            "Configure in classic MPT settings: `upload_post_enabled=true`, API key, "
            "username, and `upload_post_platforms` including `youtube`."
        )

    tab_wizard, tab_localize = st.tabs(["Onboarding wizard", "Localization"])

    with tab_wizard:
        st.markdown("##### Step 1 — Connect YouTube")
        st.info(
            "Primary path: Upload-Post in MoneyPrinterTurbo settings (same account used by Studio publish). "
            "Native YouTube Data API OAuth can be added later."
        )
        oauth_mark = st.checkbox(
            "Mark studio channel as connected (uses Upload-Post readiness)",
            value=bool(yt.get("ready_for_studio_publish")),
        )

        st.markdown("##### Step 2 — Channel identity")
        name = st.text_input("Channel name", value="My Kids Animation Channel")
        language = st.text_input("Language", value="en")
        locale = st.text_input("Locale", value="en-US")
        timezone = st.text_input("Timezone", value="UTC")
        age_band = st.text_input("Age band", value="3-6")
        keywords = st.text_input("Keywords (comma-separated)", value="kids,animation,family")
        audience = st.selectbox("Audience designation", ["made_for_kids", "not_made_for_kids"])

        st.markdown("##### Step 3 — Content strategy")
        series_rows = list_series()
        series_id = None
        if series_rows:
            series_map = {s["title"]: s["id"] for s in series_rows}
            series_id = series_map[st.selectbox("Source series", list(series_map.keys()))]
        cadence = st.number_input("Max uploads / week", min_value=1, max_value=14, value=3)

        st.markdown("##### Step 4 — Automation and budget")
        mode = st.selectbox(
            "Automation mode",
            [AutomationMode.MANUAL.value, AutomationMode.ASSISTED.value, AutomationMode.AUTONOMOUS.value],
            index=1,
        )
        auto_publish = st.checkbox(
            "Enable auto-publish (NOT recommended; bypasses per-video approval)",
            value=False,
        )
        if auto_publish:
            st.error("Auto-publish is an explicit opt-in and is off by default for safety.")
        budget_ep = st.number_input("Per-episode budget USD", min_value=0.0, value=25.0)
        budget_mo = st.number_input("Monthly budget USD", min_value=0.0, value=300.0)

        st.markdown("##### Step 5 — Confirm")
        if st.button("Create / save channel", type="primary"):
            with get_session() as session:
                channel = Channel(
                    name=name,
                    language=language,
                    locale=locale,
                    timezone=timezone,
                    age_band=age_band,
                    keywords=[k.strip() for k in keywords.split(",") if k.strip()],
                    audience_designation=audience,
                    automation_mode=mode,
                    auto_publish_enabled=bool(auto_publish),
                    max_uploads_per_week=int(cadence),
                    budget_per_episode=budget_ep,
                    budget_monthly=budget_mo,
                    oauth_connected=oauth_mark,
                    connection_health="connected" if oauth_mark else "disconnected",
                )
                session.add(channel)
                session.flush()
                if series_id:
                    session.add(ChannelSeries(channel_id=channel.id, series_id=series_id))
                write_audit(
                    session,
                    action="channel.created",
                    entity_type="channel",
                    entity_id=channel.id,
                    details={"name": name, "mode": mode, "auto_publish": auto_publish},
                )
                st.success(f"Channel saved: {channel.id}")
                st.rerun()

    with tab_localize:
        st.caption("Adaptation workflow — not word-for-word translation.")
        episodes = list_episodes()
        if not episodes:
            st.info("No source episodes.")
            return
        ep_map = {e["title"]: e["id"] for e in episodes}
        episode_id = ep_map[st.selectbox("Source episode", list(ep_map.keys()), key="loc_ep")]
        language = st.text_input("Target language code", value="tr", key="loc_lang")
        if st.button("Create localized adaptation"):
            with get_session() as session:
                source = session.get(Episode, episode_id)
                loc = create_localized_episode(session, source, language=language)
                st.success(f"Localized episode {loc.id}")
                st.text_area("Adapted script", value=loc.script, height=200)
