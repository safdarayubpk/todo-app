---
name: jwt-auth-integrator
description: This skill should be used when the user needs to implement or modify authentication logic, including Better Auth setup in Next.js frontend, JWT token handling, protected routes, current_user dependency in FastAPI backend, password hashing, or user isolation patterns. Triggers automatically for requests involving "add authentication", "implement login", "signup flow", "protect routes", "JWT tokens", "user sessions", or multi-user data separation in the Todo app.
allowed-tools: Read, Write, Grep, Bash
---

# JWT Auth Integrator

Implement robust JWT-based authentication for full-stack Next.js + FastAPI applications following project constitution and Spec-Driven Development principles.

## Quick Start

Generate auth scaffolding:

```bash
python3 .claude/skills/jwt-auth-integrator/scripts/generate_auth.py --output-dir .
```

Or copy templates from `assets/` and customize manually.

## Implementation Rules

### Frontend (Next.js with Better Auth)

- Configure Better Auth with JWT strategy
- Create protected routes with redirect for unauthenticated users
- Provide AuthProvider context wrapper
- Implement signup/login forms with error feedback
- Store JWT tokens securely (httpOnly cookies preferred)
- Handle token refresh when needed

### Backend (FastAPI)

- Create JWT dependency for `current_user` extraction
- Verify tokens and raise 401 on invalid/expired
- Use password hashing (bcrypt via passlib)
- Filter all database queries by `current_user.id` for isolation
- Implement auth routes: `/signup`, `/login`, `/me`

### Security Requirements

- Never store plain passwords
- Use environment variables for secrets (`JWT_SECRET_KEY`, etc.)
- Include proper error messages without leaking sensitive details
- Follow OWASP authentication best practices
- Use TypeScript types for user models on frontend

## Output Format

Output complete code files with full relative paths:

**Backend:**
- `backend/app/auth.py` - JWT utilities and password hashing
- `backend/app/dependencies.py` - FastAPI dependencies (get_current_user)
- `backend/app/routes/auth.py` - Auth endpoints
- `backend/app/models/user.py` - User model

**Frontend:**
- `frontend/lib/auth.ts` - Better Auth configuration
- `frontend/components/AuthProvider.tsx` - Auth context provider
- `frontend/app/(auth)/login/page.tsx` - Login page
- `frontend/app/(auth)/signup/page.tsx` - Signup page

## Additional Resources

### Reference Files

Consult for detailed patterns and code examples:
- **`references/backend-auth-patterns.md`** - FastAPI JWT, password hashing, dependencies
- **`references/frontend-auth-patterns.md`** - Better Auth, protected routes, forms

### Template Files

Copy and customize from `assets/`:
- **`assets/backend/auth.py`** - JWT utilities template
- **`assets/backend/dependencies.py`** - Current user dependency
- **`assets/backend/routes/auth.py`** - Auth routes template
- **`assets/frontend/AuthProvider.tsx`** - Auth context template
- **`assets/frontend/LoginForm.tsx`** - Login form template

### Scripts

- **`scripts/generate_auth.py`** - Scaffolds complete auth system

## Constraints

- Reference the global constitution for security and code quality standards
- Do not add features outside the current spec
- Keep changes minimal and focused on authentication
