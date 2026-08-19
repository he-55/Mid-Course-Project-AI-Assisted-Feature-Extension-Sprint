# Architecture Critique & Plan: Task Comments Extension

## Overview
Proposal to implement a commenting feature for tasks.

## Proposed Data Models

```python
class CommentCreate(BaseModel):
    author: str = Field(..., min_length=1, max_length=50)
    text: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: int
    task_id: int
    author: str
    text: str
    created_at: str
```

## Endpoints & Routes

* `POST /api/tasks/{task_id}/comments`: Post a comment to a task.
* `GET /api/tasks/{task_id}/comments`: List comments associated with a task.

## Implementation Considerations

1. **In-Memory Store**: Maintain comments in a dictionary mapping task IDs to comment lists (`_comments: dict[int, list[dict]]`).
2. **Cascade Cleanup**: Purge corresponding task comments upon task deletion (`DELETE /api/tasks/{task_id}`).
3. **Test Reset Integration**: Extend `reset_store()` to clear both `_tasks` and `_comments`.
