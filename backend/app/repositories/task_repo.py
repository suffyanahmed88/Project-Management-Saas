import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.comment import Comment
from app.models.task import Task, TaskPriority, TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Task:
        task = Task(**kwargs)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        return (
            self.db.query(Task)
            .options(joinedload(Task.assignee))
            .filter(Task.id == task_id)
            .first()
        )

    def list_for_project(self, project_id: uuid.UUID) -> list[Task]:
        return (
            self.db.query(Task)
            .options(joinedload(Task.assignee))
            .filter(Task.project_id == project_id)
            .order_by(Task.status, Task.position)
            .all()
        )

    def list_filtered(
        self,
        workspace_ids: list[uuid.UUID],
        project_id: uuid.UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: uuid.UUID | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Task], int]:
        query = self.db.query(Task).options(joinedload(Task.assignee)).filter(
            Task.workspace_id.in_(workspace_ids)
        )
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        if search:
            query = query.filter(Task.title.ilike(f"%{search}%"))
        total = query.count()
        items = (
            query.order_by(Task.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def update(self, task: Task, **kwargs) -> Task:
        for key, value in kwargs.items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def max_position(self, project_id: uuid.UUID, status: TaskStatus) -> int:
        result = self.db.query(func.max(Task.position)).filter(
            Task.project_id == project_id, Task.status == status
        ).scalar()
        return (result + 1) if result is not None else 0

    def comment_counts(self, task_ids: list[uuid.UUID]) -> dict:
        if not task_ids:
            return {}
        rows = (
            self.db.query(Comment.task_id, func.count(Comment.id))
            .filter(Comment.task_id.in_(task_ids))
            .group_by(Comment.task_id)
            .all()
        )
        return dict(rows)

    def dashboard_stats(self, workspace_ids: list[uuid.UUID]) -> dict:
        base = self.db.query(Task).filter(Task.workspace_id.in_(workspace_ids))
        open_tasks = base.filter(Task.status != TaskStatus.DONE).count()
        completed_tasks = base.filter(Task.status == TaskStatus.DONE).count()
        overdue_tasks = base.filter(
            Task.status != TaskStatus.DONE, Task.due_date != None, Task.due_date < date.today()
        ).count()
        rows = (
            self.db.query(Task.status, func.count(Task.id))
            .filter(Task.workspace_id.in_(workspace_ids))
            .group_by(Task.status)
            .all()
        )
        return {
            "open_tasks": open_tasks,
            "completed_tasks": completed_tasks,
            "overdue_tasks": overdue_tasks,
            "status_breakdown": [{"status": s.value, "count": c} for s, c in rows],
        }

    def search(self, workspace_ids: list[uuid.UUID], query: str, limit: int = 10) -> list[Task]:
        return (
            self.db.query(Task)
            .filter(Task.workspace_id.in_(workspace_ids), Task.title.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )
