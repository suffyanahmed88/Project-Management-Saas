import type { TaskPriority, TaskStatus } from "./types";

export const TASK_STATUSES: { value: TaskStatus; label: string }[] = [
  { value: "BACKLOG", label: "Backlog" },
  { value: "TODO", label: "To Do" },
  { value: "IN_PROGRESS", label: "In Progress" },
  { value: "DONE", label: "Done" },
];

export const PRIORITY_CONFIG: Record<TaskPriority, { label: string; className: string }> = {
  LOW: { label: "Low", className: "bg-muted text-muted-foreground" },
  MEDIUM: { label: "Medium", className: "bg-blue-500/10 text-blue-600 dark:text-blue-400" },
  HIGH: { label: "High", className: "bg-amber-500/10 text-amber-600 dark:text-amber-400" },
  URGENT: { label: "Urgent", className: "bg-red-500/10 text-red-600 dark:text-red-400" },
};

export const STATUS_CONFIG: Record<TaskStatus, { label: string; dotClassName: string }> = {
  BACKLOG: { label: "Backlog", dotClassName: "bg-zinc-400" },
  TODO: { label: "To Do", dotClassName: "bg-blue-400" },
  IN_PROGRESS: { label: "In Progress", dotClassName: "bg-amber-400" },
  DONE: { label: "Done", dotClassName: "bg-emerald-500" },
};
