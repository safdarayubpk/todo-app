"use client";

import { ReactNode, useEffect, useRef } from "react";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Focus trap and scroll lock
  useEffect(() => {
    if (isOpen) {
      const previouslyFocused = document.activeElement as HTMLElement;
      modalRef.current?.focus();
      document.body.style.overflow = "hidden";

      return () => {
        document.body.style.overflow = "";
        previouslyFocused?.focus();
      };
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal content - full screen on mobile, centered on desktop */}
      <div
        ref={modalRef}
        tabIndex={-1}
        className="relative w-full max-w-md bg-[var(--background)] shadow-xl border border-[var(--border)] max-h-[90vh] overflow-y-auto sm:rounded-xl rounded-t-xl fixed sm:relative bottom-0 sm:bottom-auto inset-x-0 sm:inset-x-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
          <h2
            id="modal-title"
            className="text-lg font-semibold text-[var(--foreground)]"
          >
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-[var(--input-bg)] transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5 text-[var(--secondary)]" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
}
