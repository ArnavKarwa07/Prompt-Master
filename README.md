# 🎯 Prompt Master

A **Multi-Agent Prompt Reviewer & Optimizer** SaaS built with a lean, database-light architecture. Uses LangGraph's Supervisor pattern to route prompts to specialized AI agents for evaluation and optimization.

![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-purple)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-Next.js%2015-black)
![AI](https://img.shields.io/badge/AI-LangGraph%20%2B%20Groq-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## 🏃 Quick Start (Windows)

**One-Click Start:** Double-click `start.bat` to launch both servers!

Or run individually:

```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Access:**

- 🌐 Frontend: http://localhost:3000
- 🔧 API Docs: http://localhost:8000/docs
- ❤️ Health Check: http://localhost:8000/health

## ✨ Features

- **🤖 Multi-Agent System**: Specialized agents for coding, creative writing, and data analysis
- **🎯 Intelligent Routing**: LangGraph Supervisor automatically routes to the best agent
- **📊 Prompt Scoring**: 0-100 score with detailed rubric breakdown
- **✨ Optimization**: AI-rewritten prompts for better results
- **👤 Guest Mode**: Try without signing up (stateless, no storage)
- **💾 User Mode**: Save projects and track prompt history
- **📁 Context Files**: Upload documents to enhance optimization
- **🔒 Secure Auth**: Clerk authentication

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Guest Mode  │  │  Dashboard  │  │  Project Manager    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 LangGraph Workflow                    │   │
│  │  ┌──────────┐   ┌─────────┐   ┌───────────────────┐  │   │
│  │  │Supervisor│──▶│   RAG   │──▶│  Specialized      │  │   │
│  │  │  Node    │   │  Node   │   │  Agent Nodes      │  │   │
│  │  └──────────┘   └─────────┘   │  ├─ Coding        │  │   │
│  │                               │  ├─ Creative      │  │   │
│  │                               │  ├─ Analyst       │  │   │
│  │                               │  └─ General       │  │   │
│  │                               └───────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Supabase                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  PostgreSQL │  │   Storage   │  │    Vectors          │  │
│  │  (Lean DB)  │  │   (Files)   │  │    (RAG)            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Supabase account
- Clerk account
- Groq API key

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/prompt-master.git
cd prompt-master
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your Clerk keys
```

### 4. Database Setup

1. Create a new Supabase project
2. Run the SQL from `supabase/schema.sql` in the SQL Editor
3. Create a storage bucket named `user-files` (private)
4. Apply storage policies from `supabase/storage-policies.md`

### 5. Run the Application

**Backend:**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` to use the app!

## 📁 Project Structure

```
prompt-master/
├── backend/
│   ├── app/
│   │   ├── agents/           # Specialized AI agents
│   │   │   ├── base_agent.py
│   │   │   ├── coding_agent.py
│   │   │   ├── creative_agent.py
│   │   │   ├── analyst_agent.py
│   │   │   └── general_agent.py
│   │   ├── api/              # FastAPI routes
│   │   │   ├── routes/
│   │   │   │   ├── prompts.py
│   │   │   │   └── projects.py
│   │   │   └── models.py
│   │   ├── core/             # Config, auth, database
│   │   │   ├── config.py
│   │   │   ├── auth.py
│   │   │   └── supabase_client.py
│   │   ├── graph/            # LangGraph workflow
│   │   │   ├── workflow.py
│   │   │   ├── supervisor.py
│   │   │   └── rag_node.py
│   │   ├── services/         # Business logic
│   │   │   └── ingestion.py
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   ├── sign-in/
│   │   │   └── sign-up/
│   │   ├── components/       # React components
│   │   │   ├── ui/           # Shadcn components
│   │   │   ├── prompt-optimizer.tsx
│   │   │   ├── score-card.tsx
│   │   │   └── optimized-prompt.tsx
│   │   ├── lib/              # Utilities
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── middleware.ts
│   ├── package.json
│   └── .env.example
└── supabase/
    ├── schema.sql            # Database schema
    └── storage-policies.md   # Storage bucket policies
```

## 🤖 Agent Types

| Agent        | Specialization                          | Use Case                          |
| ------------ | --------------------------------------- | --------------------------------- |
| **Coding**   | Code generation, debugging, refactoring | "Write a Python function that..." |
| **Creative** | Storytelling, marketing, content        | "Create a blog post about..."     |
| **Analyst**  | Data analysis, research, reports        | "Analyze this data and..."        |
| **General**  | Everything else                         | General-purpose prompts           |

## 📊 Scoring Rubric

Each agent uses a specialized rubric. Example for Coding Agent:

| Criteria             | Weight | Description                  |
| -------------------- | ------ | ---------------------------- |
| Language Specificity | 15%    | Programming language clarity |
| Context Completeness | 20%    | Dependencies, frameworks     |
| Requirements Clarity | 20%    | Functional requirements      |
| Constraints          | 15%    | Performance, style           |
| Error Handling       | 15%    | Edge cases addressed         |
| Output Format        | 15%    | Expected code structure      |

## 💾 Lean Storage Strategy

This project is designed for **Supabase Nano tier (<500MB)**:

1. **No Content Duplication**: Files stored in Storage, only vectors + metadata in DB
2. **Transient Processing**: Guest mode stores nothing
3. **Summary Storage**: Store chunk summaries (255 chars), not full text
4. **History Limits**: Auto-cleanup keeps last 50 prompts per project
5. **Vector Efficiency**: Optimized chunk sizes and IVFFlat indexing

## 🔧 API Endpoints

### Prompts

- `POST /api/v1/prompts/optimize` - Optimize a prompt
- `GET /api/v1/prompts/agents` - List available agents
- `POST /api/v1/prompts/analyze-only` - Quick classification only

### Projects (Authenticated)

- `GET /api/v1/projects` - List user's projects
- `POST /api/v1/projects` - Create a project
- `GET /api/v1/projects/{id}` - Get project details
- `DELETE /api/v1/projects/{id}` - Delete a project
- `GET /api/v1/projects/{id}/history` - Get prompt history
- `POST /api/v1/projects/{id}/upload` - Upload context file

## 🔐 Environment Variables

### Backend (.env)

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
CLERK_SECRET_KEY=your_clerk_secret
CLERK_JWKS_URL=https://your-clerk.clerk.accounts.dev/.well-known/jwks.json
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 🛣️ Roadmap

- [ ] Add embedding generation for RAG
- [ ] Implement vector similarity search
- [ ] Add prompt templates library
- [ ] Support for more file types
- [ ] Batch prompt processing
- [ ] Export/import projects
- [ ] Team collaboration features

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---
