import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus
from app.schemas.user import UserPublic


class TaskCreate(BaseModel):
    project_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.BACKLOG
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: uuid.UUID | None = None
    due_date: date | None = None
    labels: list[str] = []


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: uuid.UUID | None = None
    due_date: date | None = None
    labels: list[str] | None = None
    position: int | None = None


class TaskMove(BaseModel):
    status: TaskStatus
    position: int


class TaskPublic(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee: UserPublic | None
    due_date: date | None
    labels: list[str]
    position: int
    created_at: datetime
    updated_at: datetime
    comment_count: int = 0

    model_config = {"from_attributes": True}
