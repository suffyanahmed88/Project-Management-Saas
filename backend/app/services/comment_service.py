import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.activity_log import ActivityAction
from app.models.notification import NotificationType
from app.repositories.comment_repo import CommentRepository
from app.repositories.task_repo import TaskRepository
from app.services.activity_service import ActivityService
from app.services.notification_service import NotificationService
from app.services.workspace_service import WorkspaceService


class CommentService:
    def __init__(self, db: Session):
        self.repo = CommentRepository(db)
        self.tasks = TaskRepository(db)
        self.workspaces = WorkspaceService(db)
        self.activity = ActivityService(db)
        self.notifications = NotificationService(db)

    def create(self, task_id: uuid.UUID, body: str, user_id: uuid.UUID):
        task = self.tasks.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        self.workspaces.require_membership(task.workspace_id, user_id)
        comment = self.repo.create(task_id, user_id, body)
        self.activity.log(
            task.workspace_id, user_id, ActivityAction.COMMENT_ADDED,
            f"commented on \"{task.title}\"", project_id=task.project_id, task_id=task.id,
        )
        if task.assignee_id and task.assignee_id != user_id:
            self.notifications.notify(
                task.assignee_id, NotificationType.COMMENT_ADDED,
                f"New comment on \"{task.title}\"", task_id=task.id,
            )
        return comment

    def list_for_task(self, task_id: uuid.UUID, user_id: uuid.UUID):
        task = self.tasks.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        self.workspaces.require_membership(task.workspace_id, user_id)
        return self.repo.list_for_task(task_id)
