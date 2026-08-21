"use client";

import { useQuery } from "@tanstack/react-query";
import { FolderKanban } from "lucide-react";
import { api } from "@/lib/api";
import type { Project } from "@/lib/types";
import { useWorkspace } from "@/lib/workspace-context";
import { ProjectCard } from "@/components/dashboard/project-card";
import { CreateProjectDialog } from "@/components/dashboard/create-project-dialog";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function ProjectsPage() {
  const { activeWorkspace } = useWorkspace();
  const { data: projects, isLoading } = useQuery({
    queryKey: ["projects", activeWorkspace?.id],
    queryFn: () => api.get<Project[]>(`/projects?workspace_id=${activeWorkspace?.id}`),
    enabled: !!activeWorkspace,
  });

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
          <p className="text-sm text-muted-foreground">All projects in {activeWorkspace?.name || "your workspace"}.</p>
        </div>
        {activeWorkspace && <CreateProjectDialog />}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-40 rounded-xl" />
          ))}
        </div>
      ) : projects && projects.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((p) => (
            <ProjectCard key={p.id} project={p} />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={FolderKanban}
          title="No projects yet"
          description="Create your first project to start organizing work."
          action={activeWorkspace && <CreateProjectDialog />}
        />
      )}
    </div>
  );
}
