# SZ-Agent

Minimal LangChain agent that answers reader questions based solely on SZ articles.

- **Agent**: `langchain.agents.create_agent` with one tool `search_articles` (`src/sz_agent/agent.py`)
- **Search / DB**: `InMemoryVectorStore` with embeddings (`src/sz_agent/store.py`) – lost on restart
- **API**: FastAPI (`src/sz_agent/api.py`)

## Setup

```bash
uv sync
export ANTHROPIC_API_KEY=...   # chat model
export OPENAI_API_KEY=...      # embeddings
uv run sz-agent                # http://127.0.0.1:8000/docs
```

Configuration via environment variables:

| Variable | Default |
|---|---|
| `SZ_CHAT_MODEL` | `anthropic:claude-sonnet-5-5` |
| `SZ_EMBEDDING_MODEL` | `openai:text-embedding-3-small` |
| `SZ_ARTICLES_FILE` | `data/articles.json` (loaded at startup) |

## Usage

```bash
# Add articles
curl -X POST localhost:8000/articles -H 'Content-Type: application/json' \
  -d '[{"title": "...", "text": "...", "url": "...", "date": "2026-11-16"}]'

# Ask a question (pass thread_id from the response back in for follow-up questions)
curl -X POST localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question": "Was plant München bei den Radwegen?"}'
```
