"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ActivityLog } from "@/lib/types";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function ActivityPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["activity"],
    queryFn: () => api.get<ActivityLog[]>("/activity"),
  });

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Activity</h1>
        <p className="text-sm text-muted-foreground">A timeline of everything happening in your workspace.</p>
      </div>
      <Card>
        <CardContent className="p-5">
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(6)].map((_, i) => (
                <Skeleton key={i} className="h-10" />
              ))}
            </div>
          ) : (
            <ActivityFeed items={data || []} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
