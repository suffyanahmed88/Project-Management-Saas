import enum
import uuid

from sqlalchemy import BigInteger, Enum, ForeignKey, Identity, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import Timestamped, UUIDPk


class ActivityAction(str, enum.Enum):
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_STATUS_CHANGED = "TASK_STATUS_CHANGED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_DELETED = "TASK_DELETED"
    COMMENT_ADDED = "COMMENT_ADDED"
    PROJECT_CREATED = "PROJECT_CREATED"
    PROJECT_UPDATED = "PROJECT_UPDATED"


class ActivityLog(Base, UUIDPk, Timestamped):
    __tablename__ = "activity_logs"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action: Mapped[ActivityAction] = mapped_column(Enum(ActivityAction, name="activity_action"))
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    # Monotonic tie-breaker: see Comment.seq for why created_at alone is insufficient.
    seq: Mapped[int] = mapped_column(BigInteger, Identity(), unique=True)

    actor: Mapped["Base"] = relationship("User")
