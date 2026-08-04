"""Pydantic v2 schemas for the Kanban task tracker."""

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


class TaskCreate(BaseModel):
    """Payload for creating a task. New tasks always start in TODO."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class TaskUpdate(BaseModel):
    """Payload for updating a task. All fields optional (partial update)."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    """Task as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
