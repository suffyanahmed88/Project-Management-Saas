import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.activity_log import ActivityAction
from app.schemas.user import UserPublic


class ActivityLogPublic(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID | None
    task_id: uuid.UUID | None
    actor: UserPublic
    action: ActivityAction
    summary: str
    created_at: datetime

    model_config = {"from_attributes": True}
