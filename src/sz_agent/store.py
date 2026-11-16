"""In-memory vector store holding the articles."""

import json
import os
from pathlib import Path

from langchain.embeddings import init_embeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMBEDDING_MODEL = os.getenv("SZ_EMBEDDING_MODEL", "openai:text-embedding-3-small")

_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

vector_store = InMemoryVectorStore(embedding=init_embeddings(EMBEDDING_MODEL))


def add_articles(articles: list[dict]) -> int:
    """Split articles into chunks and add them to the store. Returns the number of chunks."""
    docs = [
        Document(
            page_content=a["text"],
            metadata={"title": a["title"], "url": a.get("url", ""), "date": a.get("date", "")},
        )
        for a in articles
    ]
    chunks = _splitter.split_documents(docs)
    if chunks:
        vector_store.add_documents(chunks)
    return len(chunks)


def load_articles_from_file(path: str | Path) -> int:
    return add_articles(json.loads(Path(path).read_text(encoding="utf-8")))
