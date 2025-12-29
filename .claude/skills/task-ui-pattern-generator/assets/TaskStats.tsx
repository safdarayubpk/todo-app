"use client";

interface TaskStatsProps {
  total: number;
  completed: number;
  showProgressBar?: boolean;
}

export function TaskStats({
  total,
  completed,
  showProgressBar = true,
}: TaskStatsProps) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const remaining = total - completed;

  return (
    <div className="space-y-3">
      {/* Stats summary */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <span className="text-gray-600 dark:text-gray-400">
            <span className="font-semibold text-gray-900 dark:text-gray-100">
              {completed}
            </span>
            {" "}completed
          </span>
          <span className="text-gray-600 dark:text-gray-400">
            <span className="font-semibold text-gray-900 dark:text-gray-100">
              {remaining}
            </span>
            {" "}remaining
          </span>
        </div>
        <span
          className="font-semibold text-gray-900 dark:text-gray-100"
          aria-label={`${percentage} percent complete`}
        >
          {percentage}%
        </span>
      </div>

      {/* Progress bar */}
      {showProgressBar && (
        <div
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Task completion progress: ${percentage}%`}
          className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
        >
          <div
            className={`
              h-full rounded-full transition-all duration-500 motion-reduce:transition-none
              ${percentage === 100
                ? "bg-green-500"
                : percentage > 50
                  ? "bg-blue-500"
                  : "bg-blue-400"
              }
            `}
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}

      {/* Celebration message */}
      {percentage === 100 && total > 0 && (
        <p
          className="text-sm text-green-600 dark:text-green-400 font-medium text-center"
          role="status"
          aria-live="polite"
        >
          All tasks completed!
        </p>
      )}
    </div>
  );
}
