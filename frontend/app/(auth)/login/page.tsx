"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signIn } from "@/lib/auth-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useToast } from "@/components/ui/Toast";

export default function LoginPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    if (!email || !password) {
      setError("Please enter both email and password");
      return;
    }

    setIsLoading(true);

    try {
      const { error: authError } = await signIn.email({
        email,
        password,
      });

      if (authError) {
        // Generic error message - don't reveal which field was wrong (US2 scenario 2)
        setError("Invalid credentials. Please check your email and password.");
        showToast("Login failed. Please check your credentials.", "error");
        return;
      }

      // Success - redirect to dashboard (US2 scenario 1)
      showToast("Welcome back!", "success");
      router.push("/dashboard");
    } catch {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Welcome Back</h1>
          <p className="mt-2 text-[var(--secondary)]">
            Log in to access your tasks
          </p>
        </div>

        {error && (
          <div className="p-4 bg-[var(--danger)]/10 border border-[var(--danger)] rounded-lg text-[var(--danger)] text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Email"
            name="email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            autoFocus
            disabled={isLoading}
          />

          <Input
            label="Password"
            name="password"
            type="password"
            placeholder="Enter your password"
            autoComplete="current-password"
            disabled={isLoading}
          />

          <Button type="submit" isLoading={isLoading} className="w-full">
            Log In
          </Button>
        </form>

        <p className="text-center text-[var(--secondary)]">
          Don&apos;t have an account?{" "}
          <Link href="/signup" className="text-[var(--primary)] hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </main>
  );
}
