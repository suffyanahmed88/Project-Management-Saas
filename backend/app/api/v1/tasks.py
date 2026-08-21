import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.task import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.task import TaskCreate, TaskMove, TaskPublic, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
def list_tasks(
    project_id: uuid.UUID | None = None,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: uuid.UUID | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = TaskService(db).list_filtered(
        current_user.id, project_id, status, priority, assignee_id, search, page, page_size
    )
    return PaginatedResponse(
        items=[i.model_dump(mode="json") for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size else 0,
    )


@router.post("", response_model=TaskPublic, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService(db).create(data, current_user.id)


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(task_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService(db).get(task_id, current_user.id)


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: uuid.UUID, data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return TaskService(db).update(task_id, data, current_user.id)


@router.post("/{task_id}/move", response_model=TaskPublic)
def move_task(
    task_id: uuid.UUID, data: TaskMove, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return TaskService(db).move(task_id, data, current_user.id)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    TaskService(db).delete(task_id, current_user.id)
    return None
