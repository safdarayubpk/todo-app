"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useSession, signOut } from "@/lib/auth-client";
import { Button } from "@/components/ui/Button";
import { TaskForm } from "@/components/tasks/TaskForm";
import { TaskList } from "@/components/tasks/TaskList";
import { taskApi, Task, FilterState, defaultFilters } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

export default function DashboardPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const { showToast } = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState<FilterState>(defaultFilters);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isPending && !session) {
      router.replace("/login");
    }
  }, [session, isPending, router]);

  // Check if there are active filters
  const hasActiveFilters = useMemo(() => {
    return (
      filters.status !== "all" ||
      filters.priority !== "all" ||
      filters.tags.length > 0 ||
      filters.search.trim() !== "" ||
      filters.sortBy !== "created_at"
    );
  }, [filters]);

  // Fetch tasks function with filters
  const fetchTasks = useCallback(async () => {
    try {
      // Only show loading spinner for filter changes, not initial skeleton load
      if (!isInitialLoad) {
        setIsLoadingTasks(true);
      }
      const data = await taskApi.list(filters);
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoadingTasks(false);
      setIsInitialLoad(false);
    }
  }, [filters, isInitialLoad]);

  // Fetch tasks on mount (with delay to ensure auth token is ready after login)
  useEffect(() => {
    if (session) {
      // Delay to allow auth token to fully initialize after login
      // The apiFetch function has its own retry logic, but initial delay helps
      const timer = setTimeout(() => {
        fetchTasks();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [session, fetchTasks]);

  // Listen for refresh events from chat with debounce
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const handleRefresh = () => {
      // Clear any existing timeout to debounce multiple events
      clearTimeout(timeoutId);

      // Only fetch after a short delay to prevent rapid updates
      timeoutId = setTimeout(() => {
        fetchTasks();
      }, 500);
    };

    window.addEventListener('refresh-tasks', handleRefresh);
    return () => {
      window.removeEventListener('refresh-tasks', handleRefresh);
      clearTimeout(timeoutId);
    };
  }, [fetchTasks]);

  const handleLogout = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error("Logout error:", error);
    }
    showToast("You have been logged out", "info");
    router.replace("/login");
  };

  const handleTaskCreated = (newTask: Task) => {
    setTasks((prev) => [newTask, ...prev]);
    showToast("Task created successfully", "success");
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks((prev) =>
      prev.map((task) => (task.id === updatedTask.id ? updatedTask : task))
    );
    showToast("Task updated", "success");
  };

  const handleTaskDeleted = (taskId: number) => {
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
    showToast("Task deleted", "success");
  };

  // Handle filter changes - immediately fetch with new filters
  const handleFilterChange = useCallback((newFilters: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

  if (isPending) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <div className="animate-pulse text-[var(--secondary)]">Loading...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-3xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">My Tasks</h1>
            {session?.user && (
              <p className="text-[var(--secondary)]">
                Welcome back, {session.user.username || session.user.email}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/chat"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
              Chat Assistant
            </Link>
            <Button variant="secondary" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </header>

        {/* Error display */}
        {error && (
          <div className="p-4 bg-[var(--danger)]/10 border border-[var(--danger)] rounded-lg text-[var(--danger)]">
            {error}
          </div>
        )}

        {/* Add Task Form */}
        <TaskForm onTaskCreated={handleTaskCreated} />

        {/* Task List */}
        <TaskList
          tasks={tasks}
          isLoading={isInitialLoad}
          onTaskUpdated={handleTaskUpdated}
          onTaskDeleted={handleTaskDeleted}
          filters={filters}
          onFilterChange={handleFilterChange}
          hasActiveFilters={hasActiveFilters}
        />
      </div>
    </main>
  );
}
