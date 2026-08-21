import uuid

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models.notification import NotificationType
from app.repositories.notification_repo import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def notify(self, user_id: uuid.UUID, type: NotificationType, message: str, task_id: uuid.UUID | None = None):
        return self.repo.create(user_id, type, message, task_id)

    def list_for_user(self, user_id: uuid.UUID):
        return self.repo.list_for_user(user_id)

    def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID):
        notification = self.repo.get_by_id(notification_id)
        if not notification:
            raise NotFoundError("Notification not found")
        if notification.user_id != user_id:
            raise ForbiddenError("Not authorized")
        return self.repo.mark_read(notification)
