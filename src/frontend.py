import asyncio
from typing import Dict, List

import aiohttp
import chainlit as cl
from chainlit import logger

from src.settings import ENDPOINTS

headers = {
    "Content-Type": "application/json",
    "accept": "application/json",
}


def store_message(message: Dict):
    """Save message to user's chat history."""
    chat_history: dict = cl.user_session.get("messages_history")
    chat_history.update({message["id"]: message})
    cl.user_session.set("messages_history", chat_history)


async def async_post_request(url, json=None) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json) as response:
            return await response.json()


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Moderated",
            markdown_description="Chatbot is moderated using the **NVIDIA NeMo Guardrails** framework.",
            icon="public/chatbot_moderated.svg",
        ),
        cl.ChatProfile(
            name="Unmoderated",
            markdown_description="Chatbot uses no moderation framework. Questions will go directly to the model.",
            icon="public/chatbot_unmoderated.svg",
        ),
    ]

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Iconic Quotes",
            message="Matic, what's a famous quote from 'The Godfather'?",
            icon="/public/quote-left-icon.svg",
            ),

        cl.Starter(
            label="Director's Cinematography",
            message="Hi Matic, what movies has Christopher Nolan directed?",
            icon="/public/video-roll-icon.svg",
            ),
        cl.Starter(
            label="Award-Winning Movies",
            message="Hi Matic, which film won the Best Picture Oscar in 2020?",
            icon="/public/winning-cup-icon.svg",
            ),
        cl.Starter(
            label="Movie Plot",
            message="Matic, whats the movie 'Inception' about?",
            icon="/public/movie-media-player-icon.svg",
            )
        ]

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("messages_history", {})
    _ = await async_post_request(ENDPOINTS["clear"], {})
    logger.info("New Chat")

@cl.action_callback("Show Sources")
async def on_action(action: cl.Action):
    context_text = cl.user_session.get("messages_history").get(action.forId).get("context", "")
    context_element = cl.Text(name="📄 Context", content=context_text)
    await context_element.send(for_id=action.forId)
    await action.remove()

@cl.on_message  # called every time a user sends a message
async def message(message: cl.Message):
    """Receive a user message and return a bot message"""
    # Retrieve user variables
    chat_profile: str = cl.user_session.get("chat_profile")
    user_message = {"role": "user", "content": message.content or ""}
    try:
        # Generate bot message
        url = ENDPOINTS.get(chat_profile.lower())
        bot_message = await async_post_request(url, user_message)
        store_message(bot_message)
        
        # Create chainlit message object
        message = cl.Message(content=bot_message.get("content"), id=str(bot_message.get("id")))
        action_show_sources = cl.Action(
            name="Show Sources", value=message.id, label="📄 Display Sources"
        )
        # Send bot message
        await message.send()
        await action_show_sources.send(for_id=message.id)
        
    except Exception as e:
        logger.error(e)
        await cl.Message(content="Connection Error").send()
