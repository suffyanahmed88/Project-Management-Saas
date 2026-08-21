"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as Tabs from "@radix-ui/react-tabs";
import { formatDistanceToNow } from "date-fns";
import { Trash2, X } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { ActivityLog, Comment, Project, Task, TaskPriority, TaskStatus } from "@/lib/types";
import { PRIORITY_CONFIG, TASK_STATUSES } from "@/lib/constants";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { UserAvatar } from "@/components/ui/avatar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function TaskDetailDialog({
  task,
  open,
  onOpenChange,
}: {
  task: Task | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [labelInput, setLabelInput] = useState("");
  const [comment, setComment] = useState("");
  const queryClient = useQueryClient();

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
    }
  }, [task]);

  const { data: project } = useQuery({
    queryKey: ["projects", "detail", task?.project_id],
    queryFn: () => api.get<Project>(`/projects/${task?.project_id}`),
    enabled: !!task,
  });

  const { data: comments } = useQuery({
    queryKey: ["comments", task?.id],
    queryFn: () => api.get<Comment[]>(`/tasks/${task?.id}/comments`),
    enabled: !!task,
  });

  const { data: activity } = useQuery({
    queryKey: ["activity"],
    queryFn: () => api.get<ActivityLog[]>("/activity"),
    enabled: !!task,
  });

  const taskActivity = (activity || []).filter((a) => a.task_id === task?.id);

  const invalidateTask = () => {
    queryClient.invalidateQueries({ queryKey: ["tasks", task?.project_id] });
    queryClient.invalidateQueries({ queryKey: ["activity"] });
    queryClient.invalidateQueries({ queryKey: ["projects"] });
  };

  const updateMutation = useMutation({
    mutationFn: (patch: Record<string, unknown>) => api.patch<Task>(`/tasks/${task?.id}`, patch),
    onSuccess: invalidateTask,
    onError: (err: Error) => toast.error(err.message),
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/tasks/${task?.id}`),
    onSuccess: () => {
      invalidateTask();
      toast.success("Task deleted");
      onOpenChange(false);
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const commentMutation = useMutation({
    mutationFn: () => api.post<Comment>(`/tasks/${task?.id}/comments`, { body: comment }),
    onSuccess: () => {
      setComment("");
      queryClient.invalidateQueries({ queryKey: ["comments", task?.id] });
      queryClient.invalidateQueries({ queryKey: ["tasks", task?.project_id] });
      queryClient.invalidateQueries({ queryKey: ["activity"] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  if (!task) return null;

  const saveTitle = () => {
    if (title.trim() && title !== task.title) updateMutation.mutate({ title: title.trim() });
  };
  const saveDescription = () => {
    if (description !== (task.description || "")) updateMutation.mutate({ description });
  };
  const addLabel = () => {
    const value = labelInput.trim();
    if (value && !task.labels.includes(value)) {
      updateMutation.mutate({ labels: [...task.labels, value] });
    }
    setLabelInput("");
  };
  const removeLabel = (label: string) => {
    updateMutation.mutate({ labels: task.labels.filter((l) => l !== label) });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent wide>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[1fr_240px]">
          <div className="min-w-0 space-y-4">
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onBlur={saveTitle}
              className="h-auto border-none p-0 text-lg font-semibold shadow-none focus-visible:ring-0"
            />
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onBlur={saveDescription}
              placeholder="Add a description..."
              className="min-h-[100px] resize-none border-none bg-secondary/40 shadow-none focus-visible:ring-1"
            />

            <Tabs.Root defaultValue="comments">
              <Tabs.List className="flex gap-4 border-b border-border text-sm">
                <Tabs.Trigger
                  value="comments"
                  className="border-b-2 border-transparent pb-2 text-muted-foreground data-[state=active]:border-primary data-[state=active]:text-foreground"
                >
                  Comments ({comments?.length || 0})
                </Tabs.Trigger>
                <Tabs.Trigger
                  value="activity"
                  className="border-b-2 border-transparent pb-2 text-muted-foreground data-[state=active]:border-primary data-[state=active]:text-foreground"
                >
                  Activity
                </Tabs.Trigger>
              </Tabs.List>
              <Tabs.Content value="comments" className="mt-3 space-y-3">
                <div className="max-h-52 space-y-3 overflow-y-auto pr-1">
                  {comments?.length === 0 && <p className="text-sm text-muted-foreground">No comments yet.</p>}
                  {comments?.map((c) => (
                    <div key={c.id} className="flex items-start gap-2.5">
                      <UserAvatar name={c.author.name} color={c.author.avatar_color} size="sm" />
                      <div className="flex-1 rounded-lg bg-secondary/50 px-3 py-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{c.author.name}</span>
                          <span className="text-[11px] text-muted-foreground">
                            {formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}
                          </span>
                        </div>
                        <p className="mt-0.5 whitespace-pre-wrap text-sm">{c.body}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (comment.trim()) commentMutation.mutate();
                  }}
                  className="flex gap-2"
                >
                  <Input
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Write a comment..."
                  />
                  <Button type="submit" size="sm" disabled={!comment.trim() || commentMutation.isPending}>
                    Send
                  </Button>
                </form>
              </Tabs.Content>
              <Tabs.Content value="activity" className="mt-3 max-h-64 space-y-3 overflow-y-auto">
                {taskActivity.length === 0 && <p className="text-sm text-muted-foreground">No activity yet.</p>}
                {taskActivity.map((a) => (
                  <div key={a.id} className="flex items-start gap-2.5 text-sm">
                    <UserAvatar name={a.actor.name} color={a.actor.avatar_color} size="sm" />
                    <div>
                      <p>
                        <span className="font-medium">{a.actor.name}</span>{" "}
                        <span className="text-muted-foreground">{a.summary}</span>
                      </p>
                      <p className="text-[11px] text-muted-foreground">
                        {formatDistanceToNow(new Date(a.created_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                ))}
              </Tabs.Content>
            </Tabs.Root>
          </div>

          <div className="space-y-4 text-sm">
            <Field label="Status">
              <Select value={task.status} onValueChange={(v) => updateMutation.mutate({ status: v as TaskStatus })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TASK_STATUSES.map((s) => (
                    <SelectItem key={s.value} value={s.value}>
                      {s.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>

            <Field label="Priority">
              <Select value={task.priority} onValueChange={(v) => updateMutation.mutate({ priority: v as TaskPriority })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(PRIORITY_CONFIG).map(([value, cfg]) => (
                    <SelectItem key={value} value={value}>
                      {cfg.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>

            <Field label="Assignee">
              <Select
                value={task.assignee?.id || "unassigned"}
                onValueChange={(v) => updateMutation.mutate({ assignee_id: v === "unassigned" ? null : v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Unassigned" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="unassigned">Unassigned</SelectItem>
                  {project?.members.map((m) => (
                    <SelectItem key={m.id} value={m.id}>
                      {m.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>

            <Field label="Due date">
              <Input
                type="date"
                value={task.due_date || ""}
                onChange={(e) => updateMutation.mutate({ due_date: e.target.value || null })}
              />
            </Field>

            <Field label="Labels">
              <div className="flex flex-wrap gap-1.5">
                {task.labels.map((label) => (
                  <Badge key={label} variant="outline" className="gap-1 pr-1">
                    {label}
                    <button onClick={() => removeLabel(label)}>
                      <X className="h-2.5 w-2.5" />
                    </button>
                  </Badge>
                ))}
              </div>
              <Input
                value={labelInput}
                onChange={(e) => setLabelInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addLabel();
                  }
                }}
                onBlur={addLabel}
                placeholder="Add label + Enter"
                className="mt-2"
              />
            </Field>

            <Button
              variant="outline"
              size="sm"
              className="w-full text-destructive hover:bg-destructive/10 hover:text-destructive"
              onClick={() => deleteMutation.mutate()}
            >
              <Trash2 className="h-3.5 w-3.5" /> Delete task
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-medium text-muted-foreground">{label}</label>
      {children}
    </div>
  );
}
