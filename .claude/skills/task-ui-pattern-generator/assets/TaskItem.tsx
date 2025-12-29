"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Check, Circle, Pencil, Trash2, X } from "lucide-react";

interface Task {
  id: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  createdAt: Date;
  updatedAt: Date;
}

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
      {/* Completion Toggle */}
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
            : "border-gray-300 dark:border-gray-600 hover:border-green-500 dark:hover:border-green-500"
          }
        `}
      >
        {task.isCompleted && <Check className="w-4 h-4" />}
      </button>

      {/* Task Content */}
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
              className="
                flex-1 px-2 py-1 text-sm rounded border
                border-blue-500 dark:border-blue-400
                bg-white dark:bg-gray-900
                text-gray-900 dark:text-gray-100
                focus:outline-none focus:ring-2 focus:ring-blue-500
              "
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
            className={`
              block truncate text-sm
              ${task.isCompleted
                ? "text-gray-500 dark:text-gray-400 line-through"
                : "text-gray-900 dark:text-gray-100"
              }
            `}
          >
            {task.title}
          </span>
        )}
      </div>

      {/* Action Buttons */}
      {!isEditing && (
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={() => setIsEditing(true)}
            className="
              p-1.5 rounded text-gray-500 hover:text-blue-600 hover:bg-blue-50
              dark:hover:text-blue-400 dark:hover:bg-blue-900/30
              focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
            "
            aria-label={`Edit "${task.title}"`}
          >
            <Pencil className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="
              p-1.5 rounded text-gray-500 hover:text-red-600 hover:bg-red-50
              dark:hover:text-red-400 dark:hover:bg-red-900/30
              focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500
            "
            aria-label={`Delete "${task.title}"`}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
