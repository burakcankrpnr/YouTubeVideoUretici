"""Honest implementation status for Animation Studio features."""

from __future__ import annotations

from typing import Any

from app.studio.enums import ImplementationStatus as S

FEATURE_BACKLOG: list[dict[str, Any]] = [
    # P0
    {
        "id": "auth_settings",
        "priority": "P0",
        "title": "Owner settings / optional PIN",
        "status": S.PARTIAL.value,
        "notes": "Single-owner local app; optional PIN field in settings.",
    },
    {
        "id": "channel_onboarding",
        "priority": "P0",
        "title": "Channel onboarding wizard",
        "status": S.PARTIAL.value,
        "notes": "Wizard UI + DB; YouTube OAuth requires credentials.",
    },
    {
        "id": "series_bible",
        "priority": "P0",
        "title": "Series Bible + continuity memory",
        "status": S.COMPLETE.value,
        "notes": "Versioned bible CRUD and continuity checks.",
    },
    {
        "id": "character_design",
        "priority": "P0",
        "title": "Character Design Studio",
        "status": S.COMPLETE.value,
        "notes": "Design versions, approve/reject, new-character detection.",
    },
    {
        "id": "story_pipeline",
        "priority": "P0",
        "title": "Idea/script/continuity/safety pipeline",
        "status": S.COMPLETE.value,
        "notes": "Agents with mock/LLM providers; editable outputs.",
    },
    {
        "id": "storyboard_gate",
        "priority": "P0",
        "title": "Storyboard preview + approval gate",
        "status": S.COMPLETE.value,
        "notes": "Animation blocked until storyboard approved.",
    },
    {
        "id": "production_queue",
        "priority": "P0",
        "title": "Durable production queue",
        "status": S.COMPLETE.value,
        "notes": "Jobs with idempotency, pause/resume/retry.",
    },
    {
        "id": "cost_budget",
        "priority": "P0",
        "title": "Cost estimates and budget hard limits",
        "status": S.COMPLETE.value,
        "notes": "Unknown prices labeled; hard stops enforced.",
    },
    {
        "id": "owner_review",
        "priority": "P0",
        "title": "Owner review workspace + versioned approval",
        "status": S.COMPLETE.value,
        "notes": "Checksum-bound approval; revision feedback.",
    },
    {
        "id": "youtube_publish",
        "priority": "P0",
        "title": "YouTube upload/schedule gate",
        "status": S.COMPLETE.value,
        "notes": "Owner gate + Upload-Post YouTube via MPT settings; mock only when forced/unconfigured.",
    },
    {
        "id": "mpt_bridge",
        "priority": "P0",
        "title": "MoneyPrinterTurbo production bridge",
        "status": S.COMPLETE.value,
        "notes": "Studio calls task.start for real MP4 after storyboard approval.",
    },
    {
        "id": "automation_controls",
        "priority": "P0",
        "title": "Manual/Assisted/Autonomous + global pause",
        "status": S.COMPLETE.value,
        "notes": "Auto-publish off by default; requires explicit opt-in.",
    },
    {
        "id": "longform_shorts",
        "priority": "P0",
        "title": "Long-form and Shorts formats",
        "status": S.COMPLETE.value,
        "notes": "Format config and separate queue tagging.",
    },
    # P1
    {
        "id": "localization",
        "priority": "P1",
        "title": "Localization workflow",
        "status": S.PARTIAL.value,
        "notes": "LocalizedEpisode model + basic adapt job; native review later.",
    },
    {
        "id": "analytics",
        "priority": "P1",
        "title": "YouTube analytics snapshots",
        "status": S.PARTIAL.value,
        "notes": "Mock snapshots + recommendation scaffold; real API when OAuth ready.",
    },
    {
        "id": "rights_ledger",
        "priority": "P1",
        "title": "Rights ledger / production evidence",
        "status": S.PARTIAL.value,
        "notes": "Asset.rights fields + audit trail.",
    },
    # P2
    {
        "id": "experiments",
        "priority": "P2",
        "title": "Governed experiments",
        "status": S.NOT_STARTED.value,
        "notes": "Backlog only.",
    },
    {
        "id": "advanced_consistency",
        "priority": "P2",
        "title": "Advanced scene/character consistency checks",
        "status": S.NOT_STARTED.value,
        "notes": "Provider-dependent; flagged as limitation.",
    },
]


def feature_status_map() -> dict[str, str]:
    return {item["id"]: item["status"] for item in FEATURE_BACKLOG}


def features_by_priority(priority: str) -> list[dict[str, Any]]:
    return [item for item in FEATURE_BACKLOG if item["priority"] == priority]
