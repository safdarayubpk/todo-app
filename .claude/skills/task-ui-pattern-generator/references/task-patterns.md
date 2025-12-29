# Task UI Patterns

## Core Task Interface

```typescript
interface Task {
  id: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

## TaskItem Component Pattern

Individual task display with completion toggle and actions.

```tsx
interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onEdit: (id: string, title: string) => void;
  onDelete: (id: string) => void;
}
```

**States:**
- Default: Normal display
- Completed: Strikethrough title, muted colors
- Editing: Inline input replaces title
- Loading: Disabled with spinner on action buttons

## TaskList Component Pattern

Container for multiple TaskItems with filtering.

```tsx
interface TaskListProps {
  tasks: Task[];
  filter: 'all' | 'active' | 'completed';
  onToggle: (id: string) => void;
  onEdit: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  emptyMessage?: string;
}
```

**Features:**
- Filter tasks by completion status
- Show empty state when no tasks match
- Virtualization for 100+ tasks
- Optimistic updates for smooth UX

## TaskFilters Component Pattern

Filter controls for task lists.

```tsx
interface TaskFiltersProps {
  currentFilter: 'all' | 'active' | 'completed';
  onFilterChange: (filter: 'all' | 'active' | 'completed') => void;
  counts: {
    all: number;
    active: number;
    completed: number;
  };
}
```

## TaskStats Component Pattern

Display completion statistics.

```tsx
interface TaskStatsProps {
  total: number;
  completed: number;
  showProgressBar?: boolean;
}
```

## Inline Editing Pattern

Click-to-edit behavior for task titles.

```tsx
// State management
const [isEditing, setIsEditing] = useState(false);
const [editValue, setEditValue] = useState(task.title);

// Save on Enter, cancel on Escape
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    onEdit(task.id, editValue);
    setIsEditing(false);
  } else if (e.key === 'Escape') {
    setEditValue(task.title);
    setIsEditing(false);
  }
};
```

## Optimistic Updates Pattern

Update UI immediately, rollback on error.

```tsx
const toggleTask = async (id: string) => {
  // Optimistic update
  setTasks(prev => prev.map(t =>
    t.id === id ? { ...t, isCompleted: !t.isCompleted } : t
  ));

  try {
    await api.toggleTask(id);
  } catch {
    // Rollback on error
    setTasks(prev => prev.map(t =>
      t.id === id ? { ...t, isCompleted: !t.isCompleted } : t
    ));
    toast.error('Failed to update task');
  }
};
```

## Drag and Drop Pattern

Reorder tasks via drag and drop.

```tsx
// Using @dnd-kit/core
import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';

const handleDragEnd = (event: DragEndEvent) => {
  const { active, over } = event;
  if (active.id !== over?.id) {
    const oldIndex = tasks.findIndex(t => t.id === active.id);
    const newIndex = tasks.findIndex(t => t.id === over?.id);
    setTasks(arrayMove(tasks, oldIndex, newIndex));
  }
};
```
