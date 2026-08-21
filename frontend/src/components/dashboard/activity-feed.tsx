import { formatDistanceToNow } from "date-fns";
import { UserAvatar } from "@/components/ui/avatar";
import { EmptyState } from "@/components/ui/empty-state";
import { Activity } from "lucide-react";
import type { ActivityLog } from "@/lib/types";

export function ActivityFeed({ items }: { items: ActivityLog[] }) {
  if (items.length === 0) {
    return <EmptyState icon={Activity} title="No activity yet" description="Actions across your workspace will show up here." />;
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.id} className="flex items-start gap-3">
          <UserAvatar name={item.actor.name} color={item.actor.avatar_color} size="sm" />
          <div className="flex-1 text-sm">
            <p>
              <span className="font-medium">{item.actor.name}</span>{" "}
              <span className="text-muted-foreground">{item.summary}</span>
            </p>
            <p className="text-xs text-muted-foreground">
              {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
