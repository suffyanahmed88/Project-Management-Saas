import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project, ProjectMember
from app.models.task import Task, TaskStatus


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Project:
        project = Project(**kwargs)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        return (
            self.db.query(Project)
            .options(joinedload(Project.members).joinedload(ProjectMember.user))
            .filter(Project.id == project_id)
            .first()
        )

    def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Project]:
        return (
            self.db.query(Project)
            .options(joinedload(Project.members).joinedload(ProjectMember.user))
            .filter(Project.workspace_id == workspace_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    def list_for_user_workspaces(self, workspace_ids: list[uuid.UUID]) -> list[Project]:
        if not workspace_ids:
            return []
        return (
            self.db.query(Project)
            .options(joinedload(Project.members).joinedload(ProjectMember.user))
            .filter(Project.workspace_id.in_(workspace_ids))
            .order_by(Project.created_at.desc())
            .all()
        )

    def update(self, project: Project, **kwargs) -> Project:
        for key, value in kwargs.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()

    def set_members(self, project: Project, user_ids: list[uuid.UUID]) -> None:
        self.db.query(ProjectMember).filter(ProjectMember.project_id == project.id).delete()
        for uid in user_ids:
            self.db.add(ProjectMember(project_id=project.id, user_id=uid))
        self.db.commit()

    def task_counts(self, project_ids: list[uuid.UUID]) -> dict:
        if not project_ids:
            return {}
        rows = (
            self.db.query(Task.project_id, Task.status, func.count(Task.id))
            .filter(Task.project_id.in_(project_ids))
            .group_by(Task.project_id, Task.status)
            .all()
        )
        counts: dict = {}
        for pid, status, count in rows:
            counts.setdefault(pid, {"total": 0, "done": 0})
            counts[pid]["total"] += count
            if status == TaskStatus.DONE:
                counts[pid]["done"] += count
        return counts
