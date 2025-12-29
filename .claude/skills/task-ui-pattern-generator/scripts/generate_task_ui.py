#!/usr/bin/env python3
"""
Task UI Pattern Generator
=========================
Generates task-focused UI components with Tailwind CSS and accessibility.

Usage:
    python generate_task_ui.py <component> [--output-dir <path>]

Components:
    all        - Generate all task UI components
    item       - TaskItem component (completion toggle, edit, delete)
    list       - TaskList component (filtered list with empty state)
    filters    - TaskFilters component (all/active/completed tabs)
    stats      - TaskStats component (progress bar and counts)
    form       - TaskForm component (add new task input)

Examples:
    python generate_task_ui.py all
    python generate_task_ui.py all --output-dir frontend/components/tasks
    python generate_task_ui.py item --output-dir src/components
"""

import argparse
from pathlib import Path

# Component templates with __NAME__ placeholders replaced
TASK_INTERFACE = '''export interface Task {
  id: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export type FilterType = "all" | "active" | "completed";
'''

TASK_ITEM_TEMPLATE = '''"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Check, Circle, Pencil, Trash2, X } from "lucide-react";
import { Task } from "./types";

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onEdit: (id: string, title: string) => void;
  onDelete: (id: string) => void;
}

export function TaskItem({ task, onToggle, onEdit, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(task.title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (editValue.trim()) {
        onEdit(task.id, editValue.trim());
        setIsEditing(false);
      }
    } else if (e.key === "Escape") {
      setEditValue(task.title);
      setIsEditing(false);
    }
  };

  const handleSave = () => {
    if (editValue.trim()) {
      onEdit(task.id, editValue.trim());
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditValue(task.title);
    setIsEditing(false);
  };

  return (
    <div
      className={`
        group flex items-center gap-3 p-4 rounded-lg border
        transition-all duration-200 motion-reduce:transition-none
        ${task.isCompleted
          ? "bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700"
          : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
        }
      `}
    >
      <button
        role="checkbox"
        aria-checked={task.isCompleted}
        aria-label={`Mark "${task.title}" as ${task.isCompleted ? "incomplete" : "complete"}`}
        onClick={() => onToggle(task.id)}
        className={`
          flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center
          transition-colors duration-200 motion-reduce:transition-none
          focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
          ${task.isCompleted
            ? "bg-green-500 border-green-500 text-white"
            : "border-gray-300 dark:border-gray-600 hover:border-green-500"
          }
        `}
      >
        {task.isCompleted && <Check className="w-4 h-4" />}
      </button>

      <div className="flex-1 min-w-0">
        {isEditing ? (
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={handleSave}
              className="flex-1 px-2 py-1 text-sm rounded border border-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Edit task title"
            />
            <button
              onClick={handleCancel}
              className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              aria-label="Cancel editing"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <span
            className={`block truncate text-sm ${task.isCompleted
              ? "text-gray-500 dark:text-gray-400 line-through"
              : "text-gray-900 dark:text-gray-100"
            }`}
          >
            {task.title}
          </span>
        )}
      </div>

      {!isEditing && (
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={() => setIsEditing(true)}
            className="p-1.5 rounded text-gray-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:text-blue-400 dark:hover:bg-blue-900/30 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label={`Edit "${task.title}"`}
          >
            <Pencil className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="p-1.5 rounded text-gray-500 hover:text-red-600 hover:bg-red-50 dark:hover:text-red-400 dark:hover:bg-red-900/30 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
            aria-label={`Delete "${task.title}"`}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
'''

TASK_LIST_TEMPLATE = '''"use client";

import { useMemo } from "react";
import { TaskItem } from "./TaskItem";
import { Task, FilterType } from "./types";
import { ClipboardList } from "lucide-react";

interface TaskListProps {
  tasks: Task[];
  filter: FilterType;
  onToggle: (id: string) => void;
  onEdit: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  emptyMessage?: string;
}

export function TaskList({
  tasks,
  filter,
  onToggle,
  onEdit,
  onDelete,
  emptyMessage = "No tasks yet",
}: TaskListProps) {
  const filteredTasks = useMemo(() => {
    switch (filter) {
      case "active":
        return tasks.filter((t) => !t.isCompleted);
      case "completed":
        return tasks.filter((t) => t.isCompleted);
      default:
        return tasks;
    }
  }, [tasks, filter]);

  const completedCount = tasks.filter((t) => t.isCompleted).length;

  if (filteredTasks.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
        role="status"
        aria-label={emptyMessage}
      >
        <ClipboardList className="w-12 h-12 mb-4 opacity-50" />
        <p className="text-sm">{emptyMessage}</p>
        {filter !== "all" && tasks.length > 0 && (
          <p className="text-xs mt-1 text-gray-400 dark:text-gray-500">
            Try changing the filter to see more tasks
          </p>
        )}
      </div>
    );
  }

  return (
    <div>
      <span id="task-count" className="sr-only">
        {tasks.length} tasks total, {completedCount} completed
      </span>
      <ul
        role="list"
        aria-label="Task list"
        aria-describedby="task-count"
        className="space-y-2"
      >
        {filteredTasks.map((task) => (
          <li key={task.id} role="listitem">
            <TaskItem
              task={task}
              onToggle={onToggle}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}
'''

TASK_FILTERS_TEMPLATE = '''"use client";

import { FilterType } from "./types";

interface TaskFiltersProps {
  currentFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  counts: {
    all: number;
    active: number;
    completed: number;
  };
}

const filters: { key: FilterType; label: string }[] = [
  { key: "all", label: "All" },
  { key: "active", label: "Active" },
  { key: "completed", label: "Completed" },
];

export function TaskFilters({
  currentFilter,
  onFilterChange,
  counts,
}: TaskFiltersProps) {
  return (
    <div
      role="tablist"
      aria-label="Filter tasks"
      className="flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg"
    >
      {filters.map(({ key, label }) => (
        <button
          key={key}
          role="tab"
          aria-selected={currentFilter === key}
          aria-controls="task-list"
          onClick={() => onFilterChange(key)}
          className={`
            flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium
            transition-colors duration-200 motion-reduce:transition-none
            focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
            ${currentFilter === key
              ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
            }
          `}
        >
          {label}
          <span
            className={`px-1.5 py-0.5 text-xs rounded-full ${currentFilter === key
              ? "bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300"
              : "bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
            }`}
          >
            {counts[key]}
          </span>
        </button>
      ))}
    </div>
  );
}
'''

TASK_STATS_TEMPLATE = '''"use client";

interface TaskStatsProps {
  total: number;
  completed: number;
  showProgressBar?: boolean;
}

export function TaskStats({
  total,
  completed,
  showProgressBar = true,
}: TaskStatsProps) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const remaining = total - completed;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <span className="text-gray-600 dark:text-gray-400">
            <span className="font-semibold text-gray-900 dark:text-gray-100">{completed}</span> completed
          </span>
          <span className="text-gray-600 dark:text-gray-400">
            <span className="font-semibold text-gray-900 dark:text-gray-100">{remaining}</span> remaining
          </span>
        </div>
        <span
          className="font-semibold text-gray-900 dark:text-gray-100"
          aria-label={`${percentage} percent complete`}
        >
          {percentage}%
        </span>
      </div>

      {showProgressBar && (
        <div
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Task completion progress: ${percentage}%`}
          className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
        >
          <div
            className={`h-full rounded-full transition-all duration-500 motion-reduce:transition-none ${
              percentage === 100
                ? "bg-green-500"
                : percentage > 50
                  ? "bg-blue-500"
                  : "bg-blue-400"
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}

      {percentage === 100 && total > 0 && (
        <p
          className="text-sm text-green-600 dark:text-green-400 font-medium text-center"
          role="status"
          aria-live="polite"
        >
          All tasks completed!
        </p>
      )}
    </div>
  );
}
'''

TASK_FORM_TEMPLATE = '''"use client";

import { useState, useRef, FormEvent, KeyboardEvent } from "react";
import { Plus } from "lucide-react";

interface TaskFormProps {
  onSubmit: (title: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export function TaskForm({
  onSubmit,
  placeholder = "Add a new task...",
  disabled = false,
}: TaskFormProps) {
  const [title, setTitle] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmedTitle = title.trim();
    if (trimmedTitle) {
      onSubmit(trimmedTitle);
      setTitle("");
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") {
      setTitle("");
      inputRef.current?.blur();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <label htmlFor="new-task" className="sr-only">{placeholder}</label>
      <input
        ref={inputRef}
        id="new-task"
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full px-4 py-3 pr-12 rounded-lg border bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 motion-reduce:transition-none"
        aria-describedby="task-form-hint"
      />
      <span id="task-form-hint" className="sr-only">Press Enter to add task, Escape to clear</span>
      <button
        type="submit"
        disabled={disabled || !title.trim()}
        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-md text-white bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 transition-colors duration-200 motion-reduce:transition-none"
        aria-label="Add task"
      >
        <Plus className="w-5 h-5" />
      </button>
    </form>
  );
}
'''

INDEX_TEMPLATE = '''export { TaskItem } from "./TaskItem";
export { TaskList } from "./TaskList";
export { TaskFilters } from "./TaskFilters";
export { TaskStats } from "./TaskStats";
export { TaskForm } from "./TaskForm";
export type { Task, FilterType } from "./types";
'''

COMPONENTS = {
    "types": ("types.ts", TASK_INTERFACE),
    "item": ("TaskItem.tsx", TASK_ITEM_TEMPLATE),
    "list": ("TaskList.tsx", TASK_LIST_TEMPLATE),
    "filters": ("TaskFilters.tsx", TASK_FILTERS_TEMPLATE),
    "stats": ("TaskStats.tsx", TASK_STATS_TEMPLATE),
    "form": ("TaskForm.tsx", TASK_FORM_TEMPLATE),
    "index": ("index.ts", INDEX_TEMPLATE),
}


def generate_component(component: str, output_dir: str) -> dict[str, str]:
    """Generate a single task UI component."""
    if component not in COMPONENTS:
        raise ValueError(f"Unknown component: {component}")

    filename, content = COMPONENTS[component]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_path = output_path / filename
    file_path.write_text(content)

    return {
        "file": str(file_path),
        "component": component,
    }


def generate_all(output_dir: str) -> list[dict[str, str]]:
    """Generate all task UI components."""
    results = []
    for component in COMPONENTS:
        result = generate_component(component, output_dir)
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate task-focused UI components"
    )
    parser.add_argument(
        "component",
        choices=["all", "item", "list", "filters", "stats", "form"],
        help="Component to generate (or 'all' for everything)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Output directory for generated files"
    )

    args = parser.parse_args()

    print(f"Generating task UI components in: {args.output_dir}")
    print()

    if args.component == "all":
        results = generate_all(args.output_dir)
        print("Generated files:")
        for result in results:
            print(f"  - {result['file']}")
    else:
        result = generate_component(args.component, args.output_dir)
        # Also generate types.ts as it's needed
        generate_component("types", args.output_dir)
        print(f"Generated: {result['file']}")
        print(f"Generated: {Path(args.output_dir) / 'types.ts'}")

    print()
    print("Next steps:")
    print("  1. Install dependencies: npm install lucide-react")
    print("  2. Import components in your page/layout")
    print("  3. Wire up state management (useState, Zustand, or API)")


if __name__ == "__main__":
    main()
