import uuid

from sqlalchemy.orm import Session

from app.repositories.activity_repo import ActivityRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository
from app.schemas.analytics import AnalyticsResponse, StatusBreakdown
from app.services.workspace_service import WorkspaceService


class AnalyticsService:
    def __init__(self, db: Session):
        self.projects = ProjectRepository(db)
        self.tasks = TaskRepository(db)
        self.activities = ActivityRepository(db)
        self.workspaces = WorkspaceService(db)

    def get_dashboard(self, user_id: uuid.UUID) -> AnalyticsResponse:
        ws_ids = self.workspaces.member_workspace_ids(user_id)
        projects = self.projects.list_for_user_workspaces(ws_ids)
        stats = self.tasks.dashboard_stats(ws_ids)
        activity = self.activities.list_for_workspaces(ws_ids, limit=15)
        return AnalyticsResponse(
            total_projects=len(projects),
            open_tasks=stats["open_tasks"],
            completed_tasks=stats["completed_tasks"],
            overdue_tasks=stats["overdue_tasks"],
            status_breakdown=[StatusBreakdown(**s) for s in stats["status_breakdown"]],
            recent_activity=activity,
        )
