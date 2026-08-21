"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useWorkspace } from "@/lib/workspace-context";
import type { WorkspaceRole } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UserAvatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface MemberEntry {
  id: string;
  role: WorkspaceRole;
  user: { id: string; name: string; email: string; avatar_color: string };
}

export default function SettingsPage() {
  const { user } = useAuth();
  const { activeWorkspace } = useWorkspace();
  const [inviteEmail, setInviteEmail] = useState("");
  const queryClient = useQueryClient();

  const { data: members } = useQuery({
    queryKey: ["members", activeWorkspace?.id],
    queryFn: () => api.get<MemberEntry[]>(`/workspaces/${activeWorkspace?.id}/members`),
    enabled: !!activeWorkspace,
  });

  const inviteMutation = useMutation({
    mutationFn: () => api.post(`/workspaces/${activeWorkspace?.id}/invite`, { email: inviteEmail, role: "MEMBER" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members", activeWorkspace?.id] });
      toast.success("Member invited");
      setInviteEmail("");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">Manage your profile and workspace members.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center gap-4">
          <UserAvatar name={user?.name || "?"} color={user?.avatar_color} size="lg" />
          <div>
            <p className="font-medium">{user?.name}</p>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Workspace members — {activeWorkspace?.name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (inviteEmail.trim()) inviteMutation.mutate();
            }}
            className="flex gap-2"
          >
            <Input
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="Invite by email"
            />
            <Button type="submit" disabled={inviteMutation.isPending || !inviteEmail.trim()}>
              Invite
            </Button>
          </form>

          <div className="divide-y divide-border rounded-lg border border-border">
            {members?.map((m) => (
              <div key={m.id} className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3">
                  <UserAvatar name={m.user.name} color={m.user.avatar_color} size="sm" />
                  <div>
                    <p className="text-sm font-medium">{m.user.name}</p>
                    <p className="text-xs text-muted-foreground">{m.user.email}</p>
                  </div>
                </div>
                <Badge variant="secondary">{m.role}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
