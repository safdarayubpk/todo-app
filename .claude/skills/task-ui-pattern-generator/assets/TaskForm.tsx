"use client";

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
      <label htmlFor="new-task" className="sr-only">
        {placeholder}
      </label>
      <input
        ref={inputRef}
        id="new-task"
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className={`
          w-full px-4 py-3 pr-12 rounded-lg border
          bg-white dark:bg-gray-800
          text-gray-900 dark:text-gray-100
          placeholder-gray-400 dark:placeholder-gray-500
          border-gray-200 dark:border-gray-700
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors duration-200 motion-reduce:transition-none
        `}
        aria-describedby="task-form-hint"
      />
      <span id="task-form-hint" className="sr-only">
        Press Enter to add task, Escape to clear
      </span>
      <button
        type="submit"
        disabled={disabled || !title.trim()}
        className={`
          absolute right-2 top-1/2 -translate-y-1/2
          p-2 rounded-md
          text-white bg-blue-500 hover:bg-blue-600
          disabled:opacity-50 disabled:cursor-not-allowed
          focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
          transition-colors duration-200 motion-reduce:transition-none
        `}
        aria-label="Add task"
      >
        <Plus className="w-5 h-5" />
      </button>
    </form>
  );
}
