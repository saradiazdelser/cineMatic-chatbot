# Create a fastapi app and define the routes
import logging
from typing import List

from chainlit.utils import mount_chainlit
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from src import guardrails as guardrails
from src.guardrails import LLMRails
from src.health import health_check

app = FastAPI()
logger = logging.getLogger(__name__)

rails: LLMRails = guardrails.initialize_guardrails()


class Message(BaseModel):
    role: str
    content: str


# create router
router_api = APIRouter()


@app.middleware("http")
async def redirect_middleware(request: Request, call_next):
    if request.url.path == "/":
        # Redirect to the UI path
        return RedirectResponse(url="/chatbot")
    return await call_next(request)


@router_api.post("/generate")
async def generate(messages: List[Message]):
    """Receive a list of user messages and return a bot message"""
    logger.info(f"API:: Received messages: {messages}")
    last_user_message = messages[-1].model_dump()
    messages = [msg.model_dump() for msg in messages[:-1] if msg]
    _, bot_message = await guardrails.generate_message(
        last_user_message, rails, messages
    )
    return bot_message


@router_api.get("/health")
async def health():
    return health_check()


app.include_router(router_api, prefix="/api")

mount_chainlit(app=app, target="src/frontend.py", path="/chatbot")
