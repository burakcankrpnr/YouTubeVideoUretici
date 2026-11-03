"""Animation Studio entry: sidebar navigation + page router."""

from __future__ import annotations

import streamlit as st

from app.studio.service import bootstrap_studio
from webui.studio import (
    analytics,
    automation,
    autopilot,
    backlog_status,
    channels,
    characters,
    dashboard,
    episodes,
    production_queue,
    review_workspace,
    series_bible,
    settings,
    storyboard,
)


PAGES = [
    ("Autopilot", autopilot.render),
    ("Dashboard", dashboard.render),
    ("Series Bible", series_bible.render),
    ("Characters", characters.render),
    ("Episodes", episodes.render),
    ("Storyboard", storyboard.render),
    ("Production Queue", production_queue.render),
    ("Review", review_workspace.render),
    ("Channels", channels.render),
    ("Automation", automation.render),
    ("Analytics", analytics.render),
    ("Settings", settings.render),
    ("Implementation Status", backlog_status.render),
]


def render_animation_studio() -> None:
    bootstrap = bootstrap_studio()
    st.session_state.setdefault("studio_bootstrap", bootstrap)

    st.title("Global AI Animation Studio")
    st.caption(
        "Hands-off mode available: open Autopilot and press START — AI + MoneyPrinterTurbo "
        "fill, produce, and publish without manual forms."
    )

    labels = [label for label, _ in PAGES]
    page = st.sidebar.radio("Studio pages", labels, key="studio_page", index=0)
    st.sidebar.info(
        "Demo series seeded" if bootstrap.get("seeded") == "true" else "Studio database ready"
    )
    if st.session_state.get("studio_global_pause_banner"):
        st.sidebar.error("GLOBAL PAUSE is ON — new production/publish blocked")

    for label, renderer in PAGES:
        if label == page:
            renderer()
            break
