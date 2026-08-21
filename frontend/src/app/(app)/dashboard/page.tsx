"use client";

import { useQuery } from "@tanstack/react-query";
import { FolderKanban, ListTodo, CheckCircle2, AlertTriangle } from "lucide-react";
import { api } from "@/lib/api";
import type { AnalyticsResponse } from "@/lib/types";
import { StatCard } from "@/components/dashboard/stat-card";
import { StatusChart } from "@/components/dashboard/status-chart";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useWorkspace } from "@/lib/workspace-context";

export default function DashboardPage() {
  const { activeWorkspace } = useWorkspace();
  const { data, isLoading } = useQuery({
    queryKey: ["analytics", activeWorkspace?.id],
    queryFn: () => api.get<AnalyticsResponse>("/analytics"),
    enabled: !!activeWorkspace,
  });

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">An overview of your workspace activity.</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total Projects" value={data?.total_projects || 0} icon={FolderKanban} accent="text-primary" />
          <StatCard label="Open Tasks" value={data?.open_tasks || 0} icon={ListTodo} accent="text-blue-500" />
          <StatCard label="Completed" value={data?.completed_tasks || 0} icon={CheckCircle2} accent="text-emerald-500" />
          <StatCard label="Overdue" value={data?.overdue_tasks || 0} icon={AlertTriangle} accent="text-red-500" />
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Task Status</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-48" /> : <StatusChart data={data?.status_breakdown || []} />}
          </CardContent>
        </Card>
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                {[...Array(4)].map((_, i) => (
                  <Skeleton key={i} className="h-10" />
                ))}
              </div>
            ) : (
              <ActivityFeed items={data?.recent_activity || []} />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
