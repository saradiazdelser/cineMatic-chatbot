# Create a fastapi app and define the routes
import logging
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from src import guardrails as guardrails
from src.guardrails import LLMRails

app = FastAPI()
logger = logging.getLogger(__name__)

rails: LLMRails = guardrails.initialize_guardrails()


class Message(BaseModel):
    role: str
    content: str


@app.post("/generate")
async def generate(messages: List[Message]):
    """Receive a list of user messages and return a bot message"""
    logger.info(f"API:: Received messages: {messages}")
    last_user_message = messages[-1].model_dump()
    messages = [msg.model_dump() for msg in messages[:-1] if msg]
    _, bot_message = await guardrails.generate_message(
        last_user_message, rails, messages
    )
    return bot_message
