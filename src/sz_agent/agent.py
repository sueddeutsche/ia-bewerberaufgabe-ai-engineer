"""LangChain agent with an article search tool."""

import os

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from sz_agent.store import vector_store

CHAT_MODEL = os.getenv("SZ_CHAT_MODEL", "anthropic:claude-sonnet-5-5")
NO_RESULTS = "Leider keine Inhalte gefunden"

SYSTEM_PROMPT = f"""Du bist ein Assistent für Leser:innen der Süddeutschen Zeitung.
Beantworte ihre Fragen auf Grundlage der Artikel, die dir vorliegen, und nur auf dieser Grundlage.
Nutze dazu immer das Werkzeug `search_articles`, gegebenenfalls mehrfach mit unterschiedlichen Suchbegriffen.
Fasse die relevanten Informationen knapp zusammen und nenne die Titel der verwendeten Artikel als Quellen.
Verwende kein Wissen, das nicht aus den gefundenen Artikeln stammt.
Wenn du nichts inhaltlich Relevantes findest, antworte nur '{NO_RESULTS}'."""


@tool
def search_articles(query: str) -> str:
    """Durchsucht die SZ-Artikel semantisch und liefert die relevantesten Textausschnitte."""
    results = vector_store.similarity_search(query, k=5)
    if not results:
        return "Keine Treffer."
    return "\n\n---\n\n".join(
        f"Titel: {d.metadata.get('title')}\nDatum: {d.metadata.get('date')}\n"
        f"URL: {d.metadata.get('url')}\n\n{d.page_content}"
        for d in results
    )


agent = create_agent(
    model=CHAT_MODEL,
    tools=[search_articles],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
)


def ask(question: str, thread_id: str = "default") -> str:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return result["messages"][-1].text
