"""Durable production queue controls."""

from __future__ import annotations

import streamlit as st

from app.studio.cost import estimate_episode_cost
from app.studio.db import get_session
from app.studio.models import Episode, ProductionJob
from app.studio.production import ProductionError, enqueue_production, process_episode_queue
from app.studio.service import list_episodes


def render() -> None:
    st.subheader("Production Queue")
    st.caption(
        "After storyboard approval, Studio calls MoneyPrinterTurbo (`task.start`) to produce "
        "the real MP4 (TTS + footage + FFmpeg). Mock fallback only if MPT/FFmpeg/source fails."
    )
    from app.studio.providers import get_provider

    assembly = get_provider("assembly", prefer_real=True)
    st.write(
        f"Assembly engine: **{assembly.name}** "
        f"({'ready' if getattr(assembly, 'available', lambda: False)() else 'not ready — will mock if allowed'})"
    )
    episodes = [e for e in list_episodes() if e["status"] in {
        "storyboard_approved", "queued", "producing", "qc_pending", "failed", "blocked", "revising"
    }]
    all_eps = list_episodes()
    st.markdown("#### Cost estimate preview")
    fmt = st.selectbox("Format for estimate", ["long_form", "shorts"])
    st.json(estimate_episode_cost(fmt))

    selectable = all_eps
    if not selectable:
        st.info("No episodes.")
        return
    ep_map = {f"{e['title']} [{e['status']}]": e["id"] for e in selectable}
    episode_id = ep_map[st.selectbox("Episode", list(ep_map.keys()), key="prod_ep")]
    force_budget = st.checkbox("Force continue despite budget warning/hard limit (owner confirm)")

    c1, c2 = st.columns(2)
    with get_session() as session:
        episode = session.get(Episode, episode_id)
        if c1.button("Enqueue production (requires approved storyboard)", type="primary"):
            try:
                ids = enqueue_production(session, episode, force_budget=force_budget)
                st.success(f"Enqueued jobs: {len(ids)}")
            except ProductionError as exc:
                st.error(str(exc))
        allow_mock = st.checkbox(
            "Allow mock fallback if MPT fails",
            value=True,
            help="Uncheck to fail hard when MoneyPrinterTurbo cannot produce a real video.",
        )
        if c2.button("Run MPT production now", type="primary"):
            try:
                enqueue_production(session, episode, force_budget=force_budget)
                with st.spinner("MoneyPrinterTurbo is generating the video…"):
                    render_version = process_episode_queue(
                        session, episode, allow_mock_fallback=allow_mock
                    )
                st.success(
                    f"Render {render_version.id[:8]} ready · engine="
                    f"{(render_version.metadata_payload or {}).get('production_engine')} · "
                    f"checksum={render_version.media_checksum[:12]}…"
                )
                st.code(render_version.media_path or "")
                if (render_version.qc_report or {}).get("warnings"):
                    st.warning(render_version.qc_report["warnings"])
            except ProductionError as exc:
                st.error(str(exc))

        jobs = (
            session.query(ProductionJob)
            .filter(ProductionJob.episode_id == episode_id)
            .order_by(ProductionJob.created_at.desc())
            .limit(40)
            .all()
        )
        st.dataframe(
            [
                {
                    "stage": j.stage,
                    "status": j.status,
                    "provider": j.provider,
                    "attempt": j.attempt,
                    "cost": j.cost,
                    "error": (j.error_detail or "")[:80],
                    "idempotency": j.idempotency_key[:40],
                }
                for j in jobs
            ],
            use_container_width=True,
        )

        if episode:
            st.markdown("#### Episode cost")
            st.write(
                {
                    "estimate": episode.cost_estimate,
                    "actual": episode.cost_actual,
                    "breakdown": episode.cost_breakdown,
                }
            )
