"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { X, CheckCircle, AlertCircle, Info } from "lucide-react";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}

const toastIcons: Record<ToastType, ReactNode> = {
  success: <CheckCircle className="w-5 h-5 text-[var(--accent)]" />,
  error: <AlertCircle className="w-5 h-5 text-[var(--danger)]" />,
  info: <Info className="w-5 h-5 text-[var(--primary)]" />,
};

const toastStyles: Record<ToastType, string> = {
  success: "border-[var(--accent)]/30 bg-[var(--accent)]/10",
  error: "border-[var(--danger)]/30 bg-[var(--danger)]/10",
  info: "border-[var(--primary)]/30 bg-[var(--primary)]/10",
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: ToastType = "info") => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast container - fixed at bottom on mobile, top-right on desktop */}
      <div className="fixed bottom-4 left-4 right-4 sm:bottom-auto sm:top-4 sm:left-auto sm:right-4 z-50 flex flex-col gap-2 sm:w-80 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`
              flex items-start gap-3 p-4 rounded-lg border shadow-lg
              bg-[var(--background)] pointer-events-auto
              animate-slide-in
              ${toastStyles[toast.type]}
            `}
            role="alert"
          >
            <span className="flex-shrink-0 mt-0.5">{toastIcons[toast.type]}</span>
            <p className="flex-1 text-sm text-[var(--foreground)]">{toast.message}</p>
            <button
              onClick={() => dismissToast(toast.id)}
              className="flex-shrink-0 p-1 rounded hover:bg-[var(--input-bg)] transition-colors"
              aria-label="Dismiss"
            >
              <X className="w-4 h-4 text-[var(--secondary)]" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
