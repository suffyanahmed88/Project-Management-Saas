"use client";

import * as React from "react";
import { cn, initials } from "@/lib/utils";

interface UserAvatarProps {
  name: string;
  color?: string;
  className?: string;
  size?: "sm" | "md" | "lg";
}

const sizes = {
  sm: "h-6 w-6 text-[10px]",
  md: "h-8 w-8 text-xs",
  lg: "h-10 w-10 text-sm",
};

export function UserAvatar({ name, color = "#6366f1", className, size = "md" }: UserAvatarProps) {
  return (
    <div
      className={cn(
        "flex shrink-0 items-center justify-center rounded-full font-semibold text-white ring-2 ring-background",
        sizes[size],
        className
      )}
      style={{ backgroundColor: color }}
      title={name}
    >
      {initials(name)}
    </div>
  );
}
