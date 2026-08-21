import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentPublic
from app.services.comment_service import CommentService

router = APIRouter()


@router.get("/{task_id}/comments", response_model=list[CommentPublic])
def list_comments(task_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CommentService(db).list_for_task(task_id, current_user.id)


@router.post("/{task_id}/comments", response_model=CommentPublic, status_code=201)
def create_comment(
    task_id: uuid.UUID,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommentService(db).create(task_id, data.body, current_user.id)
