from sqlalchemy.orm import Session

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.user import TokenResponse, UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: UserRegister) -> TokenResponse:
        if self.users.get_by_email(data.email):
            raise ConflictError("An account with this email already exists")
        user = self.users.create(data.email, data.name, hash_password(data.password))
        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=user)

    def login(self, data: UserLogin) -> TokenResponse:
        user = self.users.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=user)
