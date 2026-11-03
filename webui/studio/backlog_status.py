"""Honest implementation backlog status."""

from __future__ import annotations

import streamlit as st

from app.studio.backlog import FEATURE_BACKLOG, features_by_priority


def render() -> None:
    st.subheader("Implementation Status")
    st.caption(
        "UI existence alone never marks a feature complete. Status reflects backend + workflow readiness."
    )
    for priority in ("P0", "P1", "P2"):
        st.markdown(f"### {priority}")
        rows = features_by_priority(priority)
        st.dataframe(
            [
                {
                    "id": r["id"],
                    "title": r["title"],
                    "status": r["status"],
                    "notes": r["notes"],
                }
                for r in rows
            ],
            use_container_width=True,
        )

    complete = sum(1 for r in FEATURE_BACKLOG if r["status"] == "complete")
    partial = sum(1 for r in FEATURE_BACKLOG if r["status"] == "partial")
    st.metric("Complete features", complete)
    st.metric("Partial features", partial)
