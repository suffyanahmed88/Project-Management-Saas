"use client";

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { MessageSquare, CalendarDays } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { UserAvatar } from "@/components/ui/avatar";
import { PRIORITY_CONFIG } from "@/lib/constants";
import { cn, formatDate, isOverdue } from "@/lib/utils";
import type { Task } from "@/lib/types";

export function TaskCard({ task, onClick }: { task: Task; onClick: () => void }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: task.id,
    data: { type: "task", status: task.status },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  const overdue = isOverdue(task.due_date, task.status);

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      onClick={onClick}
      className="group cursor-pointer rounded-lg border border-border bg-card p-3 shadow-sm transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-md"
    >
      <p className="text-sm font-medium leading-snug">{task.title}</p>

      {task.labels.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {task.labels.map((label) => (
            <Badge key={label} variant="outline" className="px-1.5 py-0 text-[10px]">
              {label}
            </Badge>
          ))}
        </div>
      )}

      <div className="mt-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-medium", PRIORITY_CONFIG[task.priority].className)}>
            {PRIORITY_CONFIG[task.priority].label}
          </span>
          {task.due_date && (
            <span className={cn("flex items-center gap-1 text-[11px] text-muted-foreground", overdue && "text-destructive")}>
              <CalendarDays className="h-3 w-3" />
              {formatDate(task.due_date)}
            </span>
          )}
          {task.comment_count > 0 && (
            <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
              <MessageSquare className="h-3 w-3" />
              {task.comment_count}
            </span>
          )}
        </div>
        {task.assignee && <UserAvatar name={task.assignee.name} color={task.assignee.avatar_color} size="sm" />}
      </div>
    </div>
  );
}
