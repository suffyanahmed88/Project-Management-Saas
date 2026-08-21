import uuid

from sqlalchemy.orm import Session, joinedload

from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole


class WorkspaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, slug: str, owner_id: uuid.UUID) -> Workspace:
        workspace = Workspace(name=name, slug=slug)
        self.db.add(workspace)
        self.db.flush()
        member = WorkspaceMember(
            workspace_id=workspace.id, user_id=owner_id, role=WorkspaceRole.OWNER
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def get_by_id(self, workspace_id: uuid.UUID) -> Workspace | None:
        return self.db.get(Workspace, workspace_id)

    def list_for_user(self, user_id: uuid.UUID) -> list[Workspace]:
        return (
            self.db.query(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .filter(WorkspaceMember.user_id == user_id)
            .all()
        )

    def get_membership(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> WorkspaceMember | None:
        return (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .first()
        )

    def list_members(self, workspace_id: uuid.UUID) -> list[WorkspaceMember]:
        return (
            self.db.query(WorkspaceMember)
            .options(joinedload(WorkspaceMember.user))
            .filter(WorkspaceMember.workspace_id == workspace_id)
            .all()
        )

    def add_member(self, workspace_id: uuid.UUID, user_id: uuid.UUID, role: WorkspaceRole) -> WorkspaceMember:
        member = WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role)
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def slug_exists(self, slug: str) -> bool:
        return self.db.query(Workspace).filter(Workspace.slug == slug).first() is not None
