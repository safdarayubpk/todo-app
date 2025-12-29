"use client";

import { useMemo } from "react";
import { TaskItem } from "./TaskItem";
import { ClipboardList } from "lucide-react";

interface Task {
  id: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  createdAt: Date;
  updatedAt: Date;
}

type FilterType = "all" | "active" | "completed";

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
      {/* Screen reader summary */}
      <span id="task-count" className="sr-only">
        {tasks.length} tasks total, {completedCount} completed
      </span>

      {/* Task list */}
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
