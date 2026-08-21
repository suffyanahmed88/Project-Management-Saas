import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { UserAvatar } from "@/components/ui/avatar";
import type { Project } from "@/lib/types";

const STATUS_VARIANT: Record<string, "default" | "secondary" | "success" | "warning"> = {
  PLANNING: "secondary",
  ACTIVE: "default",
  ON_HOLD: "warning",
  COMPLETED: "success",
  ARCHIVED: "secondary",
};

export function ProjectCard({ project }: { project: Project }) {
  return (
    <Link href={`/projects/${project.id}`}>
      <Card className="group h-full transition-all hover:-translate-y-0.5 hover:shadow-md">
        <CardContent className="flex h-full flex-col p-5">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: project.color }} />
              <h3 className="font-medium leading-tight group-hover:text-primary">{project.name}</h3>
            </div>
            <Badge variant={STATUS_VARIANT[project.status] || "secondary"}>{project.status.replace("_", " ")}</Badge>
          </div>
          {project.description && (
            <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{project.description}</p>
          )}
          <div className="mt-4 flex-1" />
          <div className="mb-2 h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${project.progress}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {project.completed_task_count}/{project.task_count} tasks
            </span>
            <div className="flex -space-x-2">
              {project.members.slice(0, 4).map((m) => (
                <UserAvatar key={m.id} name={m.name} color={m.avatar_color} size="sm" />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
