# Create a fastapi app and define the routes
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.chat import Chat
from src.health import health_check

app = FastAPI()
logger = logging.getLogger(__name__)

chat = Chat()


class Message(BaseModel):
    role: str
    content: str


# create router
router_api = APIRouter()


@router_api.post("/generate_moderated")
async def generate(messages: List[Message]):
    """Receive a list of user messages and return a bot message using the moderated chatbot"""
    logger.info(f"API:: Received messages: {messages}")
    last_user_message = messages[-1].model_dump()
    messages = [msg.model_dump() for msg in messages[:-1] if msg]
    _, bot_message = await chat.generate_moderated_message(last_user_message, messages)
    return bot_message


@router_api.post("/generate_unmoderated")
async def generate(messages: List[Message]):
    """Receive a list of user messages and return a bot message using the unmoderated chatbot"""
    logger.info(f"API:: Received messages: {messages}")
    last_user_message = messages[-1].model_dump()
    messages = [msg.model_dump() for msg in messages[:-1] if msg]
    _, bot_message = await chat.generate_unmoderated_message(
        last_user_message, messages
    )
    return bot_message


@router_api.get("/health")
async def health():
    return health_check()


# Use public endpoint for static files
public_directory = Path(__file__).parent.parent / "public"
public = StaticFiles(directory=str(public_directory))


# Define redirecting middleware
async def redirect_middleware(request: Request, call_next):
    if request.url.path == "/":
        # Redirect to the UI path
        return RedirectResponse(url="/chatbot")
    return await call_next(request)
