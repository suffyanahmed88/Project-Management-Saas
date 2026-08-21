from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.activity import ActivityLogPublic
from app.services.activity_service import ActivityService
from app.services.workspace_service import WorkspaceService

router = APIRouter()


@router.get("", response_model=list[ActivityLogPublic])
def list_activity(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ws_ids = WorkspaceService(db).member_workspace_ids(current_user.id)
    return ActivityService(db).list_for_user_workspaces(ws_ids)
