"""Studio status enums and allowed workflow transitions."""

from __future__ import annotations

from enum import Enum


class AutomationMode(str, Enum):
    MANUAL = "manual"
    ASSISTED = "assisted"
    AUTONOMOUS = "autonomous"


class ContentFormat(str, Enum):
    LONG_FORM = "long_form"
    SHORTS = "shorts"


class EpisodeStatus(str, Enum):
    DRAFT = "draft"
    IDEA = "idea"
    SCRIPTING = "scripting"
    SCRIPT_READY = "script_ready"
    CONTINUITY_CHECK = "continuity_check"
    SAFETY_CHECK = "safety_check"
    STORYBOARD_PENDING = "storyboard_pending"
    STORYBOARD_READY = "storyboard_ready"
    STORYBOARD_APPROVED = "storyboard_approved"
    QUEUED = "queued"
    PRODUCING = "producing"
    QC_PENDING = "qc_pending"
    REVIEW_READY = "review_ready"
    REVISION_REQUESTED = "revision_requested"
    REVISING = "revising"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class JobStage(str, Enum):
    PLAN = "plan"
    STORY = "story"
    SCRIPT = "script"
    CONTINUITY = "continuity"
    SAFETY = "safety"
    STORYBOARD = "storyboard"
    VISUAL = "visual"
    VOICE = "voice"
    ASSEMBLY = "assembly"
    QC = "qc"
    THUMBNAIL = "thumbnail"
    METADATA = "metadata"
    LOCALIZE = "localize"
    PUBLISH = "publish"
    ANALYTICS = "analytics"
    REVISION = "revision"


class ApprovalScope(str, Enum):
    STORYBOARD = "storyboard"
    CHARACTER_DESIGN = "character_design"
    FINAL_RENDER = "final_render"
    METADATA = "metadata"
    PUBLICATION = "publication"


class CharacterDesignStatus(str, Enum):
    DRAFT = "draft"
    NEEDS_REVISION = "needs_revision"
    APPROVED = "approved"
    ARCHIVED = "archived"


class ImplementationStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PARTIAL = "partial"
    COMPLETE = "complete"
    BLOCKED = "blocked"


# Explicit episode status transitions (§28.8). Workers and UI must use this map.
ALLOWED_EPISODE_TRANSITIONS: dict[EpisodeStatus, set[EpisodeStatus]] = {
    EpisodeStatus.DRAFT: {
        EpisodeStatus.IDEA,
        EpisodeStatus.SCRIPTING,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.IDEA: {
        EpisodeStatus.SCRIPTING,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.SCRIPTING: {
        EpisodeStatus.SCRIPT_READY,
        EpisodeStatus.FAILED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.SCRIPT_READY: {
        EpisodeStatus.CONTINUITY_CHECK,
        EpisodeStatus.SCRIPTING,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.CONTINUITY_CHECK: {
        EpisodeStatus.SAFETY_CHECK,
        EpisodeStatus.SCRIPTING,
        EpisodeStatus.BLOCKED,
        EpisodeStatus.FAILED,
    },
    EpisodeStatus.SAFETY_CHECK: {
        EpisodeStatus.STORYBOARD_PENDING,
        EpisodeStatus.SCRIPTING,
        EpisodeStatus.BLOCKED,
        EpisodeStatus.FAILED,
    },
    EpisodeStatus.STORYBOARD_PENDING: {
        EpisodeStatus.STORYBOARD_READY,
        EpisodeStatus.FAILED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.STORYBOARD_READY: {
        EpisodeStatus.STORYBOARD_APPROVED,
        EpisodeStatus.STORYBOARD_PENDING,
        EpisodeStatus.REJECTED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.STORYBOARD_APPROVED: {
        EpisodeStatus.QUEUED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.QUEUED: {
        EpisodeStatus.PRODUCING,
        EpisodeStatus.CANCELLED,
        EpisodeStatus.FAILED,
        EpisodeStatus.BLOCKED,
    },
    EpisodeStatus.PRODUCING: {
        EpisodeStatus.QC_PENDING,
        EpisodeStatus.FAILED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.QC_PENDING: {
        EpisodeStatus.REVIEW_READY,
        EpisodeStatus.BLOCKED,
        EpisodeStatus.FAILED,
    },
    EpisodeStatus.REVIEW_READY: {
        EpisodeStatus.APPROVED,
        EpisodeStatus.REVISION_REQUESTED,
        EpisodeStatus.REJECTED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.REVISION_REQUESTED: {
        EpisodeStatus.REVISING,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.REVISING: {
        EpisodeStatus.QC_PENDING,
        EpisodeStatus.FAILED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.APPROVED: {
        EpisodeStatus.SCHEDULED,
        EpisodeStatus.PUBLISHING,
        EpisodeStatus.REVISION_REQUESTED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.SCHEDULED: {
        EpisodeStatus.PUBLISHING,
        EpisodeStatus.CANCELLED,
        EpisodeStatus.BLOCKED,
    },
    EpisodeStatus.PUBLISHING: {
        EpisodeStatus.PUBLISHED,
        EpisodeStatus.FAILED,
        EpisodeStatus.BLOCKED,
    },
    EpisodeStatus.PUBLISHED: set(),
    EpisodeStatus.REJECTED: {EpisodeStatus.CANCELLED},
    EpisodeStatus.BLOCKED: {
        EpisodeStatus.REVIEW_READY,
        EpisodeStatus.QUEUED,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.FAILED: {
        EpisodeStatus.QUEUED,
        EpisodeStatus.SCRIPTING,
        EpisodeStatus.CANCELLED,
    },
    EpisodeStatus.CANCELLED: set(),
}


def can_transition(current: EpisodeStatus | str, target: EpisodeStatus | str) -> bool:
    current_status = EpisodeStatus(current)
    target_status = EpisodeStatus(target)
    return target_status in ALLOWED_EPISODE_TRANSITIONS.get(current_status, set())
