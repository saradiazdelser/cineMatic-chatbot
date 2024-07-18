import logging
from typing import Optional

import requests
from langchain.llms import BaseLLM
from nemoguardrails.actions.actions import ActionResult

from src.settings import RETRIEVAL_ENDPOINT

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
    context: Optional[dict] = {},
    llm: Optional[BaseLLM] = None,
    chat_history: Optional[list] = [],
) -> ActionResult:
    """Retrieve relevant knowledge chunks and update the context."""
    context_updates = {}

    # Format chat history into a single string
    messages = format_chat_history(chat_history)
    logger.info(f"RAG :: Request: {str(messages)}")

    try:
        chunks = await __retrieve_relevant_chunks(text=str(messages))
    except Exception as e:
        logger.error(f"RAG :: Failed to retrieve relevant chunks: {str(e)}")
        chunks = []
    if chunks != []:
        context_updates["relevant_chunks"] = "\n".join(chunks)
    else:
        # Keep the existing relevant_chunks if we have them
        context_updates["relevant_chunks"] = context.get("relevant_chunks", None)

    logger.info(f"RAG :: Response: {str(context_updates['relevant_chunks'])}")

    return ActionResult(
        return_value=context_updates["relevant_chunks"],
        context_updates=context_updates,
    )


async def __retrieve_relevant_chunks(text: str):
    url = RETRIEVAL_ENDPOINT
    headers = {"Content-Type": "application/json", "accept": "application/json"}
    body = {
        "text": text,
        "limit": 1,
        "threshold": 0.75,
        "indexes": ["imbd_movies"],
    }
    response = requests.post(url, headers=headers, json=body)

    documents = [
        str(item["document"]).strip()
        for item in response.json()
        if str(item["document"]).strip()
    ]
    return documents
