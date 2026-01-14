"use client";

import { authClient } from "./auth-client";

// Use relative URL for API calls - Next.js will proxy to backend via rewrites
const API_BASE_URL = "/api/v1";

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
      // Retry token fetch with increasing delay to handle race condition on login
      const maxRetries = 5;
      const baseDelayMs = 150;
      let tokenData = null;

      for (let attempt = 0; attempt < maxRetries; attempt++) {
        const { data, error } = await authClient.token();

        if (data?.token) {
          tokenData = data.token;
          break;
        }

        // If we still have retries, wait with increasing delay
        if (attempt < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, baseDelayMs * (attempt + 1)));
        } else if (error) {
          throw new Error("Failed to get auth token after retries");
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

// Priority type
export type PriorityLevel = "high" | "medium" | "low";

// Filter state for task list
export interface FilterState {
  status: "all" | "pending" | "completed";
  priority: "all" | PriorityLevel;
  tags: string[];
  search: string;
  sortBy: "created_at" | "priority" | "title";
  sortDir: "asc" | "desc";
}

// Default filter state
export const defaultFilters: FilterState = {
  status: "all",
  priority: "all",
  tags: [],
  search: "",
  sortBy: "created_at",
  sortDir: "desc",
};

/**
 * Build query string from filter state
 */
function buildFilterQuery(filters?: Partial<FilterState>): string {
  if (!filters) return "";

  const params = new URLSearchParams();

  if (filters.status && filters.status !== "all") {
    params.append("status", filters.status);
  }
  if (filters.priority && filters.priority !== "all") {
    params.append("priority", filters.priority);
  }
  if (filters.tags && filters.tags.length > 0) {
    filters.tags.forEach((tag) => params.append("tags", tag));
  }
  if (filters.search && filters.search.trim()) {
    params.append("search", filters.search.trim());
  }
  if (filters.sortBy && filters.sortBy !== "created_at") {
    params.append("sort_by", filters.sortBy);
  }
  if (filters.sortDir && filters.sortDir !== "desc") {
    params.append("sort_dir", filters.sortDir);
  }

  const queryString = params.toString();
  return queryString ? `?${queryString}` : "";
}

/**
 * Task API methods
 */
export const taskApi = {
  list: (filters?: Partial<FilterState>) =>
    apiFetch<Task[]>(`/tasks${buildFilterQuery(filters)}`),

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

  addTag: (id: number, tag: string) =>
    apiFetch<Task>(`/tasks/${id}/tags?tag=${encodeURIComponent(tag)}`, {
      method: "POST",
    }),

  removeTag: (id: number, tag: string) =>
    apiFetch<Task>(`/tasks/${id}/tags?tag=${encodeURIComponent(tag)}`, {
      method: "DELETE",
    }),
};

// Types matching backend schemas
export interface Task {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  priority: PriorityLevel;
  tags: string[];
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  is_completed?: boolean;
  priority?: PriorityLevel;
  tags?: string[];
}

export interface TaskUpdate {
  title?: string | null;
  description?: string | null;
  is_completed?: boolean | null;
  priority?: PriorityLevel | null;
  tags?: string[] | null;
}
