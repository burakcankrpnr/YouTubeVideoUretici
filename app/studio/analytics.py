"""Channel analytics snapshots and explainable recommendations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.studio.models import AnalyticsSnapshot, Channel, Episode
from app.studio.workflow import write_audit


def refresh_analytics(session: Session, channel: Channel, *, use_mock: bool = True) -> AnalyticsSnapshot:
    """Pull analytics when authorized; otherwise create a clearly labeled mock snapshot."""
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=28)
    published = (
        session.query(Episode)
        .filter(Episode.channel_id == channel.id, Episode.status == "published")
        .count()
    )
    if use_mock or not channel.oauth_connected:
        metrics = {
            "views": None,
            "watch_time_hours": None,
            "average_view_duration_sec": None,
            "impressions": None,
            "ctr": None,
            "subscribers_gained": None,
            "published_episodes_tracked": published,
            "note": "Mock/unavailable analytics — connect YouTube OAuth for first-party data.",
        }
        recommendations = [
            {
                "action": "Keep 2–3 quality long-form uploads/week while measuring retention.",
                "evidence": "Insufficient first-party sample; starting hypothesis only.",
                "confidence": "low",
                "requires_owner_approval": True,
            },
            {
                "action": f"Confirm age band remains {channel.age_band} based on content strategy.",
                "evidence": "No private audience demographics available without Analytics API.",
                "confidence": "low",
                "requires_owner_approval": True,
            },
        ]
        source = "mock"
        sample_size = 0
    else:
        # Real Analytics API integration requires OAuth scopes; do not invent numbers.
        metrics = {
            "note": "OAuth connected but Analytics API fetch not configured in this build.",
            "published_episodes_tracked": published,
        }
        recommendations = []
        source = "youtube_oauth_pending_analytics"
        sample_size = 0

    snap = AnalyticsSnapshot(
        channel_id=channel.id,
        period_start=period_start,
        period_end=now,
        metrics=metrics,
        recommendations=recommendations,
        source=source,
        sample_size=sample_size,
    )
    session.add(snap)
    write_audit(
        session,
        action="analytics.refreshed",
        entity_type="channel",
        entity_id=channel.id,
        details={"source": source, "sample_size": sample_size},
        actor="system",
    )
    return snap


def latest_snapshot(session: Session, channel_id: str) -> AnalyticsSnapshot | None:
    return (
        session.query(AnalyticsSnapshot)
        .filter(AnalyticsSnapshot.channel_id == channel_id)
        .order_by(AnalyticsSnapshot.created_at.desc())
        .first()
    )
