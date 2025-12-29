# Next.js Component Patterns Reference

## Server vs Client Components

### Server Components (Default)

Use for components that:
- Fetch data directly
- Access backend resources
- Keep sensitive info on server
- Have no interactivity

```tsx
// app/components/TaskList.tsx (Server Component - no directive needed)
import { getTasks } from '@/lib/api';

export default async function TaskList() {
  const tasks = await getTasks();

  return (
    <ul className="space-y-4">
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </ul>
  );
}
```

### Client Components

Use for components that:
- Use hooks (useState, useEffect, etc.)
- Add event listeners (onClick, onChange)
- Use browser APIs
- Need interactivity

```tsx
// app/components/AddTaskForm.tsx
'use client';

import { useState } from 'react';

export default function AddTaskForm() {
  const [title, setTitle] = useState('');

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
    </form>
  );
}
```

## Component Composition

### Props Interface Pattern

```tsx
interface TaskCardProps {
  task: Task;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  isLoading?: boolean;
}

export default function TaskCard({
  task,
  onEdit,
  onDelete,
  isLoading = false
}: TaskCardProps) {
  // ...
}
```

### Children Pattern

```tsx
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`rounded-lg shadow-md p-4 ${className}`}>
      {children}
    </div>
  );
}
```

### Compound Components

```tsx
// Usage: <Card><Card.Header>Title</Card.Header><Card.Body>Content</Card.Body></Card>

function Card({ children }: { children: React.ReactNode }) {
  return <div className="rounded-lg shadow-md">{children}</div>;
}

Card.Header = function CardHeader({ children }: { children: React.ReactNode }) {
  return <div className="p-4 border-b font-semibold">{children}</div>;
};

Card.Body = function CardBody({ children }: { children: React.ReactNode }) {
  return <div className="p-4">{children}</div>;
};

export default Card;
```

## Accessibility Patterns

### Semantic HTML

```tsx
// Good - semantic
<article>
  <header><h2>{task.title}</h2></header>
  <p>{task.description}</p>
  <footer>
    <button>Edit</button>
    <button>Delete</button>
  </footer>
</article>

// Bad - div soup
<div>
  <div>{task.title}</div>
  <div>{task.description}</div>
  <div>
    <div onClick={handleEdit}>Edit</div>
  </div>
</div>
```

### ARIA Labels

```tsx
<button
  aria-label={`Delete task: ${task.title}`}
  onClick={() => onDelete(task.id)}
>
  <TrashIcon className="w-5 h-5" />
</button>

<input
  id="task-title"
  aria-describedby="title-hint"
  aria-invalid={errors.title ? 'true' : 'false'}
/>
<p id="title-hint" className="text-sm text-gray-500">
  Enter a descriptive title
</p>
```

### Focus Management

```tsx
'use client';

import { useRef, useEffect } from 'react';

export default function Modal({ isOpen, onClose, children }) {
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      closeButtonRef.current?.focus();
    }
  }, [isOpen]);

  return (
    <dialog open={isOpen} aria-modal="true">
      <button ref={closeButtonRef} onClick={onClose}>
        Close
      </button>
      {children}
    </dialog>
  );
}
```

## Loading & Error States

### Loading State

```tsx
interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  error: Error | null;
}

export default function TaskList({ tasks, isLoading, error }: TaskListProps) {
  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error.message} />;
  }

  if (tasks.length === 0) {
    return <EmptyState message="No tasks yet. Create your first task!" />;
  }

  return (
    <ul className="space-y-4">
      {tasks.map(task => <TaskCard key={task.id} task={task} />)}
    </ul>
  );
}
```

### Suspense Boundary

```tsx
import { Suspense } from 'react';

export default function TasksPage() {
  return (
    <Suspense fallback={<TaskListSkeleton />}>
      <TaskList />
    </Suspense>
  );
}
```

## Form Patterns

### Controlled Form

```tsx
'use client';

import { useState } from 'react';

interface FormData {
  title: string;
  description: string;
}

interface FormErrors {
  title?: string;
  description?: string;
}

export default function TaskForm({ onSubmit }: { onSubmit: (data: FormData) => void }) {
  const [formData, setFormData] = useState<FormData>({ title: '', description: '' });
  const [errors, setErrors] = useState<FormErrors>({});

  const validate = (): boolean => {
    const newErrors: FormErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium">
          Title
        </label>
        <input
          id="title"
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className={`mt-1 block w-full rounded-md border ${
            errors.title ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-500">{errors.title}</p>
        )}
      </div>
      <button type="submit" className="btn-primary">
        Save
      </button>
    </form>
  );
}
```
