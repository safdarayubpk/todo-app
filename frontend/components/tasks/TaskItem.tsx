"use client";

import { useState } from "react";
import { Check, Pencil, Trash2 } from "lucide-react";
import { Task, taskApi } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";

interface TaskItemProps {
  task: Task;
  onTaskUpdated: (task: Task) => void;
  onTaskDeleted: (taskId: number) => void;
}

export function TaskItem({ task, onTaskUpdated, onTaskDeleted }: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || "");
  const [editError, setEditError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      const updatedTask = await taskApi.toggle(task.id);
      onTaskUpdated(updatedTask);
    } catch (err) {
      console.error("Failed to toggle task:", err);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await taskApi.delete(task.id);
      onTaskDeleted(task.id);
      setShowDeleteModal(false);
    } catch (err) {
      console.error("Failed to delete task:", err);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEditError("");

    if (!editTitle.trim()) {
      setEditError("Title is required");
      return;
    }

    setIsSaving(true);
    try {
      const updatedTask = await taskApi.update(task.id, {
        title: editTitle.trim(),
        description: editDescription.trim() || null,
      });
      onTaskUpdated(updatedTask);
      setShowEditModal(false);
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Failed to update task");
    } finally {
      setIsSaving(false);
    }
  };

  const openEditModal = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || "");
    setEditError("");
    setShowEditModal(true);
  };

  return (
    <>
      <div
        className={`
          flex items-start gap-3 p-4 rounded-lg border transition-colors
          ${
            task.is_completed
              ? "bg-[var(--accent)]/5 border-[var(--accent)]/30"
              : "bg-[var(--background)] border-[var(--border)]"
          }
        `}
      >
        {/* Checkbox/Toggle */}
        <button
          onClick={handleToggle}
          disabled={isToggling}
          className={`
            flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center
            transition-colors mt-0.5
            ${
              task.is_completed
                ? "bg-[var(--accent)] border-[var(--accent)] text-white"
                : "border-[var(--border)] hover:border-[var(--accent)]"
            }
            disabled:opacity-50
          `}
          aria-label={task.is_completed ? "Mark as incomplete" : "Mark as complete"}
        >
          {task.is_completed && <Check className="w-4 h-4" />}
        </button>

        {/* Task content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`
              font-medium break-words
              ${task.is_completed ? "line-through text-[var(--secondary)]" : ""}
            `}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`
                mt-1 text-sm break-words
                ${
                  task.is_completed
                    ? "text-[var(--secondary)]/70"
                    : "text-[var(--secondary)]"
                }
              `}
            >
              {task.description}
            </p>
          )}
        </div>

        {/* Actions - touch-friendly sizes for mobile */}
        <div className="flex-shrink-0 flex gap-1">
          <button
            onClick={openEditModal}
            className="p-2 sm:p-2 min-w-[44px] min-h-[44px] sm:min-w-0 sm:min-h-0 rounded-lg hover:bg-[var(--input-bg)] active:bg-[var(--input-bg)] transition-colors flex items-center justify-center"
            aria-label="Edit task"
          >
            <Pencil className="w-4 h-4 text-[var(--secondary)]" />
          </button>
          <button
            onClick={() => setShowDeleteModal(true)}
            className="p-2 sm:p-2 min-w-[44px] min-h-[44px] sm:min-w-0 sm:min-h-0 rounded-lg hover:bg-[var(--danger)]/10 active:bg-[var(--danger)]/10 transition-colors flex items-center justify-center"
            aria-label="Delete task"
          >
            <Trash2 className="w-4 h-4 text-[var(--danger)]" />
          </button>
        </div>
      </div>

      {/* Edit Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Edit Task"
      >
        <form onSubmit={handleEdit} className="space-y-4">
          {editError && (
            <div className="p-3 bg-[var(--danger)]/10 border border-[var(--danger)] rounded-lg text-[var(--danger)] text-sm">
              {editError}
            </div>
          )}

          <Input
            label="Title"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            disabled={isSaving}
          />

          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-[var(--foreground)]">
              Description
            </label>
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              disabled={isSaving}
              rows={3}
              className="w-full px-3 py-2 rounded-lg bg-[var(--input-bg)] border border-[var(--border)] text-[var(--foreground)] placeholder-[var(--secondary)] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed resize-none"
            />
          </div>

          <div className="flex gap-3 justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setShowEditModal(false)}
              disabled={isSaving}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={isSaving}>
              Save
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Task"
      >
        <div className="space-y-4">
          <p className="text-[var(--secondary)]">
            Are you sure you want to delete this task? This action cannot be undone.
          </p>
          <p className="font-medium">&ldquo;{task.title}&rdquo;</p>
          <div className="flex gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={() => setShowDeleteModal(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
              isLoading={isDeleting}
            >
              Delete
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}
