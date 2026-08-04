"""Pydantic v2 schemas for the Kanban task tracker."""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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


class TaskUpdate(BaseModel):
    """Payload for updating a task. All fields optional (partial update).

    ``due_date`` distinguishes "not sent" from an explicit ``null`` (which
    clears the date) via ``model_fields_set`` in the route handler.
    """

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    """Task as returned by the API. ``due_date`` serializes as ISO 8601 (YYYY-MM-DD)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_date: Optional[date] = None
