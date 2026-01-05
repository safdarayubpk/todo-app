"use client";

import { PriorityLevel } from "@/lib/api";

interface PriorityBadgeProps {
  priority: PriorityLevel;
  size?: "sm" | "md";
}

const priorityConfig = {
  high: {
    label: "High",
    bgColor: "bg-red-100 dark:bg-red-900/30",
    textColor: "text-red-700 dark:text-red-400",
    borderColor: "border-red-200 dark:border-red-800",
  },
  medium: {
    label: "Medium",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
    textColor: "text-yellow-700 dark:text-yellow-400",
    borderColor: "border-yellow-200 dark:border-yellow-800",
  },
  low: {
    label: "Low",
    bgColor: "bg-green-100 dark:bg-green-900/30",
    textColor: "text-green-700 dark:text-green-400",
    borderColor: "border-green-200 dark:border-green-800",
  },
};

export function PriorityBadge({ priority, size = "sm" }: PriorityBadgeProps) {
  const config = priorityConfig[priority];

  const sizeClasses = size === "sm"
    ? "px-1.5 py-0.5 text-xs"
    : "px-2 py-1 text-sm";

  return (
    <span
      className={`
        inline-flex items-center rounded-md font-medium border
        ${config.bgColor} ${config.textColor} ${config.borderColor}
        ${sizeClasses}
      `}
    >
      {config.label}
    </span>
  );
}

export function PriorityDot({ priority }: { priority: PriorityLevel }) {
  const dotColors = {
    high: "bg-red-500",
    medium: "bg-yellow-500",
    low: "bg-green-500",
  };

  return (
    <span
      className={`inline-block w-2 h-2 rounded-full ${dotColors[priority]}`}
      title={`${priority} priority`}
    />
  );
}
