---
name: nextjs-component-builder
description: This skill should be used when the user needs to generate or modify React components for the Next.js frontend, such as TaskCard, TaskList, AddTaskForm, EditTaskModal, AuthLayout, or LoadingSpinner. Triggers automatically for requests involving "create component", "build UI", "add form", "Next.js pages", "Tailwind styling", "responsive layout", or any UI element displaying or interacting with tasks in the Todo app.
allowed-tools: Read, Write, Grep, Bash
---

# Next.js Component Builder

Generate clean, modern, responsive React components following project constitution and Spec-Driven Development principles.

## Quick Start

Generate a component using the script:

```bash
python3 .claude/skills/nextjs-component-builder/scripts/generate_component.py <ComponentName> --output-dir frontend/src/components
```

Or copy templates from `assets/` and customize manually.

## Generation Rules

Apply these rules when generating components:

- Use Next.js App Router structure (`app/` or `src/app/`)
- Mark components as `'use client'` only when necessary (prefer server components)
- Use Tailwind CSS for styling (mobile-first, responsive)
- Implement proper accessibility (ARIA labels, semantic HTML)
- Use TypeScript with meaningful prop interfaces
- Follow component composition and reusability
- Include loading and error states where appropriate
- Keep components focused and single-responsibility

## Component Patterns

| Component | Purpose |
|-----------|---------|
| TaskCard | Title, description, status indicator, edit/delete buttons |
| TaskList | Grid/table layout, responsive, maps TaskCard |
| AddTaskForm | Form with validation, submit handler |
| EditTaskModal | Modal dialog with form, cancel/save actions |
| AuthLayout | Wrapper for auth pages |
| LoadingSpinner | Reusable loading indicator |

## Output Format

Output complete code files with full relative paths:
- `frontend/src/components/{ComponentName}.tsx` - Component file
- `frontend/src/types/{resource}.ts` - TypeScript interfaces (if needed)

## Additional Resources

### Reference Files

Consult for detailed patterns and code examples:
- **`references/component-patterns.md`** - Server vs client components, composition, accessibility
- **`references/tailwind-conventions.md`** - Styling patterns, responsive design, color system

### Template Files

Copy and customize from `assets/`:
- **`assets/TaskCard.tsx`** - Task display component template
- **`assets/TaskList.tsx`** - List layout template
- **`assets/FormTemplate.tsx`** - Form with validation template
- **`assets/ModalTemplate.tsx`** - Modal dialog template

### Scripts

- **`scripts/generate_component.py`** - Automated component generator

## Constraints

- Reference the global constitution for code quality and UX consistency
- Do not add features outside the current spec
- Keep changes minimal and focused on the requested component
