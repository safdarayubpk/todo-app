# Tailwind CSS Conventions Reference

## Mobile-First Responsive Design

Apply base styles for mobile, then add breakpoint prefixes for larger screens:

```tsx
<div className="
  px-4 py-2          // Mobile: smaller padding
  md:px-6 md:py-4    // Tablet: medium padding
  lg:px-8 lg:py-6    // Desktop: larger padding
">
```

### Breakpoints

| Prefix | Min Width | Typical Device |
|--------|-----------|----------------|
| (none) | 0px | Mobile |
| `sm:` | 640px | Large phones |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Laptops |
| `xl:` | 1280px | Desktops |
| `2xl:` | 1536px | Large screens |

## Layout Patterns

### Grid Layouts

```tsx
// Responsive task grid
<div className="
  grid
  grid-cols-1
  sm:grid-cols-2
  lg:grid-cols-3
  gap-4
">
  {tasks.map(task => <TaskCard key={task.id} task={task} />)}
</div>
```

### Flexbox Layouts

```tsx
// Header with space-between
<header className="flex items-center justify-between p-4">
  <h1>Tasks</h1>
  <button>Add Task</button>
</header>

// Centered content
<div className="flex items-center justify-center min-h-screen">
  <LoginForm />
</div>

// Stack with gap
<div className="flex flex-col gap-4">
  <TaskCard />
  <TaskCard />
</div>
```

### Container

```tsx
<main className="container mx-auto px-4 py-8 max-w-4xl">
  {children}
</main>
```

## Color System

### Semantic Colors

```tsx
// Status indicators
<span className="text-green-600">Completed</span>
<span className="text-yellow-600">In Progress</span>
<span className="text-gray-500">Pending</span>

// Backgrounds
<div className="bg-white dark:bg-gray-800">
<div className="bg-gray-50 dark:bg-gray-900">

// Borders
<div className="border border-gray-200 dark:border-gray-700">
```

### Interactive States

```tsx
<button className="
  bg-blue-600
  hover:bg-blue-700
  active:bg-blue-800
  focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  disabled:bg-gray-400 disabled:cursor-not-allowed
  transition-colors
">
  Submit
</button>
```

## Component Styles

### Buttons

```tsx
// Primary button
<button className="
  px-4 py-2
  bg-blue-600 text-white
  rounded-lg
  hover:bg-blue-700
  focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  transition-colors
">

// Secondary button
<button className="
  px-4 py-2
  bg-gray-100 text-gray-700
  rounded-lg
  hover:bg-gray-200
  border border-gray-300
">

// Danger button
<button className="
  px-4 py-2
  bg-red-600 text-white
  rounded-lg
  hover:bg-red-700
">

// Icon button
<button className="
  p-2
  rounded-full
  hover:bg-gray-100
  focus:ring-2
" aria-label="Delete">
  <TrashIcon className="w-5 h-5" />
</button>
```

### Cards

```tsx
<article className="
  bg-white
  rounded-lg
  shadow-md
  p-4
  hover:shadow-lg
  transition-shadow
  border border-gray-100
">
```

### Forms

```tsx
// Input
<input className="
  w-full
  px-3 py-2
  border border-gray-300
  rounded-lg
  focus:ring-2 focus:ring-blue-500 focus:border-blue-500
  placeholder-gray-400
" />

// Error state
<input className="
  w-full
  px-3 py-2
  border border-red-500
  rounded-lg
  focus:ring-2 focus:ring-red-500
" />

// Label
<label className="block text-sm font-medium text-gray-700 mb-1">

// Error message
<p className="mt-1 text-sm text-red-500">
```

### Badges/Status

```tsx
// Completed badge
<span className="
  inline-flex items-center
  px-2.5 py-0.5
  rounded-full
  text-xs font-medium
  bg-green-100 text-green-800
">
  Completed
</span>

// Pending badge
<span className="
  inline-flex items-center
  px-2.5 py-0.5
  rounded-full
  text-xs font-medium
  bg-gray-100 text-gray-800
">
  Pending
</span>
```

## Spacing Conventions

### Consistent Spacing Scale

| Class | Size | Use Case |
|-------|------|----------|
| `gap-2` / `space-y-2` | 0.5rem | Tight groups |
| `gap-4` / `space-y-4` | 1rem | Default spacing |
| `gap-6` / `space-y-6` | 1.5rem | Section spacing |
| `gap-8` / `space-y-8` | 2rem | Large sections |

### Page Layout

```tsx
<main className="min-h-screen bg-gray-50">
  <div className="container mx-auto px-4 py-8">
    <header className="mb-8">
      <h1 className="text-2xl font-bold">My Tasks</h1>
    </header>
    <section className="space-y-6">
      {/* Content */}
    </section>
  </div>
</main>
```

## Dark Mode

```tsx
<div className="
  bg-white dark:bg-gray-800
  text-gray-900 dark:text-gray-100
  border-gray-200 dark:border-gray-700
">
```

## Animation

```tsx
// Fade in
<div className="animate-fadeIn">

// Spin (loading)
<div className="animate-spin">

// Pulse (skeleton)
<div className="animate-pulse bg-gray-200 rounded h-4 w-full">

// Transition
<div className="transition-all duration-200 ease-in-out">
```
