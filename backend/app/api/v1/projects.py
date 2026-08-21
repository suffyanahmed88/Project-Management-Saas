import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectPublic, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("", response_model=list[ProjectPublic])
def list_projects(
    workspace_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProjectService(db).list_for_user(current_user.id, workspace_id)


@router.post("", response_model=ProjectPublic, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ProjectService(db).create(data, current_user.id)


@router.get("/{project_id}", response_model=ProjectPublic)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ProjectService(db).get(project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectPublic)
def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProjectService(db).update(project_id, data, current_user.id)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ProjectService(db).delete(project_id, current_user.id)
    return None
