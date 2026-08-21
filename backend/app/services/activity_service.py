import uuid

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityAction
from app.repositories.activity_repo import ActivityRepository


class ActivityService:
    def __init__(self, db: Session):
        self.repo = ActivityRepository(db)

    def log(
        self,
        workspace_id: uuid.UUID,
        actor_id: uuid.UUID,
        action: ActivityAction,
        summary: str,
        project_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
    ):
        return self.repo.create(workspace_id, actor_id, action, summary, project_id, task_id)

    def list_for_user_workspaces(self, workspace_ids: list[uuid.UUID], limit: int = 50):
        return self.repo.list_for_workspaces(workspace_ids, limit)
