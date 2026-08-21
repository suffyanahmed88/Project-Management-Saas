from pydantic import BaseModel

from app.schemas.activity import ActivityLogPublic


class StatusBreakdown(BaseModel):
    status: str
    count: int


class AnalyticsResponse(BaseModel):
    total_projects: int
    open_tasks: int
    completed_tasks: int
    overdue_tasks: int
    status_breakdown: list[StatusBreakdown]
    recent_activity: list[ActivityLogPublic]


class SearchResult(BaseModel):
    type: str
    id: str
    title: str
    subtitle: str | None = None
    project_id: str | None = None
