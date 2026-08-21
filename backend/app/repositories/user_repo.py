import uuid

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, name: str, hashed_password: str) -> User:
        user = User(email=email, name=name, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def search(self, query: str, limit: int = 10) -> list[User]:
        like = f"%{query}%"
        return (
            self.db.query(User)
            .filter((User.name.ilike(like)) | (User.email.ilike(like)))
            .limit(limit)
            .all()
        )
