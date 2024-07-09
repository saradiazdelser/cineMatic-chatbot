import logging
from typing import Optional

import requests
from langchain.llms import BaseLLM
from nemoguardrails.actions.actions import ActionResult

logger = logging.getLogger(__name__)


def format_chat_history(chat_history: list) -> str:
    """Format the chat history into a single string."""
    try:
        messages = [
            f'{str(item["role"]).title()}: {item["content"]}' for item in chat_history
        ]
    except:
        messages = []
    return "\n".join(messages)


async def retrieve_information(
    context: Optional[dict] = None,
    llm: Optional[BaseLLM] = None,
    rag_prompt: Optional[str] = None,
    chat_history: Optional[list] = [],
) -> ActionResult:
    """Retrieve relevant knowledge chunks and update the context."""
    # Retrieve the user message and bot messages and RAG prompt
    messages = format_chat_history(chat_history)
    # rag_prompt = rag_prompt.format(conversation=messages))
    # logger.info(f"RAG:: Reword prompt: {rag_prompt}")

    context_updates = {}

    # # # Generate a rephrased version of the user message for search
    # response = await llm.agenerate(prompts=[rag_prompt])
    # search_message = response.generations[0][0].text
    search_message = messages
    logger.info(f"RAG:: Reword response: {search_message}")

    chunks = await __retrieve_relevant_chunks(text=search_message)
    if chunks != []:
        context_updates["relevant_chunks"] = "\n".join(chunks)
    else:
        # Keep the existing relevant_chunks if we have them
        context_updates["relevant_chunks"] = context.get("relevant_chunks", "")

    logger.debug(f"RAG:: Response: {context_updates['relevant_chunks']}")

    return ActionResult(
        return_value=context_updates["relevant_chunks"],
        context_updates=context_updates,
    )


async def __retrieve_relevant_chunks(text: str):
    url = "http://localhost:6000/search"
    headers = {"Content-Type": "application/json", "accept": "application/json"}
    body = {
        "text": text,
        "limit": 1,
        "threshold": 0.75,
        "indexes": ["imbd_movies"],
    }
    response = requests.post(url, headers=headers, json=body)

    documents = [item["document"] for item in response.json()]
    return documents
