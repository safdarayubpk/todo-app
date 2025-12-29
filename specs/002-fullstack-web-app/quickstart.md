# Quickstart: Full-Stack Multi-User Web Todo Application

**Feature Branch**: `002-fullstack-web-app`
**Created**: 2025-12-28

## Prerequisites

- Node.js 20+ (for frontend)
- Python 3.11+ with UV (for backend)
- Neon PostgreSQL account (free tier works)
- Git

## Environment Setup

### 1. Clone and Checkout Branch

```bash
cd todoapp
git checkout 002-fullstack-web-app
```

### 2. Create Neon Database

1. Go to [console.neon.tech](https://console.neon.tech)
2. Create a new project (e.g., "todoapp")
3. Copy the connection string (use the asyncpg format)

### 3. Configure Environment Variables

#### Backend (.env)

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.region.neon.tech/todoapp?sslmode=require
JWT_SECRET_KEY=your-secure-secret-key-at-least-32-chars
BETTER_AUTH_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

#### Frontend (.env.local)

```bash
cd frontend
cp .env.example .env.local
```

Edit `frontend/.env.local`:
```env
BETTER_AUTH_SECRET=your-better-auth-secret-at-least-32-chars
DATABASE_URL=postgresql://user:pass@ep-xxx.region.neon.tech/todoapp?sslmode=require
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
uv sync                          # Install dependencies
uv run uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

### Start Frontend (Terminal 2)

```bash
cd frontend
npm install                      # or pnpm install
npm run dev                      # or pnpm dev
```

Frontend will be available at: http://localhost:3000

## Testing the Application

### 1. Register a User

1. Navigate to http://localhost:3000/signup
2. Enter email, username, and password (8+ chars)
3. Click "Sign Up"

### 2. Login

1. Navigate to http://localhost:3000/login
2. Enter your email and password
3. Click "Login"
4. You'll be redirected to the dashboard

### 3. Create Tasks

1. On the dashboard, enter a task title
2. Click "Add Task"
3. Task appears in the list

### 4. Manage Tasks

- **Toggle completion**: Click the checkbox
- **Edit**: Click the edit icon, modify, save
- **Delete**: Click delete icon, confirm

### 5. Test User Isolation

1. Logout (click logout button)
2. Create a second account
3. Login with second account
4. Verify you see an empty task list

## API Testing (cURL Examples)

### Get JWT Token (after login in browser)
```bash
# The JWT is retrieved via Better Auth client
# For direct API testing, use the /api/auth/token endpoint
```

### List Tasks
```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Created via curl"}'
```

### Toggle Task
```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1/toggle \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Delete Task
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Common Issues

### Database Connection Failed
- Check DATABASE_URL format includes `?sslmode=require`
- Verify Neon project is not paused (free tier pauses after inactivity)
- Ensure you're using asyncpg driver: `postgresql+asyncpg://...`

### CORS Errors
- Verify `CORS_ORIGINS` in backend .env includes frontend URL
- Restart backend after changing .env

### JWT Verification Failed
- Ensure `BETTER_AUTH_URL` in backend matches frontend URL
- Check `BETTER_AUTH_SECRET` is set in frontend

### 401 on API Calls
- Session may have expired - try logging out and back in
- Check browser DevTools for cookie presence

## Project Structure

```
todoapp/
├── frontend/
│   ├── app/
│   │   ├── (auth)/login/page.tsx
│   │   ├── (auth)/signup/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── api/auth/[...all]/route.ts
│   │   └── layout.tsx
│   ├── components/
│   ├── lib/auth.ts
│   └── middleware.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── dependencies.py
│   │   └── routes/tasks.py
│   └── database.py
│
└── specs/002-fullstack-web-app/
```

## Next Steps

After verifying the quickstart works:

1. Review the [spec.md](./spec.md) for acceptance criteria
2. Check [data-model.md](./data-model.md) for entity details
3. See [contracts/openapi.yaml](./contracts/openapi.yaml) for full API spec
4. Run `/sp.tasks` to generate implementation tasks
