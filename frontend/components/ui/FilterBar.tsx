"use client";

import { useState, useEffect } from "react";
import { Search, X, SlidersHorizontal, ArrowUpDown } from "lucide-react";
import { FilterState, PriorityLevel } from "@/lib/api";

interface FilterBarProps {
  filters: FilterState;
  onFilterChange: (filters: Partial<FilterState>) => void;
  availableTags?: string[];
}

export function FilterBar({ filters, onFilterChange, availableTags = [] }: FilterBarProps) {
  const [searchInput, setSearchInput] = useState(filters.search);
  const [showFilters, setShowFilters] = useState(false);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== filters.search) {
        onFilterChange({ search: searchInput });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, filters.search, onFilterChange]);

  const hasActiveFilters =
    filters.status !== "all" ||
    filters.priority !== "all" ||
    filters.tags.length > 0 ||
    filters.search.trim() !== "" ||
    filters.sortBy !== "created_at";

  const clearFilters = () => {
    setSearchInput("");
    onFilterChange({
      status: "all",
      priority: "all",
      tags: [],
      search: "",
      sortBy: "created_at",
      sortDir: "desc",
    });
  };

  const toggleTag = (tag: string) => {
    const newTags = filters.tags.includes(tag)
      ? filters.tags.filter((t) => t !== tag)
      : [...filters.tags, tag];
    onFilterChange({ tags: newTags });
  };

  return (
    <div className="space-y-3">
      {/* Search and filter toggle row */}
      <div className="flex gap-2">
        {/* Search input */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--secondary)]" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-9 pr-8 py-2 rounded-lg bg-[var(--input-bg)] border border-[var(--border)] text-[var(--foreground)] placeholder-[var(--secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent text-sm"
          />
          {searchInput && (
            <button
              onClick={() => {
                setSearchInput("");
                onFilterChange({ search: "" });
              }}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-[var(--border)] rounded transition-colors"
            >
              <X className="w-3 h-3 text-[var(--secondary)]" />
            </button>
          )}
        </div>

        {/* Filter toggle button */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`
            flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors
            ${showFilters || hasActiveFilters
              ? "bg-[var(--primary)]/10 border-[var(--primary)] text-[var(--primary)]"
              : "bg-[var(--input-bg)] border-[var(--border)] text-[var(--secondary)] hover:border-[var(--primary)]"
            }
          `}
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span className="hidden sm:inline text-sm">Filters</span>
          {hasActiveFilters && (
            <span className="w-2 h-2 rounded-full bg-[var(--primary)]" />
          )}
        </button>
      </div>

      {/* Expanded filters */}
      {showFilters && (
        <div className="p-4 bg-[var(--input-bg)] border border-[var(--border)] rounded-xl space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Status filter */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--secondary)] uppercase tracking-wider">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => onFilterChange({ status: e.target.value as FilterState["status"] })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              >
                <option value="all">All</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Priority filter */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--secondary)] uppercase tracking-wider">
                Priority
              </label>
              <select
                value={filters.priority}
                onChange={(e) => onFilterChange({ priority: e.target.value as FilterState["priority"] })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              >
                <option value="all">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            {/* Sort by */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--secondary)] uppercase tracking-wider">
                Sort By
              </label>
              <select
                value={filters.sortBy}
                onChange={(e) => onFilterChange({ sortBy: e.target.value as FilterState["sortBy"] })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              >
                <option value="created_at">Date Created</option>
                <option value="priority">Priority</option>
                <option value="title">Title (A-Z)</option>
              </select>
            </div>

            {/* Sort direction */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--secondary)] uppercase tracking-wider">
                Order
              </label>
              <button
                onClick={() => onFilterChange({ sortDir: filters.sortDir === "asc" ? "desc" : "asc" })}
                className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] text-sm hover:border-[var(--primary)] transition-colors"
              >
                <span>{filters.sortDir === "asc" ? "Ascending" : "Descending"}</span>
                <ArrowUpDown className="w-4 h-4 text-[var(--secondary)]" />
              </button>
            </div>
          </div>

          {/* Tags filter */}
          {availableTags.length > 0 && (
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--secondary)] uppercase tracking-wider">
                Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {availableTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={`
                      px-2.5 py-1 rounded-full text-sm transition-colors
                      ${filters.tags.includes(tag)
                        ? "bg-[var(--primary)] text-white"
                        : "bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] hover:border-[var(--primary)]"
                      }
                    `}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Clear filters */}
          {hasActiveFilters && (
            <div className="pt-2 border-t border-[var(--border)]">
              <button
                onClick={clearFilters}
                className="text-sm text-[var(--primary)] hover:underline"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      )}

      {/* Active filters summary (when collapsed) */}
      {!showFilters && hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span className="text-[var(--secondary)]">Active:</span>
          {filters.status !== "all" && (
            <span className="px-2 py-0.5 rounded-full bg-[var(--accent)]/10 text-[var(--accent)]">
              {filters.status}
            </span>
          )}
          {filters.priority !== "all" && (
            <span className="px-2 py-0.5 rounded-full bg-[var(--primary)]/10 text-[var(--primary)]">
              {filters.priority} priority
            </span>
          )}
          {filters.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 rounded-full bg-[var(--primary)]/10 text-[var(--primary)]"
            >
              #{tag}
            </span>
          ))}
          {filters.sortBy !== "created_at" && (
            <span className="px-2 py-0.5 rounded-full bg-[var(--secondary)]/10 text-[var(--secondary)]">
              sorted by {filters.sortBy}
            </span>
          )}
          <button
            onClick={clearFilters}
            className="text-[var(--primary)] hover:underline"
          >
            Clear
          </button>
        </div>
      )}
    </div>
  );
}
