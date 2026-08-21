import uuid

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, user_id: uuid.UUID, type: NotificationType, message: str, task_id: uuid.UUID | None = None
    ) -> Notification:
        notification = Notification(user_id=user_id, type=type, message=message, task_id=task_id)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_for_user(self, user_id: uuid.UUID, limit: int = 30) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        return self.db.get(Notification, notification_id)
