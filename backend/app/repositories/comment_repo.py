import uuid

from sqlalchemy.orm import Session, joinedload

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, task_id: uuid.UUID, author_id: uuid.UUID, body: str) -> Comment:
        comment = Comment(task_id=task_id, author_id=author_id, body=body)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_for_task(self, task_id: uuid.UUID) -> list[Comment]:
        return (
            self.db.query(Comment)
            .options(joinedload(Comment.author))
            .filter(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc(), Comment.seq.asc())
            .all()
        )
