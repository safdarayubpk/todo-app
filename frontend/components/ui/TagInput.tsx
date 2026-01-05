"use client";

import { useState, KeyboardEvent } from "react";
import { X, Plus } from "lucide-react";

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  maxTags?: number;
}

export function TagInput({
  tags,
  onChange,
  placeholder = "Add tags...",
  disabled = false,
  maxTags = 20,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");

  const normalizeTag = (tag: string) => tag.trim().toLowerCase();

  const addTag = (tag: string) => {
    const normalized = normalizeTag(tag);
    if (!normalized) return;
    if (tags.includes(normalized)) return;
    if (tags.length >= maxTags) return;

    onChange([...tags, normalized]);
    setInputValue("");
  };

  const removeTag = (tagToRemove: string) => {
    onChange(tags.filter((tag) => tag !== tagToRemove));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === "Backspace" && !inputValue && tags.length > 0) {
      removeTag(tags[tags.length - 1]);
    }
  };

  const handleAddClick = () => {
    addTag(inputValue);
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-1.5 p-2 min-h-[42px] rounded-lg bg-[var(--background)] border border-[var(--border)] focus-within:ring-2 focus-within:ring-[var(--primary)] focus-within:border-transparent transition-colors">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[var(--primary)]/10 text-[var(--primary)] text-sm"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              disabled={disabled}
              className="hover:bg-[var(--primary)]/20 rounded-full p-0.5 transition-colors disabled:opacity-50"
              aria-label={`Remove tag ${tag}`}
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
        <div className="flex-1 flex items-center min-w-[120px]">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={tags.length < maxTags ? placeholder : ""}
            disabled={disabled || tags.length >= maxTags}
            className="flex-1 bg-transparent border-none outline-none text-sm text-[var(--foreground)] placeholder-[var(--secondary)] disabled:opacity-50"
          />
          {inputValue && (
            <button
              type="button"
              onClick={handleAddClick}
              disabled={disabled}
              className="p-1 hover:bg-[var(--input-bg)] rounded transition-colors disabled:opacity-50"
              aria-label="Add tag"
            >
              <Plus className="w-4 h-4 text-[var(--secondary)]" />
            </button>
          )}
        </div>
      </div>
      <p className="text-xs text-[var(--secondary)]">
        Press Enter or comma to add. {tags.length}/{maxTags} tags.
      </p>
    </div>
  );
}
