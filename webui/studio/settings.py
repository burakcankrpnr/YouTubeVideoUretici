"""Studio settings and provider configuration visibility."""

from __future__ import annotations

import streamlit as st

from app.studio.db import get_session, studio_db_path
from app.studio.models import ProviderConfig, StudioSettings
from app.studio.providers import get_provider
from app.studio.workflow import write_audit


def render() -> None:
    st.subheader("Studio Settings")
    st.write(f"Database: `{studio_db_path()}`")

    with get_session() as session:
        settings = session.query(StudioSettings).first()
        if settings is None:
            settings = StudioSettings()
            session.add(settings)
            session.flush()

        settings.default_language = st.text_input("Default language", value=settings.default_language)
        settings.default_timezone = st.text_input("Owner timezone", value=settings.default_timezone)
        settings.default_age_band = st.text_input("Default age band", value=settings.default_age_band)
        settings.default_duration_min = st.number_input(
            "Default duration min (minutes)", value=int(settings.default_duration_min), min_value=1
        )
        settings.default_duration_max = st.number_input(
            "Default duration max (minutes)", value=int(settings.default_duration_max), min_value=1
        )
        pin = st.text_input("Optional owner PIN (stored hashed locally — demo plain hash)", type="password")
        if st.button("Save settings", type="primary"):
            if pin:
                import hashlib

                settings.owner_pin_hash = hashlib.sha256(pin.encode("utf-8")).hexdigest()
            write_audit(
                session,
                action="settings.updated",
                entity_type="studio_settings",
                entity_id=settings.id,
                details={"language": settings.default_language},
            )
            st.success("Saved")

        st.markdown("#### Providers")
        providers = session.query(ProviderConfig).order_by(ProviderConfig.category, ProviderConfig.priority).all()
        st.dataframe(
            [
                {
                    "category": p.category,
                    "provider": p.provider_id,
                    "enabled": p.enabled,
                    "is_mock": p.is_mock,
                    "priority": p.priority,
                }
                for p in providers
            ],
            use_container_width=True,
        )

        st.markdown("#### Runtime provider resolution")
        for category in ["text", "image", "video", "tts", "safety", "youtube", "assembly"]:
            provider = get_provider(category, prefer_real=True)
            label = "MOCK" if getattr(provider, "is_mock", False) else "REAL"
            st.write(f"- `{category}` → **{provider.name}** ({label})")

        st.markdown("#### Environment placeholders")
        st.code(
            "\n".join(
                [
                    "YOUTUBE_CLIENT_ID=",
                    "YOUTUBE_CLIENT_SECRET=",
                    "YOUTUBE_REDIRECT_URI=http://localhost:8501",
                    "STUDIO_DEFAULT_TIMEZONE=Europe/Istanbul",
                ]
            )
        )
