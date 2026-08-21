import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.workspace import WorkspaceRole
from app.schemas.user import UserPublic


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class WorkspaceMemberPublic(BaseModel):
    id: uuid.UUID
    user: UserPublic
    role: WorkspaceRole

    model_config = {"from_attributes": True}


class WorkspacePublic(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
    my_role: WorkspaceRole | None = None

    model_config = {"from_attributes": True}


class WorkspaceInviteRequest(BaseModel):
    email: str
    role: WorkspaceRole = WorkspaceRole.MEMBER
