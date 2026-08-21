export type WorkspaceRole = "OWNER" | "ADMIN" | "MEMBER";
export type ProjectStatus = "PLANNING" | "ACTIVE" | "ON_HOLD" | "COMPLETED" | "ARCHIVED";
export type TaskStatus = "BACKLOG" | "TODO" | "IN_PROGRESS" | "DONE";
export type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_color: string;
  created_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  my_role: WorkspaceRole | null;
}

export interface Project {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  color: string;
  created_at: string;
  updated_at: string;
  task_count: number;
  completed_task_count: number;
  progress: number;
  members: User[];
}

export interface Task {
  id: string;
  project_id: string;
  workspace_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee: User | null;
  due_date: string | null;
  labels: string[];
  position: number;
  created_at: string;
  updated_at: string;
  comment_count: number;
}

export interface Comment {
  id: string;
  task_id: string;
  author: User;
  body: string;
  created_at: string;
}

export interface Notification {
  id: string;
  type: "TASK_ASSIGNED" | "COMMENT_ADDED" | "MENTION";
  message: string;
  task_id: string | null;
  is_read: boolean;
  created_at: string;
}

export interface ActivityLog {
  id: string;
  project_id: string | null;
  task_id: string | null;
  actor: User;
  action: string;
  summary: string;
  created_at: string;
}

export interface AnalyticsResponse {
  total_projects: number;
  open_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  status_breakdown: { status: string; count: number }[];
  recent_activity: ActivityLog[];
}

export interface SearchResult {
  type: "project" | "task";
  id: string;
  title: string;
  subtitle: string | null;
  project_id: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
