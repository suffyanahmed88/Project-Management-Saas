import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.activity_log import ActivityAction
from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.repositories.workspace_repo import WorkspaceRepository
from app.schemas.project import ProjectCreate, ProjectPublic, ProjectUpdate
from app.services.activity_service import ActivityService
from app.services.workspace_service import WorkspaceService


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepository(db)
        self.workspaces = WorkspaceService(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.activity = ActivityService(db)

    def _to_public(self, project: Project, counts: dict) -> ProjectPublic:
        c = counts.get(project.id, {"total": 0, "done": 0})
        progress = (c["done"] / c["total"] * 100) if c["total"] else 0.0
        return ProjectPublic(
            id=project.id,
            workspace_id=project.workspace_id,
            name=project.name,
            description=project.description,
            status=project.status,
            color=project.color,
            created_at=project.created_at,
            updated_at=project.updated_at,
            task_count=c["total"],
            completed_task_count=c["done"],
            progress=round(progress, 1),
            members=[m.user for m in project.members],
        )

    def create(self, data: ProjectCreate, user_id: uuid.UUID) -> ProjectPublic:
        self.workspaces.require_membership(data.workspace_id, user_id)
        project = self.repo.create(
            workspace_id=data.workspace_id,
            name=data.name,
            description=data.description,
            color=data.color,
            created_by=user_id,
        )
        member_ids = set(data.member_ids) | {user_id}
        self.repo.set_members(project, list(member_ids))
        project = self.repo.get_by_id(project.id)
        self.activity.log(
            data.workspace_id, user_id, ActivityAction.PROJECT_CREATED,
            f"created project \"{project.name}\"", project_id=project.id,
        )
        return self._to_public(project, {})

    def get(self, project_id: uuid.UUID, user_id: uuid.UUID) -> ProjectPublic:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        self.workspaces.require_membership(project.workspace_id, user_id)
        counts = self.repo.task_counts([project.id])
        return self._to_public(project, counts)

    def list_for_user(self, user_id: uuid.UUID, workspace_id: uuid.UUID | None = None) -> list[ProjectPublic]:
        if workspace_id:
            self.workspaces.require_membership(workspace_id, user_id)
            projects = self.repo.list_for_workspace(workspace_id)
        else:
            ws_ids = self.workspaces.member_workspace_ids(user_id)
            projects = self.repo.list_for_user_workspaces(ws_ids)
        counts = self.repo.task_counts([p.id for p in projects])
        return [self._to_public(p, counts) for p in projects]

    def update(self, project_id: uuid.UUID, data: ProjectUpdate, user_id: uuid.UUID) -> ProjectPublic:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        self.workspaces.require_membership(project.workspace_id, user_id)
        update_data = data.model_dump(exclude_unset=True, exclude={"member_ids"})
        if update_data:
            project = self.repo.update(project, **update_data)
        if data.member_ids is not None:
            self.repo.set_members(project, list(set(data.member_ids) | {user_id}))
            project = self.repo.get_by_id(project.id)
        self.activity.log(
            project.workspace_id, user_id, ActivityAction.PROJECT_UPDATED,
            f"updated project \"{project.name}\"", project_id=project.id,
        )
        counts = self.repo.task_counts([project.id])
        return self._to_public(project, counts)

    def delete(self, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        self.workspaces.require_membership(project.workspace_id, user_id)
        self.repo.delete(project)
