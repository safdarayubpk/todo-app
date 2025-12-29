"use client";

import { Task } from "@/lib/api";
import { TaskItem } from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  onTaskUpdated: (task: Task) => void;
  onTaskDeleted: (taskId: number) => void;
}

export function TaskList({
  tasks,
  isLoading,
  onTaskUpdated,
  onTaskDeleted,
}: TaskListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="animate-pulse p-4 rounded-lg border border-[var(--border)] bg-[var(--input-bg)]"
          >
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-[var(--border)]" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-[var(--border)] rounded w-3/4" />
                <div className="h-3 bg-[var(--border)] rounded w-1/2" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Empty state (US4 scenario 2)
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 px-4 border border-dashed border-[var(--border)] rounded-xl">
        <div className="text-4xl mb-4">📝</div>
        <h3 className="text-lg font-medium mb-2">No tasks yet</h3>
        <p className="text-[var(--secondary)]">
          Create your first task using the form above to get started!
        </p>
      </div>
    );
  }

  // Separate completed and incomplete tasks
  const incompleteTasks = tasks.filter((t) => !t.is_completed);
  const completedTasks = tasks.filter((t) => t.is_completed);

  return (
    <div className="space-y-6">
      {/* Incomplete tasks */}
      {incompleteTasks.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-[var(--secondary)] uppercase tracking-wider">
            To Do ({incompleteTasks.length})
          </h3>
          <div className="space-y-2">
            {incompleteTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onTaskUpdated={onTaskUpdated}
                onTaskDeleted={onTaskDeleted}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed tasks */}
      {completedTasks.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-[var(--secondary)] uppercase tracking-wider">
            Completed ({completedTasks.length})
          </h3>
          <div className="space-y-2">
            {completedTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onTaskUpdated={onTaskUpdated}
                onTaskDeleted={onTaskDeleted}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
