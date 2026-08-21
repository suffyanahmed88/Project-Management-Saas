"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { STATUS_CONFIG } from "@/lib/constants";
import type { TaskStatus } from "@/lib/types";

const COLORS: Record<string, string> = {
  BACKLOG: "#a1a1aa",
  TODO: "#60a5fa",
  IN_PROGRESS: "#fbbf24",
  DONE: "#34d399",
};

export function StatusChart({ data }: { data: { status: string; count: number }[] }) {
  const total = data.reduce((sum, d) => sum + d.count, 0);

  if (total === 0) {
    return (
      <div className="flex h-56 items-center justify-center text-sm text-muted-foreground">
        No tasks yet
      </div>
    );
  }

  return (
    <div className="flex items-center gap-6">
      <div className="h-48 w-48">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="count" nameKey="status" innerRadius={55} outerRadius={80} paddingAngle={2}>
              {data.map((entry) => (
                <Cell key={entry.status} fill={COLORS[entry.status] || "#a1a1aa"} stroke="none" />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: 8,
                fontSize: 12,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex-1 space-y-2">
        {data.map((d) => (
          <div key={d.status} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: COLORS[d.status] || "#a1a1aa" }}
              />
              <span className="text-muted-foreground">
                {STATUS_CONFIG[d.status as TaskStatus]?.label || d.status}
              </span>
            </div>
            <span className="font-medium">{d.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
