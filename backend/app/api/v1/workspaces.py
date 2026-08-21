from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceInviteRequest,
    WorkspaceMemberPublic,
    WorkspacePublic,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter()


@router.get("", response_model=list[WorkspacePublic])
def list_workspaces(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = WorkspaceService(db)
    workspaces = service.list_for_user(current_user.id)
    result = []
    for w in workspaces:
        member = service.repo.get_membership(w.id, current_user.id)
        result.append(WorkspacePublic.model_validate(w).model_copy(update={"my_role": member.role if member else None}))
    return result


@router.post("", response_model=WorkspacePublic, status_code=201)
def create_workspace(data: WorkspaceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = WorkspaceService(db)
    from app.models.workspace import WorkspaceRole

    workspace = service.create(data.name, current_user.id)
    return WorkspacePublic.model_validate(workspace).model_copy(update={"my_role": WorkspaceRole.OWNER})


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberPublic])
def list_members(workspace_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = WorkspaceService(db)
    service.require_membership(workspace_id, current_user.id)
    return service.list_members(workspace_id)


@router.post("/{workspace_id}/invite", response_model=WorkspaceMemberPublic, status_code=201)
def invite_member(
    workspace_id: str,
    data: WorkspaceInviteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkspaceService(db)
    from app.models.workspace import WorkspaceRole

    service.require_role(workspace_id, current_user.id, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN])
    return service.invite_member(workspace_id, data.email, data.role)
