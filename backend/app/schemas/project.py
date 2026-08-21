import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.project import ProjectStatus
from app.schemas.user import UserPublic


class ProjectCreate(BaseModel):
    workspace_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    color: str = "#6366f1"
    member_ids: list[uuid.UUID] = []


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    color: str | None = None
    member_ids: list[uuid.UUID] | None = None


class ProjectPublic(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str | None
    status: ProjectStatus
    color: str
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    completed_task_count: int = 0
    progress: float = 0.0
    members: list[UserPublic] = []

    model_config = {"from_attributes": True}
