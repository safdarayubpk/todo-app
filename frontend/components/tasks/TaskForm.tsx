"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { taskApi, Task } from "@/lib/api";

interface TaskFormProps {
  onTaskCreated: (task: Task) => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    // Validate title is not empty (US3 scenario 3)
    if (!title.trim()) {
      setError("Task title is required");
      return;
    }

    setIsLoading(true);

    try {
      const newTask = await taskApi.create({
        title: title.trim(),
        description: description.trim() || undefined,
      });

      onTaskCreated(newTask);

      // Clear form
      setTitle("");
      setDescription("");
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

      <Button type="submit" isLoading={isLoading} className="w-full sm:w-auto">
        Add Task
      </Button>
    </form>
  );
}
