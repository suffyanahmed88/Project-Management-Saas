from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import SearchResult
from app.services.search_service import SearchService

router = APIRouter()


@router.get("", response_model=list[SearchResult])
def search(q: str = Query(default=""), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return SearchService(db).search(q, current_user.id)
