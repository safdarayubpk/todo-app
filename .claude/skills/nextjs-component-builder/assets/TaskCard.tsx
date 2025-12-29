'use client';

import { Task } from '@/types/task';

interface TaskCardProps {
  task: Task;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  onToggle?: (id: number) => void;
}

export default function TaskCard({
  task,
  onEdit,
  onDelete,
  onToggle,
}: TaskCardProps) {
  return (
    <article className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow border border-gray-100">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          {/* Checkbox */}
          <button
            onClick={() => onToggle?.(task.id)}
            className={`
              mt-1 w-5 h-5 rounded border-2 flex-shrink-0
              flex items-center justify-center
              transition-colors
              ${task.is_completed
                ? 'bg-green-500 border-green-500 text-white'
                : 'border-gray-300 hover:border-green-500'
              }
            `}
            aria-label={task.is_completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {task.is_completed && (
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </button>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h3
              className={`font-medium text-gray-900 ${
                task.is_completed ? 'line-through text-gray-500' : ''
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                {task.description}
              </p>
            )}
            <div className="mt-2 flex items-center gap-2">
              <span
                className={`
                  inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                  ${task.is_completed
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                  }
                `}
              >
                {task.is_completed ? 'Completed' : 'Pending'}
              </span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 flex-shrink-0">
          <button
            onClick={() => onEdit?.(task.id)}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            aria-label={`Edit task: ${task.title}`}
          >
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={() => onDelete?.(task.id)}
            className="p-2 rounded-full hover:bg-red-50 transition-colors"
            aria-label={`Delete task: ${task.title}`}
          >
            <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </article>
  );
}
