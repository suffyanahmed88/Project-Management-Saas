# Flow — Project Management SaaS

A modern, premium project management application in the style of Linear, Notion, and Vercel: workspaces, projects, a drag-and-drop Kanban board, task details with comments and activity, a live dashboard, global search (⌘K), and notifications — built as a full-stack, production-shaped MVP.

> Portfolio project. Not affiliated with Linear, Notion, or Vercel — their products just informed the visual language.

## Features

- **Authentication** — email/password registration and login, bcrypt password hashing, JWT bearer tokens, protected routes on both client and server.
- **Workspaces** — create workspaces, invite members by email, `OWNER` / `ADMIN` / `MEMBER` roles, strict workspace isolation (every resource lookup verifies membership server-side).
- **Projects** — create/edit/delete, status (`PLANNING → ACTIVE → ON_HOLD → COMPLETED → ARCHIVED`), computed progress, per-project member assignment.
- **Tasks** — title, description, status, priority, assignee, due date, labels; statuses flow `BACKLOG → TODO → IN_PROGRESS → DONE`; priorities `LOW / MEDIUM / HIGH / URGENT`.
- **Kanban board** — polished drag-and-drop (dnd-kit) with cross-column moves, in-column reordering, optimistic UI updates, and persisted positions — no page reloads.
- **Task details** — a side-by-side modal with editable description, status/priority/assignee/due-date/labels, threaded comments, and a per-task activity tab.
- **Dashboard** — total projects, open/completed/overdue tasks, a task-status donut chart, and a recent activity feed.
- **Global search** — `⌘K` / `Ctrl+K` command palette searching projects and tasks across the active workspace.
- **Notifications** — generated on task assignment and new comments, with a read/unread indicator.
- **Activity log** — every create/update/status-change/assignment/comment is recorded and rendered as a timeline.
- **Premium UI** — light/dark mode, collapsible sidebar, skeleton loaders, empty states, toasts, and a restrained, high-contrast visual system.

## Screenshots

> Run the app locally (see below) and drop screenshots here — `docs/dashboard.png`, `docs/kanban.png`, `docs/task-detail.png` — before publishing.

## Architecture

```mermaid
flowchart LR
    subgraph Client
        UI["Next.js 14 (App Router)\nTanStack Query + dnd-kit"]
    end

    subgraph Backend["FastAPI"]
        API["API layer\n(routers, auth, validation)"]
        SVC["Service layer\n(authorization, business rules)"]
        REPO["Repository layer\n(SQLAlchemy queries)"]
    end

    DB[(PostgreSQL)]
    REDIS[(Redis\noptional cache/rate-limit)]

    UI -- "REST /api/v1 (JWT)" --> API
    API --> SVC --> REPO --> DB
    SVC -.-> REDIS
```

Every request into the service layer resolves the caller's workspace membership from the database — the client-supplied `workspace_id` / `project_id` is never trusted for authorization, only used to look up the record whose membership is then checked server-side.

### Backend layering

```
routers (app/api/v1)      → HTTP concerns, request/response models
   ↓
services (app/services)   → authorization, orchestration, activity/notification side-effects
   ↓
repositories (app/repositories) → SQLAlchemy queries, no business logic
   ↓
PostgreSQL
```

## Tech stack

| Layer      | Choice |
|------------|--------|
| Frontend   | Next.js 14 (App Router) + TypeScript, Tailwind CSS, shadcn/ui-style components (Radix primitives), TanStack Query, dnd-kit, Recharts |
| Backend    | FastAPI, Python 3.12, Pydantic v2, SQLAlchemy 2.0, Alembic |
| Database   | PostgreSQL 16 |
| Cache      | Redis (wired for future rate-limiting/caching; not required for core features) |
| Auth       | JWT (HS256), bcrypt password hashing |
| Infra      | Docker Compose (postgres, redis, backend, frontend) |

## Getting started

### Option A — Docker Compose (recommended)

```bash
cp .env.example backend/.env
cp frontend/.env.example frontend/.env.local
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- API health check: http://localhost:8000/health

The backend container runs `alembic upgrade head` automatically on startup, so the schema is ready on first boot.

### Option B — Local development

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at your local Postgres
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

> The backend targets Python 3.12 (as pinned in `backend/Dockerfile`); some pinned dependency wheels are not yet published for newer interpreters, so local venvs should also use 3.12.

## API documentation

Interactive OpenAPI docs are served by FastAPI at `/docs` (Swagger UI) and `/redoc` once the backend is running.

| Method | Path                                  | Description                          |
|--------|---------------------------------------|---------------------------------------|
| POST   | `/api/v1/auth/register`               | Create an account, returns a JWT      |
| POST   | `/api/v1/auth/login`                  | Exchange credentials for a JWT        |
| GET    | `/api/v1/auth/me`                     | Current authenticated user            |
| GET    | `/api/v1/workspaces`                  | Workspaces the caller belongs to      |
| POST   | `/api/v1/workspaces`                  | Create a workspace (caller becomes OWNER) |
| GET    | `/api/v1/workspaces/{id}/members`     | List workspace members                |
| POST   | `/api/v1/workspaces/{id}/invite`      | Invite a user by email                |
| GET    | `/api/v1/projects`                    | List projects (optionally by workspace) |
| POST   | `/api/v1/projects`                    | Create a project                      |
| PATCH  | `/api/v1/projects/{id}`               | Update a project                      |
| DELETE | `/api/v1/projects/{id}`               | Delete a project                      |
| GET    | `/api/v1/tasks`                       | List/filter tasks (paginated)         |
| POST   | `/api/v1/tasks`                       | Create a task                         |
| PATCH  | `/api/v1/tasks/{id}`                  | Update task fields                    |
| POST   | `/api/v1/tasks/{id}/move`             | Move a task (Kanban drag-and-drop)    |
| DELETE | `/api/v1/tasks/{id}`                  | Delete a task                         |
| GET    | `/api/v1/tasks/{id}/comments`         | List comments on a task               |
| POST   | `/api/v1/tasks/{id}/comments`         | Add a comment                         |
| GET    | `/api/v1/notifications`               | List notifications for the caller     |
| POST   | `/api/v1/notifications/{id}/read`     | Mark a notification read              |
| GET    | `/api/v1/activity`                    | Workspace activity timeline           |
| GET    | `/api/v1/search`                      | Search projects and tasks             |
| GET    | `/api/v1/analytics`                   | Dashboard metrics                     |
| GET    | `/health`                              | Liveness check                        |

Errors are returned as a consistent JSON envelope:

```json
{ "error": { "code": "forbidden", "message": "You are not a member of this workspace" } }
```

## Testing

**Backend** — pytest, run against a real Postgres instance (matches production behavior for UUIDs, arrays, and enums):

```bash
docker compose up -d postgres
cd backend
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pmsaas_test pytest -v
```

Coverage includes: registration/login, workspace isolation (a user cannot see or act on another user's workspace, project, or task), project CRUD, task CRUD, Kanban status/position changes, and comment creation/authorization.

**Frontend** — type-checked build as a baseline correctness gate:

```bash
cd frontend
npm run build
```

## Design decisions

- **Service layer owns authorization.** Every service method re-derives the caller's workspace membership from the database before acting — route handlers never trust a `workspace_id`/`project_id` supplied by the client beyond using it to look up the record.
- **Repositories stay dumb.** They only translate between SQLAlchemy and plain Python; no authorization or business rules live there, so they're trivially testable and reusable.
- **Optimistic Kanban updates.** Drag-and-drop writes to the TanStack Query cache immediately and reconciles with the server response; a failed move rolls back and surfaces a toast rather than silently desyncing the board.
- **Monotonic tie-breakers on timestamps.** Comments and activity log entries carry a `seq` identity column in addition to `created_at`, because Postgres' `now()` is fixed for the lifetime of a transaction — relying on timestamps alone can produce ties under concurrent writes.
- **Hand-rolled shadcn-style primitives.** Rather than vendoring the shadcn CLI output wholesale, the UI primitives (button, dialog, select, dropdown, etc.) are minimal Radix wrappers styled with the same design tokens — same DX, smaller surface area to audit.

## Known limitations / future improvements

- Redis is wired into `docker-compose` but not yet used for caching or distributed rate limiting — `slowapi` is included as a dependency for adding per-route limits.
- Notifications are polled (30s interval) rather than pushed over WebSockets/SSE.
- No file/image attachments on tasks or comments.
- No email delivery for invitations (in-app membership add only — invited users must already have an account).
- Search is substring-based (`ILIKE`); a production system at scale would move to Postgres full-text search or an external index.
- E2E browser tests are not included; correctness is covered by backend pytest suites and a type-checked frontend production build.
