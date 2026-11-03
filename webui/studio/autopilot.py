"""One-click fully automatic studio operation."""

from __future__ import annotations

import streamlit as st

from app.studio.autonomous import run_autonomous_batch, run_daily_long_and_shorts
from app.studio.enums import ContentFormat
from app.studio.mpt_bridge import upload_post_youtube_status


def render() -> None:
    st.subheader("Autopilot — hands-off mode")
    st.markdown(
        """
**Target cadence:** every day **1 long YouTube video + 1 Shorts** (≈ 60 uploads / month).

AI fills idea → script → storyboard → MoneyPrinterTurbo render → publish.
"""
    )

    yt = upload_post_youtube_status()
    if yt.get("ready_for_studio_publish"):
        st.success(f"YouTube ready via Upload-Post ({yt.get('username')})")
    else:
        st.warning(
            "Upload-Post YouTube not configured yet — autopilot will still produce "
            "and use **mock publish** until API key/username/`youtube` platform are set."
        )

    st.info(
        "Cost ballpark (stock footage + Edge TTS + light LLM): roughly "
        "**$30–120 / month** for daily long+Shorts. "
        "Full AI-animation per scene can jump to **$500–2000+ / month**."
    )

    topic = st.text_input(
        "Optional topic hint (leave empty — AI chooses)",
        value="",
        placeholder="e.g. Pip finds a glowing leaf at dusk",
    )
    language = st.text_input("Language", value="en")
    allow_mock = st.checkbox(
        "Allow mock video if MPT cannot render (demo)",
        value=True,
    )

    st.error(
        "Autopilot enables **Autonomous + auto-publish** and sets weekly upload cap to 14 "
        "(daily long + Shorts)."
    )

    days = st.number_input("How many days to produce now", min_value=1, max_value=7, value=1)

    if st.button(
        "START DAILY PAIR — 1 Long + 1 Shorts",
        type="primary",
        use_container_width=True,
    ):
        logs: list[str] = []
        log_box = st.empty()

        def _log(message: str) -> None:
            logs.append(message)
            log_box.code("\n".join(logs[-50:]))

        try:
            with st.spinner("Producing daily long-form + Shorts…"):
                results = run_daily_long_and_shorts(
                    topic_hint=topic,
                    language=language or "en",
                    allow_mock_production=allow_mock,
                    days=int(days),
                    log=_log,
                )
            st.success(f"Finished {len(results)} items ({days} day pair(s))")
            for result in results:
                st.markdown(
                    f"### Day {result.get('day')} · {result.get('slot')} · {result.get('title')}"
                )
                st.write(
                    {
                        "status": result.get("status"),
                        "media_path": result.get("media_path"),
                        "youtube_url": result.get("youtube_url"),
                        "published_mock": result.get("published_mock"),
                    }
                )
                media = result.get("media_path") or ""
                if str(media).lower().endswith((".mp4", ".webm", ".mov")):
                    st.video(media)
        except Exception as exc:
            st.error(str(exc))
            if logs:
                st.code("\n".join(logs))

    with st.expander("Advanced: single-format batch"):
        count = st.number_input("Episodes", min_value=1, max_value=5, value=1, key="ap_count")
        fmt = st.selectbox(
            "Format",
            [ContentFormat.LONG_FORM.value, ContentFormat.SHORTS.value],
            format_func=lambda v: "Long-form" if v == "long_form" else "Shorts",
            key="ap_fmt",
        )
        if st.button("Run single-format batch"):
            logs2: list[str] = []
            box2 = st.empty()

            def _log2(message: str) -> None:
                logs2.append(message)
                box2.code("\n".join(logs2[-40:]))

            results = run_autonomous_batch(
                count=int(count),
                topic_hint=topic,
                content_format=fmt,
                language=language or "en",
                allow_mock_production=allow_mock,
                log=_log2,
            )
            st.success(f"Finished {len(results)} episode(s)")
