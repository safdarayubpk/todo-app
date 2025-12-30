# Todo App - Multi-Phase Development

A progressive todo application demonstrating evolution from console to full-stack with AI integration.

## Current Phase: Phase III - AI-Powered Chatbot

### Features

#### Core Task Management
- Add, view, update, delete tasks
- Toggle completion status
- Multi-user support with authentication

#### AI Chat Assistant
- Natural language task management
- Conversational interface at `/chat`
- Real-time sync with task list
- Supported commands:
  - "Add a task to buy groceries"
  - "Show my tasks"
  - "Mark groceries as done"
  - "Delete the groceries task"
  - "Rename task X to Y"

### Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 15, React, Tailwind CSS |
| Backend | FastAPI, SQLModel, Python 3.11+ |
| Database | Neon PostgreSQL |
| Auth | Better Auth with JWT |
| AI | OpenAI Agents SDK |
| Chat UI | Custom React with SSE streaming |

## Project Structure

```
todoapp/
├── frontend/                # Next.js frontend
│   ├── app/
│   │   ├── chat/           # AI chat page
│   │   ├── dashboard/      # Task dashboard
│   │   └── api/            # API routes
│   └── components/
│       ├── chat/           # Chat components
│       └── tasks/          # Task components
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── chatkit/        # AI chatbot module
│   │   └── routes/         # API routes
│   └── database.py         # DB connection
└── specs/                   # Feature specifications
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+ with UV
- OpenAI API key
- Neon PostgreSQL database

### Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL
# - OPENAI_API_KEY
# - CHATKIT_SECRET_KEY

# Run server
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your settings

# Run development server
npm run dev
```

### Access the Application

- Dashboard: http://localhost:3000/dashboard
- Chat Assistant: http://localhost:3000/chat
- API Docs: http://localhost:8000/docs

## Development Phases

### Phase I: Console Application
- In-memory storage
- Python CLI interface
- Basic CRUD operations

### Phase II: Full-Stack Web App
- Next.js frontend
- FastAPI backend
- PostgreSQL database
- Better Auth authentication
- Multi-user support

### Phase III: AI Chatbot (Current)
- OpenAI Agents SDK integration
- Natural language task management
- Real-time streaming responses
- Chat/task list sync

### Phase IV-V: (Planned)
- Kubernetes deployment
- Event-driven architecture
- Advanced AI features

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://...
BETTER_AUTH_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
OPENAI_API_KEY=sk-...
CHATKIT_SECRET_KEY=your-secret-key
```

### Frontend (.env.local)
```bash
BETTER_AUTH_SECRET=...
DATABASE_URL=postgresql://...
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_CHATKIT_URL=http://localhost:8000/chatkit
```

## License

MIT
