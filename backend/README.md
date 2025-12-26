# Backend Development Guide

## Getting Started

### Prerequisites

- Python 3.11+
- pip or uv package manager
- Supabase project
- Groq API key
- Clerk account

### Installation

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:

| Variable               | Description               |
| ---------------------- | ------------------------- |
| `GROQ_API_KEY`         | Your Groq API key         |
| `SUPABASE_URL`         | Supabase project URL      |
| `SUPABASE_ANON_KEY`    | Supabase anonymous key    |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `CLERK_SECRET_KEY`     | Clerk secret key          |
| `CLERK_JWKS_URL`       | Clerk JWKS endpoint       |

### Running the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Architecture

### LangGraph Workflow

The multi-agent system uses LangGraph's StateGraph:

```
Entry → Supervisor → RAG → [Agent Selection] → End
                      ↓
            ┌─────────┴─────────┐
            ↓         ↓         ↓         ↓
         Coding   Creative   Analyst   General
```

### Agent Structure

Each agent extends `BaseAgent`:

```python
class CodingAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "coding"

    @property
    def description(self) -> str:
        return "Specializes in code-related prompts..."

    @property
    def system_prompt(self) -> str:
        return "You are an expert..."

    @property
    def rubric(self) -> dict:
        return {
            "criterion": {"weight": 20, "description": "..."},
            # ...
        }
```

### Adding a New Agent

1. Create a new file in `app/agents/`:

```python
# app/agents/my_agent.py
from app.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "my_agent"

    # ... implement required properties
```

2. Register in `app/agents/__init__.py`:

```python
from app.agents.my_agent import MyAgent

AGENT_REGISTRY = {
    # ... existing agents
    "my_agent": MyAgent,
}
```

3. Add to workflow in `app/graph/workflow.py`:

```python
async def my_agent_node(state: GraphState) -> GraphState:
    agent = get_agent("my_agent")
    # ... process state
```

## API Endpoints

### Health Check

```
GET /health
```

Response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents_available": ["coding", "creative", "analyst", "general"]
}
```

### Optimize Prompt

```
POST /api/v1/prompts/optimize
```

Request:

```json
{
  "prompt": "Write code to sort a list",
  "goal": "Generate Python code",
  "force_agent": null,
  "project_id": null
}
```

Response:

```json
{
  "original_prompt": "...",
  "goal": "...",
  "agent": "coding",
  "routing": {
    "confidence": 0.95,
    "reasoning": "Code-related task detected"
  },
  "score": 75,
  "feedback": "The prompt could be more specific...",
  "optimized_prompt": "Write a Python function that..."
}
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

Set these in your hosting platform:

- All variables from `.env.example`
- `DEBUG=false`
- `HOST=0.0.0.0`
