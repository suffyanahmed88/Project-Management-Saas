import uuid

from sqlalchemy.orm import Session, joinedload

from app.models.activity_log import ActivityAction, ActivityLog


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        workspace_id: uuid.UUID,
        actor_id: uuid.UUID,
        action: ActivityAction,
        summary: str,
        project_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
    ) -> ActivityLog:
        log = ActivityLog(
            workspace_id=workspace_id,
            project_id=project_id,
            task_id=task_id,
            actor_id=actor_id,
            action=action,
            summary=summary,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_for_workspaces(self, workspace_ids: list[uuid.UUID], limit: int = 50) -> list[ActivityLog]:
        return (
            self.db.query(ActivityLog)
            .options(joinedload(ActivityLog.actor))
            .filter(ActivityLog.workspace_id.in_(workspace_ids))
            .order_by(ActivityLog.created_at.desc(), ActivityLog.seq.desc())
            .limit(limit)
            .all()
        )
