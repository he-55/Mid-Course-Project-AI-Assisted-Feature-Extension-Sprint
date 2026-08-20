"""Pydantic v2 schemas for the Kanban task tracker."""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_TAGS_PER_TASK = 10
TAG_MAX_LENGTH = 30


def normalize_tags(tags: list[str]) -> list[str]:
    """Trim, lowercase, and de-duplicate tags (order-preserving).

    Raises ValueError (surfaced as HTTP 422) for empty tags, tags over
    TAG_MAX_LENGTH characters, or more than MAX_TAGS_PER_TASK tags.
    """
    normalized: list[str] = []
    for raw in tags:
        tag = raw.strip().lower()
        if not tag:
            raise ValueError("tags must not be empty or whitespace-only")
        if len(tag) > TAG_MAX_LENGTH:
            raise ValueError(f"tags must be at most {TAG_MAX_LENGTH} characters")
        if tag not in normalized:
            normalized.append(tag)
    if len(normalized) > MAX_TAGS_PER_TASK:
        raise ValueError(f"a task can have at most {MAX_TAGS_PER_TASK} tags")
    return normalized


class TaskStatus(str, Enum):
    """Kanban columns. Flow is strictly unidirectional: TODO -> IN_PROGRESS -> DONE."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


# Rank used to enforce the unidirectional flow: a task may never move to a
# column with a lower rank than its current one.
STATUS_ORDER: dict[TaskStatus, int] = {
    TaskStatus.TODO: 0,
    TaskStatus.IN_PROGRESS: 1,
    TaskStatus.DONE: 2,
}


class DueFilter(str, Enum):
    """Timeline filters accepted by GET /api/tasks?due=..."""

    OVERDUE = "overdue"  # past due date and not DONE
    SOON = "soon"        # due today through the due-soon window, not DONE
    NONE = "none"        # no due date set


class TaskCreate(BaseModel):
    """Payload for creating a task. New tasks always start in TODO."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, value: list[str]) -> list[str]:
        return normalize_tags(value)


class TaskUpdate(BaseModel):
    """Payload for updating a task. All fields optional (partial update).

    ``due_date`` distinguishes "not sent" from an explicit ``null`` (which
    clears the date) via ``model_fields_set`` in the route handler.
    """

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None
    # None = leave tags untouched; a list (including []) replaces them wholesale.
    tags: Optional[list[str]] = None

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        return None if value is None else normalize_tags(value)


class TaskResponse(BaseModel):
    """Task as returned by the API. ``due_date`` serializes as ISO 8601 (YYYY-MM-DD)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
