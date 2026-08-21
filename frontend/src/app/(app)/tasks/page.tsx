"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ListChecks } from "lucide-react";
import { api } from "@/lib/api";
import type { PaginatedResponse, Task, TaskStatus } from "@/lib/types";
import { PRIORITY_CONFIG, STATUS_CONFIG, TASK_STATUSES } from "@/lib/constants";
import { cn, formatDate, isOverdue } from "@/lib/utils";
import { UserAvatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { TaskDetailDialog } from "@/components/tasks/task-detail-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function TasksPage() {
  const [status, setStatus] = useState<string>("ALL");
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["tasks", "all", status],
    queryFn: () =>
      api.get<PaginatedResponse<Task>>(
        `/tasks?page_size=100${status !== "ALL" ? `&status=${status}` : ""}`
      ),
  });

  const tasks = data?.items || [];

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">My Tasks</h1>
          <p className="text-sm text-muted-foreground">Every task across your workspace.</p>
        </div>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All statuses</SelectItem>
            {TASK_STATUSES.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-lg" />
          ))}
        </div>
      ) : tasks.length === 0 ? (
        <EmptyState icon={ListChecks} title="No tasks found" description="Try a different filter or create a new task in a project." />
      ) : (
        <div className="overflow-hidden rounded-xl border border-border">
          {tasks.map((task, i) => {
            const overdue = isOverdue(task.due_date, task.status);
            return (
              <button
                key={task.id}
                onClick={() => setSelectedTask(task)}
                className={cn(
                  "flex w-full items-center gap-3 px-4 py-3 text-left text-sm transition-colors hover:bg-accent",
                  i !== 0 && "border-t border-border"
                )}
              >
                <span className={cn("h-2 w-2 shrink-0 rounded-full", STATUS_CONFIG[task.status as TaskStatus].dotClassName)} />
                <span className="flex-1 truncate font-medium">{task.title}</span>
                {task.labels.slice(0, 2).map((l) => (
                  <Badge key={l} variant="outline" className="hidden sm:inline-flex">
                    {l}
                  </Badge>
                ))}
                <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-medium", PRIORITY_CONFIG[task.priority].className)}>
                  {PRIORITY_CONFIG[task.priority].label}
                </span>
                {task.due_date && (
                  <span className={cn("hidden text-xs text-muted-foreground sm:inline", overdue && "text-destructive")}>
                    {formatDate(task.due_date)}
                  </span>
                )}
                {task.assignee ? (
                  <UserAvatar name={task.assignee.name} color={task.assignee.avatar_color} size="sm" />
                ) : (
                  <span className="h-6 w-6" />
                )}
              </button>
            );
          })}
        </div>
      )}

      <TaskDetailDialog task={selectedTask} open={!!selectedTask} onOpenChange={(open) => !open && setSelectedTask(null)} />
    </div>
  );
}
