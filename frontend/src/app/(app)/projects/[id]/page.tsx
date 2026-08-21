"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Settings2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { PaginatedResponse, Project, Task } from "@/lib/types";
import { KanbanBoard } from "@/components/kanban/kanban-board";
import { CreateTaskDialog } from "@/components/tasks/create-task-dialog";
import { TaskDetailDialog } from "@/components/tasks/task-detail-dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { UserAvatar } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";
import type { TaskStatus } from "@/lib/types";

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [createStatus, setCreateStatus] = useState<TaskStatus | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ["projects", "detail", id],
    queryFn: () => api.get<Project>(`/projects/${id}`),
  });

  const { data: taskPage, isLoading: tasksLoading } = useQuery({
    queryKey: ["tasks", id],
    queryFn: () => api.get<PaginatedResponse<Task>>(`/tasks?project_id=${id}&page_size=200`),
  });

  const tasks = taskPage?.items || [];

  useEffect(() => {
    const taskId = searchParams.get("task");
    if (taskId && tasks.length > 0) {
      const found = tasks.find((t) => t.id === taskId);
      if (found) setSelectedTask(found);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, tasks.length]);

  useEffect(() => {
    if (selectedTask) {
      const fresh = tasks.find((t) => t.id === selectedTask.id);
      if (fresh && fresh !== selectedTask) setSelectedTask(fresh);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tasks]);

  const deleteProject = async () => {
    if (!confirm("Delete this project and all of its tasks? This cannot be undone.")) return;
    try {
      await api.delete(`/projects/${id}`);
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project deleted");
      router.push("/projects");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete project");
    }
  };

  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/projects" className="text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
          </Link>
          {projectLoading ? (
            <Skeleton className="h-7 w-48" />
          ) : (
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: project?.color }} />
              <h1 className="text-xl font-semibold tracking-tight">{project?.name}</h1>
            </div>
          )}
          <div className="flex -space-x-2 pl-2">
            {project?.members.map((m) => (
              <UserAvatar key={m.id} name={m.name} color={m.avatar_color} size="sm" />
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            onClick={() => {
              setCreateStatus(null);
              setShowCreate(true);
            }}
          >
            + Add task
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon">
                <Settings2 className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={deleteProject} className="text-destructive">
                <Trash2 className="h-3.5 w-3.5" /> Delete project
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {tasksLoading ? (
        <div className="flex gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-96 w-72 rounded-xl" />
          ))}
        </div>
      ) : (
        <KanbanBoard
          tasks={tasks}
          projectId={id}
          onTaskClick={setSelectedTask}
          onAddTask={(status) => {
            setCreateStatus(status);
            setShowCreate(true);
          }}
        />
      )}

      <CreateTaskDialog projectId={id} status={createStatus} open={showCreate} onOpenChange={setShowCreate} />
      <TaskDetailDialog
        task={selectedTask}
        open={!!selectedTask}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedTask(null);
            router.replace(`/projects/${id}`);
          }
        }}
      />
    </div>
  );
}
