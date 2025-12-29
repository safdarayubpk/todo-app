# Task UI Pattern Generator

## Description

This skill should be used when the user needs to generate or modify UI patterns for displaying, listing, or interacting with tasks in the frontend. It provides modular, accessible, and Tailwind-styled React components following best practices for task-centric UIs. Applicable contexts include task lists, task cards, completion toggles, inline editing, drag-and-drop reordering, and task filtering interfaces.

## Body

Generate task-focused UI components for Next.js applications using TypeScript and Tailwind CSS. Follow these principles:

**Component Architecture:**
- Create modular, composable task components
- Separate presentational and container components
- Use proper TypeScript interfaces for Task data
- Follow React Server Components patterns where applicable

**Task-Specific Patterns:**
- TaskItem: Individual task with completion toggle, title, actions
- TaskList: Virtualized list for performance with many tasks
- TaskFilters: Filter by status (all/active/completed)
- TaskStats: Display completion progress and counts
- InlineEditor: Click-to-edit task titles
- TaskActions: Edit, delete, priority controls

**Accessibility Requirements:**
- Proper ARIA roles for checkboxes and lists
- Keyboard navigation (Enter to toggle, Tab to navigate)
- Screen reader announcements for state changes
- Focus management after actions

**Styling Conventions:**
- Use Tailwind utility classes exclusively
- Support dark mode with `dark:` variants
- Consistent spacing (gap-2, p-4, etc.)
- Transition animations for state changes

See `references/` for detailed patterns and `assets/` for complete component templates.
