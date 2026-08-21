"use client";

import { useMemo, useState } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  closestCorners,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { TASK_STATUSES } from "@/lib/constants";
import type { PaginatedResponse, Task, TaskStatus } from "@/lib/types";
import { KanbanColumn } from "./kanban-column";
import { TaskCard } from "./task-card";

export function KanbanBoard({
  tasks,
  projectId,
  onTaskClick,
  onAddTask,
}: {
  tasks: Task[];
  projectId: string;
  onTaskClick: (task: Task) => void;
  onAddTask: (status: TaskStatus) => void;
}) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const queryClient = useQueryClient();
  const queryKey = ["tasks", projectId];

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }));

  const columns = useMemo(() => {
    const grouped: Record<TaskStatus, Task[]> = { BACKLOG: [], TODO: [], IN_PROGRESS: [], DONE: [] };
    for (const task of tasks) grouped[task.status].push(task);
    for (const status of Object.keys(grouped) as TaskStatus[]) {
      grouped[status].sort((a, b) => a.position - b.position);
    }
    return grouped;
  }, [tasks]);

  const findStatus = (id: string): TaskStatus | null => {
    if (TASK_STATUSES.some((s) => s.value === id)) return id as TaskStatus;
    return tasks.find((t) => t.id === id)?.status || null;
  };

  const handleDragStart = (event: DragStartEvent) => {
    const task = tasks.find((t) => t.id === event.active.id);
    setActiveTask(task || null);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveTask(null);
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;
    const sourceStatus = findStatus(activeId);
    const targetStatus = findStatus(overId);
    if (!sourceStatus || !targetStatus) return;

    const targetTasks = columns[targetStatus].filter((t) => t.id !== activeId);
    const overIndex = targetTasks.findIndex((t) => t.id === overId);
    const insertIndex = overIndex >= 0 ? overIndex : targetTasks.length;

    if (sourceStatus === targetStatus && insertIndex === columns[targetStatus].findIndex((t) => t.id === activeId)) {
      return;
    }

    const movedTask = tasks.find((t) => t.id === activeId);
    if (!movedTask) return;

    const previous = queryClient.getQueryData<PaginatedResponse<Task>>(queryKey);

    queryClient.setQueryData<PaginatedResponse<Task>>(queryKey, (old) => {
      if (!old) return old;
      const withoutMoved = old.items.filter((t) => t.id !== activeId);
      const newTargetList = withoutMoved.filter((t) => t.status === targetStatus);
      newTargetList.splice(insertIndex, 0, { ...movedTask, status: targetStatus });
      const others = withoutMoved.filter((t) => t.status !== targetStatus);
      const reindexed = newTargetList.map((t, idx) => ({ ...t, position: idx }));
      return { ...old, items: [...others, ...reindexed] };
    });

    try {
      await api.post(`/tasks/${activeId}/move`, { status: targetStatus, position: insertIndex });
      queryClient.invalidateQueries({ queryKey });
      queryClient.invalidateQueries({ queryKey: ["activity"] });
    } catch (err) {
      queryClient.setQueryData(queryKey, previous);
      toast.error(err instanceof Error ? err.message : "Failed to move task");
    }
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="flex h-full gap-4 overflow-x-auto pb-4">
        {TASK_STATUSES.map(({ value }) => (
          <KanbanColumn key={value} status={value} tasks={columns[value]} onTaskClick={onTaskClick} onAddTask={onAddTask} />
        ))}
      </div>
      <DragOverlay>{activeTask && <TaskCard task={activeTask} onClick={() => {}} />}</DragOverlay>
    </DndContext>
  );
}
