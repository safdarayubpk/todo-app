"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signUp } from "@/lib/auth-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useToast } from "@/components/ui/Toast";

interface FormErrors {
  email?: string;
  username?: string;
  password?: string;
  general?: string;
}

export default function SignupPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [successMessage, setSuccessMessage] = useState("");

  const validateForm = (
    email: string,
    username: string,
    password: string
  ): FormErrors => {
    const newErrors: FormErrors = {};

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      newErrors.email = "Email is required";
    } else if (!emailRegex.test(email)) {
      newErrors.email = "Please enter a valid email address";
    }

    // Username validation (3-50 chars)
    if (!username) {
      newErrors.username = "Username is required";
    } else if (username.length < 3) {
      newErrors.username = "Username must be at least 3 characters";
    } else if (username.length > 50) {
      newErrors.username = "Username must be less than 50 characters";
    }

    // Password validation (8+ chars)
    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrors({});
    setSuccessMessage("");

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const username = formData.get("username") as string;
    const password = formData.get("password") as string;

    // Client-side validation
    const validationErrors = validateForm(email, username, password);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsLoading(true);

    try {
      const { error } = await signUp.email({
        email,
        password,
        name: username,
      });

      if (error) {
        // Handle duplicate email error
        if (error.message?.toLowerCase().includes("email")) {
          setErrors({ email: "This email is already registered" });
        } else if (error.message?.toLowerCase().includes("user")) {
          setErrors({ general: "An account with this email already exists" });
        } else {
          setErrors({ general: error.message || "Registration failed" });
        }
        return;
      }

      // Success - show message and redirect
      setSuccessMessage("Account created successfully! Redirecting to login...");
      showToast("Account created successfully!", "success");
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch {
      setErrors({ general: "An unexpected error occurred. Please try again." });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Create Account</h1>
          <p className="mt-2 text-[var(--secondary)]">
            Sign up to start managing your tasks
          </p>
        </div>

        {successMessage && (
          <div className="p-4 bg-[var(--accent)]/10 border border-[var(--accent)] rounded-lg text-[var(--accent)] text-center">
            {successMessage}
          </div>
        )}

        {errors.general && (
          <div className="p-4 bg-[var(--danger)]/10 border border-[var(--danger)] rounded-lg text-[var(--danger)] text-center">
            {errors.general}
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
            error={errors.email}
            disabled={isLoading}
          />

          <Input
            label="Username"
            name="username"
            type="text"
            placeholder="johndoe"
            autoComplete="username"
            error={errors.username}
            disabled={isLoading}
          />

          <Input
            label="Password"
            name="password"
            type="password"
            placeholder="At least 8 characters"
            autoComplete="new-password"
            error={errors.password}
            disabled={isLoading}
          />

          <Button type="submit" isLoading={isLoading} className="w-full">
            Sign Up
          </Button>
        </form>

        <p className="text-center text-[var(--secondary)]">
          Already have an account?{" "}
          <Link href="/login" className="text-[var(--primary)] hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
