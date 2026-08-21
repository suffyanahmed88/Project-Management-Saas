import uuid

from sqlalchemy import BigInteger, ForeignKey, Identity, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import Timestamped, UUIDPk


class Comment(Base, UUIDPk, Timestamped):
    __tablename__ = "comments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # Monotonic tie-breaker: created_at alone can collide when multiple comments
    # are committed within the same DB transaction (e.g. in tests), since
    # Postgres' now() is fixed for the duration of a transaction.
    seq: Mapped[int] = mapped_column(BigInteger, Identity(), unique=True)

    author: Mapped["Base"] = relationship("User")
