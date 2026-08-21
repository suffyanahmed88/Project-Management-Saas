import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationPublic
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=list[NotificationPublic])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return NotificationService(db).list_for_user(current_user.id)


@router.post("/{notification_id}/read", response_model=NotificationPublic)
def mark_read(notification_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return NotificationService(db).mark_read(notification_id, current_user.id)
