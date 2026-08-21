"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import type { Workspace } from "./types";
import { useAuth } from "./auth-context";

interface WorkspaceContextValue {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  setActiveWorkspaceId: (id: string) => void;
  isLoading: boolean;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [activeId, setActiveId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["workspaces"],
    queryFn: () => api.get<Workspace[]>("/workspaces"),
    enabled: !!user,
  });

  const workspaces = useMemo(() => data ?? [], [data]);

  useEffect(() => {
    if (!activeId && workspaces.length > 0) {
      const stored = typeof window !== "undefined" ? localStorage.getItem("pmsaas_active_ws") : null;
      const match = workspaces.find((w) => w.id === stored);
      setActiveId(match ? match.id : workspaces[0].id);
    }
  }, [workspaces, activeId]);

  const setActiveWorkspaceId = (id: string) => {
    setActiveId(id);
    if (typeof window !== "undefined") localStorage.setItem("pmsaas_active_ws", id);
  };

  const activeWorkspace = workspaces.find((w) => w.id === activeId) || null;

  return (
    <WorkspaceContext.Provider value={{ workspaces, activeWorkspace, setActiveWorkspaceId, isLoading }}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within WorkspaceProvider");
  return ctx;
}
