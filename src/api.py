# Create a fastapi app and define the routes
import logging
from pathlib import Path
from typing import Dict, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.chat import ChatBot
from src.health import health_check

logger = logging.getLogger(__name__)

chat: ChatBot = ChatBot()


class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    role: str
    content: str
    context: str = ""


# create router
router = APIRouter()
internal_router = APIRouter()


@router.post("/generate_moderated", tags=["Chatbot"])
async def moderated(message: Message) -> Message:
    """Receive a user message and return a bot message using the moderated chatbot."""
    logger.info(f"API :: Received message: {message}")
    user_message = message.model_dump()
    bot_message = await chat.generate_moderated_message(user_message)
    return Message(**bot_message)


@router.post("/generate_unmoderated", tags=["Chatbot"])
async def unmoderated(message: Message):
    """Receive a list of user messages and return a bot message using the unmoderated chatbot."""
    logger.info(f"API :: Received message: {message}")
    user_message = message.model_dump()
    bot_message = await chat.generate_unmoderated_message(user_message)
    return Message(**bot_message)


@router.get("/history", tags=["Conversation History"])
def history() -> List:
    return chat.get_history()


@router.post("/clear", tags=["Conversation History"])
def clear():
    chat.clear_history()
    return {"status": "success"}


@router.get("/healthz", tags=["Health"])
async def healthz():
    return health_check()


@router.get("/health", tags=["Health"])
async def health():
    return health_check(details=True)


# Use public endpoint for static files
public_directory = Path(__file__).parent.parent / "public"
public = StaticFiles(directory=str(public_directory))


# Define redirecting middleware
async def redirect_middleware(request: Request, call_next):
    if request.url.path == "/":
        # Redirect to the UI path
        return RedirectResponse(url="/chatbot")
    return await call_next(request)
