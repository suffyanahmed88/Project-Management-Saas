import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class CommentPublic(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    author: UserPublic
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
