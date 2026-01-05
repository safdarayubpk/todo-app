"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { TagInput } from "@/components/ui/TagInput";
import { taskApi, Task, PriorityLevel } from "@/lib/api";

interface TaskFormProps {
  onTaskCreated: (task: Task) => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<PriorityLevel>("medium");
  const [tags, setTags] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    // Validate title is not empty
    if (!title.trim()) {
      setError("Task title is required");
      return;
    }

    setIsLoading(true);

    try {
      const newTask = await taskApi.create({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        tags,
      });

      onTaskCreated(newTask);

      // Clear form
      setTitle("");
      setDescription("");
      setPriority("medium");
      setTags([]);
      setShowAdvanced(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 bg-[var(--input-bg)] border border-[var(--border)] rounded-xl space-y-4"
    >
      <h2 className="text-lg font-semibold">Add New Task</h2>

      {error && (
        <div className="p-3 bg-[var(--danger)]/10 border border-[var(--danger)] rounded-lg text-[var(--danger)] text-sm">
          {error}
        </div>
      )}

      <Input
        label="Title"
        name="title"
        type="text"
        placeholder="What needs to be done?"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        disabled={isLoading}
      />

      {/* Priority dropdown - always visible */}
      <div className="flex flex-col gap-1">
        <label
          htmlFor="priority"
          className="text-sm font-medium text-[var(--foreground)]"
        >
          Priority
        </label>
        <select
          id="priority"
          name="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as PriorityLevel)}
          disabled={isLoading}
          className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Toggle for advanced options */}
      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-1 text-sm text-[var(--secondary)] hover:text-[var(--foreground)] transition-colors"
      >
        {showAdvanced ? (
          <>
            <ChevronUp className="w-4 h-4" />
            Hide advanced options
          </>
        ) : (
          <>
            <ChevronDown className="w-4 h-4" />
            Show advanced options
          </>
        )}
      </button>

      {/* Advanced options */}
      {showAdvanced && (
        <div className="space-y-4 pl-2 border-l-2 border-[var(--border)]">
          <div className="flex flex-col gap-1">
            <label
              htmlFor="description"
              className="text-sm font-medium text-[var(--foreground)]"
            >
              Description (optional)
            </label>
            <textarea
              id="description"
              name="description"
              placeholder="Add more details..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isLoading}
              rows={3}
              className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] placeholder-[var(--secondary)] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed resize-none"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-[var(--foreground)]">
              Tags (optional)
            </label>
            <TagInput
              tags={tags}
              onChange={setTags}
              placeholder="Add tags..."
              disabled={isLoading}
            />
          </div>
        </div>
      )}

      <Button type="submit" isLoading={isLoading} className="w-full sm:w-auto">
        Add Task
      </Button>
    </form>
  );
}
