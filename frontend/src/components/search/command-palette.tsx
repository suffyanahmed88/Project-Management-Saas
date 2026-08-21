"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Command } from "cmdk";
import { FolderKanban, ListChecks, Search } from "lucide-react";
import { api } from "@/lib/api";
import type { SearchResult } from "@/lib/types";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const router = useRouter();

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      }
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const { data: results } = useQuery({
    queryKey: ["search", query],
    queryFn: () => api.get<SearchResult[]>(`/search?q=${encodeURIComponent(query)}`),
    enabled: open && query.length > 0,
  });

  if (!open) return null;

  const go = (result: SearchResult) => {
    setOpen(false);
    setQuery("");
    if (result.type === "project") router.push(`/projects/${result.id}`);
    else router.push(`/projects/${result.project_id}?task=${result.id}`);
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center bg-black/40 pt-[15vh] backdrop-blur-[2px] animate-fade-in"
      onClick={() => setOpen(false)}
    >
      <Command
        className="w-full max-w-lg overflow-hidden rounded-xl border border-border bg-popover shadow-2xl animate-slide-up"
        onClick={(e) => e.stopPropagation()}
        shouldFilter={false}
      >
        <div className="flex items-center gap-2 border-b border-border px-3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Command.Input
            autoFocus
            value={query}
            onValueChange={setQuery}
            placeholder="Search projects and tasks..."
            className="h-11 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <kbd className="rounded border border-border px-1.5 py-0.5 text-[10px] text-muted-foreground">
            ESC
          </kbd>
        </div>
        <Command.List className="max-h-80 overflow-y-auto p-2">
          {query.length === 0 && (
            <div className="px-3 py-6 text-center text-sm text-muted-foreground">
              Type to search across projects and tasks
            </div>
          )}
          {query.length > 0 && (!results || results.length === 0) && (
            <Command.Empty className="px-3 py-6 text-center text-sm text-muted-foreground">
              No results found
            </Command.Empty>
          )}
          {results?.map((r) => (
            <Command.Item
              key={`${r.type}-${r.id}`}
              value={`${r.type}-${r.id}`}
              onSelect={() => go(r)}
              className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2 text-sm data-[selected=true]:bg-accent"
            >
              {r.type === "project" ? (
                <FolderKanban className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ListChecks className="h-4 w-4 text-muted-foreground" />
              )}
              <div className="flex flex-col">
                <span className="font-medium">{r.title}</span>
                {r.subtitle && <span className="text-xs text-muted-foreground">{r.subtitle}</span>}
              </div>
            </Command.Item>
          ))}
        </Command.List>
      </Command>
    </div>
  );
}
