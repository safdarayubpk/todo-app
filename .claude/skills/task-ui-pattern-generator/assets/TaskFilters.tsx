"use client";

type FilterType = "all" | "active" | "completed";

interface TaskFiltersProps {
  currentFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  counts: {
    all: number;
    active: number;
    completed: number;
  };
}

const filters: { key: FilterType; label: string }[] = [
  { key: "all", label: "All" },
  { key: "active", label: "Active" },
  { key: "completed", label: "Completed" },
];

export function TaskFilters({
  currentFilter,
  onFilterChange,
  counts,
}: TaskFiltersProps) {
  return (
    <div
      role="tablist"
      aria-label="Filter tasks"
      className="flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg"
    >
      {filters.map(({ key, label }) => (
        <button
          key={key}
          role="tab"
          aria-selected={currentFilter === key}
          aria-controls="task-list"
          onClick={() => onFilterChange(key)}
          className={`
            flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium
            transition-colors duration-200 motion-reduce:transition-none
            focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
            ${currentFilter === key
              ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
            }
          `}
        >
          {label}
          <span
            className={`
              px-1.5 py-0.5 text-xs rounded-full
              ${currentFilter === key
                ? "bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300"
                : "bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
              }
            `}
          >
            {counts[key]}
          </span>
        </button>
      ))}
    </div>
  );
}
