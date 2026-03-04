# Installation

DocForge can be installed using Docker (recommended for most users), pip, or from source.

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Node.js | 22+ |
| npm | 10+ |
| Docker (optional) | 24+ |

## Docker (Recommended)

The fastest way to get DocForge running is with Docker Compose. This starts both the backend API server and the frontend dev server with a single command.

```bash
git clone https://github.com/m-chimiste/docforge.git
cd docforge
docker compose up
```

The application will be available at:

- **Frontend:** `http://localhost:5173`
- **Backend API:** `http://localhost:8000`
- **API docs (Swagger):** `http://localhost:8000/docs`

## pip Install

Install the backend package from PyPI:

```bash
pip install docforge
```

This installs the `docforge` CLI and the Python backend. You can then run the API server with:

```bash
docforge  # or: uvicorn main:app --reload
```

## From Source

### Backend

DocForge uses conda/miniforge for Python environment management:

```bash
git clone https://github.com/m-chimiste/docforge.git
cd docforge

# Create and activate conda environment
conda create -n docforge python=3.12
conda activate docforge

# Install backend in editable mode with dev dependencies
cd backend
pip install -e ".[dev]"
```

### Frontend

```bash
cd frontend
npm install
```

### Running the Development Servers

Start the backend and frontend dev servers in separate terminals:

```bash
# Terminal 1: Backend (hot reload on :8000)
conda activate docforge
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend (hot reload on :5173, proxies /api to :8000)
cd frontend
npm run dev
```

The frontend development server proxies API requests to the backend automatically.

## Verifying the Installation

Once both servers are running, open `http://localhost:5173` in your browser. You should see the DocForge projects page.

You can also verify the backend is running by hitting the API directly:

```bash
curl http://localhost:8000/api/v1/projects
```

This should return an empty JSON array `[]` if no projects have been created yet.

## LLM Configuration (Optional)

DocForge is fully functional without any LLM API keys. If you want to enable LLM-powered content generation, set the appropriate environment variable for your provider:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Local models (Ollama, LM Studio)
# No API key needed -- just configure the endpoint in project settings
```

See [LLM Configuration](user-guide/llm-config.md) for detailed provider setup instructions.

## Upgrading

### Docker

```bash
git pull
docker compose build
docker compose up
```

### pip

```bash
pip install --upgrade docforge
```

### From Source

```bash
git pull
cd backend && pip install -e ".[dev]"
cd ../frontend && npm install
```
