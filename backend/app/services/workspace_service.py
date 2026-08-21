import re
import uuid

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.repositories.user_repo import UserRepository
from app.repositories.workspace_repo import WorkspaceRepository


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "workspace"


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WorkspaceRepository(db)
        self.users = UserRepository(db)

    def create(self, name: str, owner_id: uuid.UUID) -> Workspace:
        base_slug = slugify(name)
        slug = base_slug
        suffix = 1
        while self.repo.slug_exists(slug):
            suffix += 1
            slug = f"{base_slug}-{suffix}"
        return self.repo.create(name=name, slug=slug, owner_id=owner_id)

    def list_for_user(self, user_id: uuid.UUID) -> list[Workspace]:
        return self.repo.list_for_user(user_id)

    def require_membership(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> WorkspaceMember:
        member = self.repo.get_membership(workspace_id, user_id)
        if not member:
            raise ForbiddenError("You are not a member of this workspace")
        return member

    def require_role(self, workspace_id: uuid.UUID, user_id: uuid.UUID, roles: list[WorkspaceRole]) -> WorkspaceMember:
        member = self.require_membership(workspace_id, user_id)
        if member.role not in roles:
            raise ForbiddenError("You do not have permission to perform this action")
        return member

    def member_workspace_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        return [w.id for w in self.repo.list_for_user(user_id)]

    def list_members(self, workspace_id: uuid.UUID) -> list[WorkspaceMember]:
        return self.repo.list_members(workspace_id)

    def invite_member(self, workspace_id: uuid.UUID, email: str, role: WorkspaceRole) -> WorkspaceMember:
        user = self.users.get_by_email(email)
        if not user:
            raise NotFoundError("No user found with that email")
        existing = self.repo.get_membership(workspace_id, user.id)
        if existing:
            raise ForbiddenError("User is already a member of this workspace")
        return self.repo.add_member(workspace_id, user.id, role)
