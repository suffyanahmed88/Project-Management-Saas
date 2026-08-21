"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { Workspace } from "@/lib/types";
import { useWorkspace } from "@/lib/workspace-context";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function CreateWorkspaceDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [name, setName] = useState("");
  const queryClient = useQueryClient();
  const { setActiveWorkspaceId } = useWorkspace();

  const mutation = useMutation({
    mutationFn: () => api.post<Workspace>("/workspaces", { name }),
    onSuccess: (workspace) => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      setActiveWorkspaceId(workspace.id);
      toast.success(`Workspace "${workspace.name}" created`);
      setName("");
      onOpenChange(false);
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create workspace</DialogTitle>
        </DialogHeader>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (name.trim()) mutation.mutate();
          }}
          className="space-y-4"
        >
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Workspace name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Acme Inc" autoFocus />
          </div>
          <Button type="submit" className="w-full" disabled={mutation.isPending || !name.trim()}>
            {mutation.isPending ? "Creating..." : "Create workspace"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
