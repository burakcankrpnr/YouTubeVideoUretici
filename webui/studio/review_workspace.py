"""Owner review workspace and publication actions."""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from app.studio.db import get_session
from app.studio.models import Episode
from app.studio.production import apply_revision
from app.studio.publish import PublishError, schedule_or_publish
from app.studio.review import (
    ReviewError,
    approve_render,
    current_render,
    reject_render,
    request_revision,
)
from app.studio.service import list_episodes


def render() -> None:
    st.subheader("Review Workspace")
    st.caption("Approval is bound to the exact render checksum + metadata version.")
    candidates = [
        e
        for e in list_episodes()
        if e["status"]
        in {
            "review_ready",
            "approved",
            "revision_requested",
            "scheduled",
            "published",
            "rejected",
            "blocked",
        }
    ] or list_episodes()
    if not candidates:
        st.info("No episodes to review.")
        return
    ep_map = {f"{e['title']} [{e['status']}]": e["id"] for e in candidates}
    episode_id = ep_map[st.selectbox("Episode", list(ep_map.keys()), key="review_ep")]

    with get_session() as session:
        episode = session.get(Episode, episode_id)
        render = current_render(session, episode_id)
        if episode is None or render is None:
            st.warning("No current render. Run production first.")
            return

        st.markdown(f"### {episode.title}")
        st.write(
            f"Format: **{episode.content_format}** · Language: **{episode.language}** · "
            f"Duration target: {episode.target_duration_sec}s · Revision {render.revision_number}"
        )
        st.code(render.media_path or "(no path)")
        st.caption(f"Checksum: `{render.media_checksum}`")
        if render.media_path and str(render.media_path).endswith((".mp4", ".webm", ".mov")):
            st.video(render.media_path)
        else:
            st.info(
                "Preview file is a mock placeholder JSON in demo mode — not a real video. "
                "Connect real video providers for playable output."
            )

        meta = dict(render.metadata_payload or {})
        meta["title"] = st.text_input("Title", value=meta.get("title") or episode.title)
        meta["description"] = st.text_area(
            "Description", value=meta.get("description") or episode.synopsis or "", height=120
        )
        meta["ai_disclosure_acknowledged"] = st.checkbox(
            "I acknowledge AI/synthetic media disclosure requirements for this upload",
            value=bool(meta.get("ai_disclosure_acknowledged")),
        )
        if st.button("Save metadata to current render"):
            render.metadata_payload = meta
            render.metadata_version = int(render.metadata_version or 1) + 1
            st.success("Metadata saved (prior approval invalidated if checksum/metadata changed)")
            st.rerun()

        st.json(render.qc_report or {})
        st.markdown("#### Parent-facing info")
        st.json(episode.parent_facing_info or {})

        feedback = st.text_area("Revision feedback (natural language)")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Approve this version", type="primary"):
            try:
                render.metadata_payload = meta
                approve_render(session, episode, render)
                st.success("Approved")
                st.rerun()
            except ReviewError as exc:
                st.error(str(exc))
        if c2.button("Request revision"):
            try:
                request_revision(session, episode, render, feedback)
                result = apply_revision(session, episode, feedback)
                st.warning(result)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
        if c3.button("Reject"):
            reject_render(session, episode, render, feedback or "rejected")
            st.error("Rejected")
            st.rerun()
        from app.studio.mpt_bridge import upload_post_youtube_status

        yt_status = upload_post_youtube_status()
        if yt_status.get("ready_for_studio_publish"):
            st.success(
                f"YouTube via Upload-Post ready (user: {yt_status.get('username')})"
            )
        else:
            st.warning(
                "Upload-Post YouTube not ready. Enable Upload-Post in MPT settings, "
                "set API key + username, and include `youtube` in platforms. "
                "You can still demo with mock publish."
            )

        force_mock = st.checkbox(
            "Force mock publish (demo only — does not upload to YouTube)",
            value=not yt_status.get("ready_for_studio_publish"),
        )
        privacy = st.selectbox("Privacy", ["private", "unlisted", "public"], index=0)

        if c4.button("Approve & publish to YouTube", type="primary"):
            try:
                render.metadata_payload = meta
                if episode.status != "approved":
                    approve_render(session, episode, render)
                job = schedule_or_publish(
                    session,
                    episode,
                    render,
                    privacy_status=privacy,
                    force_mock=force_mock,
                )
                st.success(f"Publish status={job.status} id={job.youtube_video_id}")
                if job.youtube_url:
                    st.write(job.youtube_url)
                if (job.api_response or {}).get("is_mock"):
                    st.info("This was a MOCK publish — no real YouTube upload.")
                st.rerun()
            except (ReviewError, PublishError) as exc:
                st.error(str(exc))

        schedule_date = st.text_input(
            "Optional schedule UTC ISO (Approve & schedule)",
            value="",
            placeholder="2026-11-10T15:00:00+00:00",
        )
        if st.button("Approve & schedule"):
            try:
                render.metadata_payload = meta
                if episode.status != "approved":
                    approve_render(session, episode, render)
                when = datetime.fromisoformat(schedule_date) if schedule_date else datetime.now(timezone.utc)
                job = schedule_or_publish(
                    session,
                    episode,
                    render,
                    scheduled_at=when,
                    privacy_status=privacy,
                    force_mock=force_mock,
                )
                st.success(f"Scheduled/publish job {job.status}")
            except Exception as exc:
                st.error(str(exc))
