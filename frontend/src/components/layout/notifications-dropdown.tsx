"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api";
import type { Notification } from "@/lib/types";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

export function NotificationsDropdown() {
  const queryClient = useQueryClient();
  const { data: notifications } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => api.get<Notification[]>("/notifications"),
    refetchInterval: 30_000,
  });

  const unread = notifications?.filter((n) => !n.is_read).length || 0;

  const markRead = async (id: string) => {
    await api.post(`/notifications/${id}/read`);
    queryClient.invalidateQueries({ queryKey: ["notifications"] });
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4 w-4" />
          {unread > 0 && (
            <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary ring-2 ring-background" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Notifications</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {(!notifications || notifications.length === 0) && (
          <div className="px-3 py-6 text-center text-sm text-muted-foreground">You&apos;re all caught up</div>
        )}
        <div className="max-h-80 overflow-y-auto">
          {notifications?.map((n) => (
            <DropdownMenuItem
              key={n.id}
              onClick={() => !n.is_read && markRead(n.id)}
              className="flex flex-col items-start gap-0.5 py-2"
            >
              <div className="flex w-full items-start gap-2">
                {!n.is_read && <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />}
                <span className={n.is_read ? "text-muted-foreground" : ""}>{n.message}</span>
              </div>
              <span className="pl-3.5 text-[11px] text-muted-foreground">
                {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
              </span>
            </DropdownMenuItem>
          ))}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
