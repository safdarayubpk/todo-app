"use client";

import { X } from "lucide-react";

interface TagChipProps {
  tag: string;
  onRemove?: () => void;
  size?: "sm" | "md";
}

export function TagChip({ tag, onRemove, size = "sm" }: TagChipProps) {
  const sizeClasses = size === "sm"
    ? "px-1.5 py-0.5 text-xs gap-1"
    : "px-2 py-1 text-sm gap-1.5";

  return (
    <span
      className={`
        inline-flex items-center rounded-full
        bg-[var(--primary)]/10 text-[var(--primary)]
        border border-[var(--primary)]/20
        ${sizeClasses}
      `}
    >
      <span className="max-w-[100px] truncate">{tag}</span>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="flex-shrink-0 hover:bg-[var(--primary)]/20 rounded-full p-0.5 transition-colors"
          aria-label={`Remove tag ${tag}`}
        >
          <X className="w-3 h-3" />
        </button>
      )}
    </span>
  );
}

interface TagListProps {
  tags: string[];
  onRemove?: (tag: string) => void;
  maxDisplay?: number;
}

export function TagList({ tags, onRemove, maxDisplay = 3 }: TagListProps) {
  if (!tags || tags.length === 0) return null;

  const displayTags = maxDisplay ? tags.slice(0, maxDisplay) : tags;
  const remaining = tags.length - displayTags.length;

  return (
    <div className="flex flex-wrap items-center gap-1">
      {displayTags.map((tag) => (
        <TagChip
          key={tag}
          tag={tag}
          onRemove={onRemove ? () => onRemove(tag) : undefined}
        />
      ))}
      {remaining > 0 && (
        <span className="text-xs text-[var(--secondary)]">
          +{remaining} more
        </span>
      )}
    </div>
  );
}
