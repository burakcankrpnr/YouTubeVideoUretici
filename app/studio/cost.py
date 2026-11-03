"""Cost estimates, budget hard limits, and ledger."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.studio.models import BudgetLedger, Channel, Episode
from app.studio.workflow import write_audit


# Explicit estimate table — unknown stages stay None (never fabricate).
STAGE_ESTIMATES_USD: dict[str, float | None] = {
    "script": 0.05,
    "continuity": 0.01,
    "safety": 0.01,
    "storyboard": 0.10,
    "visual": None,  # provider-dependent
    "voice": 0.20,
    "assembly": 0.00,
    "qc": 0.00,
    "thumbnail": 0.05,
    "metadata": 0.02,
    "localize": 0.15,
    "publish": 0.00,
}


class BudgetExceeded(Exception):
    def __init__(self, message: str, details: dict[str, Any]):
        super().__init__(message)
        self.details = details


def estimate_episode_cost(content_format: str = "long_form") -> dict[str, Any]:
    stages = dict(STAGE_ESTIMATES_USD)
    if content_format == "shorts":
        stages["visual"] = 0.50  # shorter mock default when using mock video
        stages["voice"] = 0.08
    known = {k: v for k, v in stages.items() if v is not None}
    unknown = [k for k, v in stages.items() if v is None]
    total_known = sum(known.values())
    return {
        "currency": "USD",
        "breakdown": stages,
        "known_total": round(total_known, 4),
        "unknown_stages": unknown,
        "label": "estimate",
        "disclaimer": "Estimates only. Unknown provider prices are not invented.",
    }


def record_ledger(
    session: Session,
    *,
    amount: float,
    category: str,
    channel_id: str | None = None,
    episode_id: str | None = None,
    job_id: str | None = None,
    estimated: bool = False,
    note: str = "",
) -> BudgetLedger:
    entry = BudgetLedger(
        channel_id=channel_id,
        episode_id=episode_id,
        job_id=job_id,
        amount=amount,
        category=category,
        estimated=estimated,
        note=note,
    )
    session.add(entry)
    return entry


def channel_spend(
    session: Session, channel_id: str, *, since: datetime | None = None
) -> float:
    q = session.query(func.coalesce(func.sum(BudgetLedger.amount), 0.0)).filter(
        BudgetLedger.channel_id == channel_id,
        BudgetLedger.estimated.is_(False),
    )
    if since is not None:
        q = q.filter(BudgetLedger.created_at >= since)
    return float(q.scalar() or 0.0)


def assert_budget_allows(
    session: Session,
    episode: Episode,
    estimate: dict[str, Any] | None = None,
    *,
    force: bool = False,
) -> dict[str, Any]:
    estimate = estimate or estimate_episode_cost(episode.content_format)
    episode.cost_estimate = estimate.get("known_total")
    episode.cost_breakdown = estimate
    if force:
        return {"allowed": True, "forced": True, "estimate": estimate}

    channel = session.get(Channel, episode.channel_id) if episode.channel_id else None
    warnings: list[str] = []
    blockers: list[str] = []

    if channel and channel.budget_per_episode is not None:
        known = float(estimate.get("known_total") or 0)
        if known > channel.budget_per_episode:
            blockers.append(
                f"Estimated known cost {known} exceeds per-episode cap {channel.budget_per_episode}"
            )
        if estimate.get("unknown_stages"):
            warnings.append(
                "Some stages have unknown cost; confirm before expensive production."
            )

    if channel and channel.budget_monthly is not None:
        month_start = datetime.now(timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        spent = channel_spend(session, channel.id, since=month_start)
        projected = spent + float(estimate.get("known_total") or 0)
        if projected > channel.budget_monthly:
            blockers.append(
                f"Monthly spend {spent} + estimate would exceed cap {channel.budget_monthly}"
            )

    result = {
        "allowed": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "estimate": estimate,
    }
    write_audit(
        session,
        action="budget.checked",
        entity_type="episode",
        entity_id=episode.id,
        details=result,
        actor="system",
    )
    if blockers:
        raise BudgetExceeded("; ".join(blockers), result)
    return result
