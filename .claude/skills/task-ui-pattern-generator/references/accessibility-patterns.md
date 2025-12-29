# Task UI Accessibility Patterns

## ARIA Roles and Labels

### Task Checkbox
```tsx
<button
  role="checkbox"
  aria-checked={task.isCompleted}
  aria-label={`Mark "${task.title}" as ${task.isCompleted ? 'incomplete' : 'complete'}`}
  onClick={() => onToggle(task.id)}
>
  {task.isCompleted ? <CheckIcon /> : <CircleIcon />}
</button>
```

### Task List
```tsx
<ul
  role="list"
  aria-label="Task list"
  aria-describedby="task-count"
>
  {tasks.map(task => (
    <li key={task.id} role="listitem">
      <TaskItem task={task} />
    </li>
  ))}
</ul>
<span id="task-count" className="sr-only">
  {tasks.length} tasks, {completedCount} completed
</span>
```

### Filter Buttons
```tsx
<div role="tablist" aria-label="Filter tasks">
  <button
    role="tab"
    aria-selected={filter === 'all'}
    aria-controls="task-list"
    onClick={() => setFilter('all')}
  >
    All ({counts.all})
  </button>
  {/* ... other filters */}
</div>
```

## Keyboard Navigation

### Task Item Keyboard Handling
```tsx
const handleKeyDown = (e: KeyboardEvent) => {
  switch (e.key) {
    case 'Enter':
    case ' ':
      e.preventDefault();
      onToggle(task.id);
      break;
    case 'Delete':
    case 'Backspace':
      if (e.metaKey || e.ctrlKey) {
        e.preventDefault();
        onDelete(task.id);
      }
      break;
    case 'e':
      if (e.metaKey || e.ctrlKey) {
        e.preventDefault();
        setIsEditing(true);
      }
      break;
  }
};
```

### Focus Management
```tsx
// Focus input when editing starts
useEffect(() => {
  if (isEditing && inputRef.current) {
    inputRef.current.focus();
    inputRef.current.select();
  }
}, [isEditing]);

// Return focus after delete
const handleDelete = () => {
  const nextTask = getNextFocusableTask(task.id);
  onDelete(task.id);
  nextTask?.focus();
};
```

## Screen Reader Announcements

### Live Regions for State Changes
```tsx
// Announce task completion
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
  className="sr-only"
>
  {announcement}
</div>

// Usage
const toggleTask = (id: string) => {
  const task = tasks.find(t => t.id === id);
  setAnnouncement(
    `Task "${task.title}" marked as ${task.isCompleted ? 'incomplete' : 'complete'}`
  );
  onToggle(id);
};
```

### Progress Announcements
```tsx
// Announce progress after batch operations
useEffect(() => {
  setAnnouncement(`${completedCount} of ${totalCount} tasks completed`);
}, [completedCount, totalCount]);
```

## Tailwind Accessibility Utilities

### Screen Reader Only
```tsx
// Hide visually but keep for screen readers
<span className="sr-only">Mark task as complete</span>
```

### Focus Indicators
```tsx
// Visible focus rings
<button className="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">
```

### Reduced Motion
```tsx
// Respect user preference
<div className="transition-all duration-200 motion-reduce:transition-none">
```

## Color Contrast

### Status Colors
```tsx
// Ensure 4.5:1 contrast ratio
const statusColors = {
  active: 'text-gray-900 dark:text-gray-100',
  completed: 'text-gray-500 dark:text-gray-400',
  error: 'text-red-700 dark:text-red-400',
};
```

### Interactive Elements
```tsx
// High contrast for clickable elements
<button className="
  text-blue-700 hover:text-blue-800
  dark:text-blue-400 dark:hover:text-blue-300
  underline-offset-2 hover:underline
">
  Edit
</button>
```

## Testing Checklist

- [ ] All interactive elements are keyboard accessible
- [ ] Focus order follows visual order
- [ ] Focus is visible on all interactive elements
- [ ] Screen reader announces all state changes
- [ ] Color is not the only indicator of state
- [ ] Text has 4.5:1 contrast ratio (3:1 for large text)
- [ ] Touch targets are at least 44x44px
- [ ] Animations respect `prefers-reduced-motion`
