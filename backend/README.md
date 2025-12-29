---
title: Todo App API
emoji: ✅
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Todo App Backend

FastAPI backend for multi-user Todo application.

## API Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/tasks` - List user's tasks
- `POST /api/v1/tasks` - Create a task
- `PUT /api/v1/tasks/{id}` - Update a task
- `DELETE /api/v1/tasks/{id}` - Delete a task
- `PATCH /api/v1/tasks/{id}/toggle` - Toggle task completion

## Environment Variables

Set these in Hugging Face Space secrets:

- `DATABASE_URL` - Neon PostgreSQL connection string (with +asyncpg)
- `BETTER_AUTH_URL` - Frontend URL for JWKS verification
- `CORS_ORIGINS` - Allowed CORS origins
# Trigger rebuild 1766984772
