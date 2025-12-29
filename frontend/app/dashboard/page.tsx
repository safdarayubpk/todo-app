"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession, signOut } from "@/lib/auth-client";
import { Button } from "@/components/ui/Button";
import { TaskForm } from "@/components/tasks/TaskForm";
import { TaskList } from "@/components/tasks/TaskList";
import { taskApi, Task } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

export default function DashboardPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const { showToast } = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [error, setError] = useState("");

  // Fetch tasks on mount
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const data = await taskApi.list();
        setTasks(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load tasks");
      } finally {
        setIsLoadingTasks(false);
      }
    };

    if (session) {
      fetchTasks();
    }
  }, [session]);

  const handleLogout = async () => {
    await signOut();
    showToast("You have been logged out", "info");
    router.push("/login");
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
                Welcome back, {session.user.name || session.user.email}
              </p>
            )}
          </div>
          <Button variant="secondary" onClick={handleLogout}>
            Logout
          </Button>
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
          isLoading={isLoadingTasks}
          onTaskUpdated={handleTaskUpdated}
          onTaskDeleted={handleTaskDeleted}
        />
      </div>
    </main>
  );
}
