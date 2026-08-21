import uuid

from sqlalchemy.orm import Session

from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository
from app.schemas.analytics import SearchResult
from app.services.workspace_service import WorkspaceService


class SearchService:
    def __init__(self, db: Session):
        self.projects = ProjectRepository(db)
        self.tasks = TaskRepository(db)
        self.workspaces = WorkspaceService(db)

    def search(self, query: str, user_id: uuid.UUID) -> list[SearchResult]:
        if not query or len(query.strip()) < 1:
            return []
        ws_ids = self.workspaces.member_workspace_ids(user_id)
        results: list[SearchResult] = []

        projects = self.projects.list_for_user_workspaces(ws_ids)
        for p in projects:
            if query.lower() in p.name.lower():
                results.append(
                    SearchResult(type="project", id=str(p.id), title=p.name, subtitle="Project")
                )

        tasks = self.tasks.search(ws_ids, query, limit=15)
        for t in tasks:
            results.append(
                SearchResult(
                    type="task", id=str(t.id), title=t.title,
                    subtitle=f"Task · {t.status.value}", project_id=str(t.project_id),
                )
            )
        return results[:20]
