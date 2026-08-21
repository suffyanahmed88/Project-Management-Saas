import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.activity_log import ActivityAction
from app.models.notification import NotificationType
from app.models.task import Task, TaskStatus
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository
from app.schemas.task import TaskCreate, TaskMove, TaskPublic, TaskUpdate
from app.services.activity_service import ActivityService
from app.services.notification_service import NotificationService
from app.services.workspace_service import WorkspaceService


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TaskRepository(db)
        self.projects = ProjectRepository(db)
        self.workspaces = WorkspaceService(db)
        self.activity = ActivityService(db)
        self.notifications = NotificationService(db)

    def _to_public(self, task: Task, comment_counts: dict | None = None) -> TaskPublic:
        counts = comment_counts or {}
        return TaskPublic(
            id=task.id,
            project_id=task.project_id,
            workspace_id=task.workspace_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assignee=task.assignee,
            due_date=task.due_date,
            labels=task.labels or [],
            position=task.position,
            created_at=task.created_at,
            updated_at=task.updated_at,
            comment_count=counts.get(task.id, 0),
        )

    def create(self, data: TaskCreate, user_id: uuid.UUID) -> TaskPublic:
        project = self.projects.get_by_id(data.project_id)
        if not project:
            raise NotFoundError("Project not found")
        self.workspaces.require_membership(project.workspace_id, user_id)
        position = self.repo.max_position(project.id, data.status)
        task = self.repo.create(
            project_id=project.id,
            workspace_id=project.workspace_id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            assignee_id=data.assignee_id,
            due_date=data.due_date,
            labels=data.labels,
            position=position,
            created_by=user_id,
        )
        self.activity.log(
            project.workspace_id, user_id, ActivityAction.TASK_CREATED,
            f"created task \"{task.title}\"", project_id=project.id, task_id=task.id,
        )
        if data.assignee_id and data.assignee_id != user_id:
            self.notifications.notify(
                data.assignee_id, NotificationType.TASK_ASSIGNED,
                f"You were assigned to \"{task.title}\"", task_id=task.id,
            )
        return self._to_public(task)

    def get(self, task_id: uuid.UUID, user_id: uuid.UUID) -> TaskPublic:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        self.workspaces.require_membership(task.workspace_id, user_id)
        counts = self.repo.comment_counts([task.id])
        return self._to_public(task, counts)

    def list_for_project(self, project_id: uuid.UUID, user_id: uuid.UUID) -> list[TaskPublic]:
        project = self.projects.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        self.workspaces.require_membership(project.workspace_id, user_id)
        tasks = self.repo.list_for_project(project_id)
        counts = self.repo.comment_counts([t.id for t in tasks])
        return [self._to_public(t, counts) for t in tasks]

    def list_filtered(
        self, user_id: uuid.UUID, project_id=None, status=None, priority=None,
        assignee_id=None, search=None, page: int = 1, page_size: int = 50,
    ):
        ws_ids = self.workspaces.member_workspace_ids(user_id)
        tasks, total = self.repo.list_filtered(
            ws_ids, project_id, status, priority, assignee_id, search, page, page_size
        )
        counts = self.repo.comment_counts([t.id for t in tasks])
        return [self._to_public(t, counts) for t in tasks], total

    def update(self, task_id: uuid.UUID, data: TaskUpdate, user_id: uuid.UUID) -> TaskPublic:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        self.workspaces.require_membership(task.workspace_id, user_id)
        update_data = data.model_dump(exclude_unset=True)
        old_status = task.status
        old_assignee = task.assignee_id
        new_assignee = update_data.get("assignee_id", old_assignee)
        task = self.repo.update(task, **update_data)

        if "status" in update_data and update_data["status"] != old_status:
            action = (
                ActivityAction.TASK_COMPLETED
                if update_data["status"] == TaskStatus.DONE
                else ActivityAction.TASK_STATUS_CHANGED
            )
            self.activity.log(
                task.workspace_id, user_id, action,
                f"moved \"{task.title}\" to {update_data['status'].value if hasattr(update_data['status'], 'value') else update_data['status']}",
                project_id=task.project_id, task_id=task.id,
            )
        elif update_data:
            self.activity.log(
                task.workspace_id, user_id, ActivityAction.TASK_UPDATED,
                f"updated task \"{task.title}\"", project_id=task.project_id, task_id=task.id,
            )

        if "assignee_id" in update_data and new_assignee and new_assignee != old_assignee and new_assignee != user_id:
            self.activity.log(
                task.workspace_id, user_id, ActivityAction.TASK_ASSIGNED,
                f"assigned \"{task.title}\"", project_id=task.project_id, task_id=task.id,
            )
            self.notifications.notify(
                new_assignee, NotificationType.TASK_ASSIGNED,
                f"You were assigned to \"{task.title}\"", task_id=task.id,
            )
        counts = self.repo.comment_counts([task.id])
        return self._to_public(task, counts)

    def move(self, task_id: uuid.UUID, data: TaskMove, user_id: uuid.UUID) -> TaskPublic:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        self.workspaces.require_membership(task.workspace_id, user_id)
        old_status = task.status
        task = self.repo.update(task, status=data.status, position=data.position)
        if data.status != old_status:
            self.activity.log(
                task.workspace_id, user_id, ActivityAction.TASK_STATUS_CHANGED,
                f"moved \"{task.title}\" to {data.status.value}",
                project_id=task.project_id, task_id=task.id,
            )
        counts = self.repo.comment_counts([task.id])
        return self._to_public(task, counts)

    def delete(self, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        self.workspaces.require_membership(task.workspace_id, user_id)
        self.activity.log(
            task.workspace_id, user_id, ActivityAction.TASK_DELETED,
            f"deleted task \"{task.title}\"", project_id=task.project_id,
        )
        self.repo.delete(task)

    def dashboard_stats(self, user_id: uuid.UUID) -> dict:
        ws_ids = self.workspaces.member_workspace_ids(user_id)
        return self.repo.dashboard_stats(ws_ids)
