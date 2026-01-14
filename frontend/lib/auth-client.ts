"use client";

import { useState, useEffect } from "react";

// Use relative URL for API calls - Next.js will proxy to backend via rewrites
const API_BASE_URL = "/api/v1";
const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";

// Types for auth responses
export interface AuthUser {
  id: string;
  email: string;
  username: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface AuthError {
  message: string;
  status?: number;
}

export interface AuthResult {
  data?: AuthResponse;
  error?: AuthError;
}

/**
 * Get stored auth token from localStorage
 */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Get stored user data from localStorage
 */
export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const userData = localStorage.getItem(USER_KEY);
  return userData ? JSON.parse(userData) : null;
}

/**
 * Store auth token and user data
 */
function storeAuth(authResponse: AuthResponse): void {
  localStorage.setItem(TOKEN_KEY, authResponse.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(authResponse.user));
}

/**
 * Clear auth token and user data
 */
function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Sign up a new user
 */
export const signUp = {
  email: async ({
    email,
    password,
    name,
  }: {
    email: string;
    password: string;
    name?: string;
  }): Promise<AuthResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          username: name,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: {
            message: errorData.detail || "Signup failed",
            status: response.status,
          },
        };
      }

      const data: AuthResponse = await response.json();
      storeAuth(data);

      return { data };
    } catch (error) {
      return {
        error: {
          message:
            error instanceof Error
              ? error.message
              : "Network error during signup",
        },
      };
    }
  },
};

/**
 * Sign in an existing user
 */
export const signIn = {
  email: async ({
    email,
    password,
  }: {
    email: string;
    password: string;
  }): Promise<AuthResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: {
            message: errorData.detail || "Login failed",
            status: response.status,
          },
        };
      }

      const data: AuthResponse = await response.json();
      storeAuth(data);

      return { data };
    } catch (error) {
      return {
        error: {
          message:
            error instanceof Error
              ? error.message
              : "Network error during login",
        },
      };
    }
  },
};

/**
 * Sign out the current user
 */
export async function signOut(): Promise<void> {
  clearAuth();
  // Redirect to login page
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

/**
 * Get current user session
 */
export function useSession() {
  const [isClient, setIsClient] = useState(false);

  // Ensure we're on the client side to prevent hydration mismatch
  useEffect(() => {
    setIsClient(true);
  }, []);

  const user = isClient ? getStoredUser() : null;
  const token = isClient ? getToken() : null;

  return {
    data: user
      ? {
          user,
          session: {
            token,
            expiresAt: null, // We don't track expiry on client side
          },
        }
      : null,
    isPending: !isClient, // Still pending until client-side hydration is complete
    error: null,
  };
}

/**
 * Get current session (async version for compatibility)
 */
export async function getSession() {
  const user = getStoredUser();
  const token = getToken();

  return {
    data: user
      ? {
          user,
          session: {
            token,
            expiresAt: null,
          },
        }
      : null,
    error: null,
  };
}

/**
 * Auth client for compatibility with existing code
 */
export const authClient = {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
  token: async () => {
    const token = getToken();
    return {
      data: token ? { token } : null,
      error: token ? null : { message: "No token available" },
    };
  },
};
