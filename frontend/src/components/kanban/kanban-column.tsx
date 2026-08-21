"use client";

import { useDroppable } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { Plus } from "lucide-react";
import { TaskCard } from "./task-card";
import { STATUS_CONFIG } from "@/lib/constants";
import type { Task, TaskStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

export function KanbanColumn({
  status,
  tasks,
  onTaskClick,
  onAddTask,
}: {
  status: TaskStatus;
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  onAddTask: (status: TaskStatus) => void;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: status, data: { type: "column", status } });
  const config = STATUS_CONFIG[status];

  return (
    <div className="flex w-72 shrink-0 flex-col rounded-xl bg-secondary/40">
      <div className="flex items-center justify-between px-3 pb-2 pt-3">
        <div className="flex items-center gap-2">
          <span className={cn("h-2 w-2 rounded-full", config.dotClassName)} />
          <h3 className="text-sm font-medium">{config.label}</h3>
          <span className="rounded-full bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground">
            {tasks.length}
          </span>
        </div>
        <button
          onClick={() => onAddTask(status)}
          className="rounded p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        >
          <Plus className="h-3.5 w-3.5" />
        </button>
      </div>
      <div
        ref={setNodeRef}
        className={cn(
          "kanban-column-scroll flex-1 space-y-2 overflow-y-auto px-2 pb-3 transition-colors",
          isOver && "bg-primary/5"
        )}
        style={{ minHeight: 120 }}
      >
        <SortableContext items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onClick={() => onTaskClick(task)} />
          ))}
        </SortableContext>
      </div>
    </div>
  );
}
