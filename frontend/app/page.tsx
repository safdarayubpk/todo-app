import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold">Todo App</h1>
        <p className="text-[var(--secondary)] max-w-md">
          A multi-user task management application. Sign up to start organizing
          your tasks.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-6 py-3 bg-[var(--primary)] text-white rounded-lg hover:bg-[var(--primary-hover)] transition-colors"
          >
            Login
          </Link>
          <Link
            href="/signup"
            className="px-6 py-3 border border-[var(--border)] rounded-lg hover:bg-[var(--input-bg)] transition-colors"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </main>
  );
}
