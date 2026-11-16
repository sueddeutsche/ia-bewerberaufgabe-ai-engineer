"""FastAPI server exposing the agent."""

import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from sz_agent.agent import ask
from sz_agent.store import add_articles, load_articles_from_file

ARTICLES_FILE = Path(os.getenv("SZ_ARTICLES_FILE", "data/articles.json"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    if ARTICLES_FILE.exists():
        n = load_articles_from_file(ARTICLES_FILE)
        print(f"Loaded {n} chunks from {ARTICLES_FILE}")
    yield


app = FastAPI(title="SZ Agent", lifespan=lifespan)


class Article(BaseModel):
    title: str
    text: str
    url: str = ""
    date: str = ""


class Question(BaseModel):
    question: str
    thread_id: str | None = None


class Answer(BaseModel):
    answer: str
    thread_id: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/articles")
async def ingest(articles: list[Article]) -> dict:
    n = await run_in_threadpool(add_articles, [a.model_dump() for a in articles])
    return {"articles": len(articles), "chunks": n}


@app.post("/ask", response_model=Answer)
async def ask_endpoint(q: Question) -> Answer:
    thread_id = q.thread_id or str(uuid.uuid4())
    answer = await run_in_threadpool(ask, q.question, thread_id)
    return Answer(answer=answer, thread_id=thread_id)
