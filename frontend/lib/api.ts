"use client";

import { authClient } from "./auth-client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

interface FetchOptions extends RequestInit {
  requireAuth?: boolean;
}

/**
 * API client helper with automatic Bearer token injection.
 */
export async function apiFetch<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { requireAuth = true, headers = {}, ...fetchOptions } = options;

  const requestHeaders: HeadersInit = {
    "Content-Type": "application/json",
    ...headers,
  };

  // Inject Bearer token if auth is required
  if (requireAuth) {
    try {
      // Retry token fetch with small delay to handle race condition on login
      let retries = 3;
      let tokenData = null;

      while (retries > 0) {
        const { data, error } = await authClient.token();
        if (error) {
          retries--;
          if (retries > 0) {
            await new Promise(resolve => setTimeout(resolve, 100));
            continue;
          }
          throw new Error("Failed to get auth token");
        }
        if (data?.token) {
          tokenData = data.token;
          break;
        }
        retries--;
        if (retries > 0) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      }

      if (tokenData) {
        (requestHeaders as Record<string, string>)["Authorization"] =
          `Bearer ${tokenData}`;
      } else {
        throw new Error("No token available");
      }
    } catch {
      throw new Error("Authentication required");
    }
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers: requestHeaders,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

/**
 * Task API methods
 */
export const taskApi = {
  list: () => apiFetch<Task[]>("/tasks"),

  get: (id: number) => apiFetch<Task>(`/tasks/${id}`),

  create: (data: TaskCreate) =>
    apiFetch<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: TaskUpdate) =>
    apiFetch<Task>(`/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiFetch<void>(`/tasks/${id}`, {
      method: "DELETE",
    }),

  toggle: (id: number) =>
    apiFetch<Task>(`/tasks/${id}/toggle`, {
      method: "PATCH",
    }),
};

// Types matching backend schemas
export interface Task {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  is_completed?: boolean;
}

export interface TaskUpdate {
  title?: string | null;
  description?: string | null;
  is_completed?: boolean | null;
}
