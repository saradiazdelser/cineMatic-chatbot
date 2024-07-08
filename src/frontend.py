from typing import List

import chainlit as cl

from src import guardrails as guardrails
from src.guardrails import LLMRails


@cl.on_chat_start
async def on_chat_start():
    rails: LLMRails = guardrails.initialize_guardrails()
    cl.user_session.set("rails", rails)
    cl.user_session.set("chat_history", [])


@cl.on_message  # called every time a user sends a message
async def main(message: cl.Message):
    """Receive a user message and return a bot message"""
    # Retrieve user variables
    chat_history: List = cl.user_session.get("chat_history")
    rails: LLMRails = cl.user_session.get("rails")
    last_user_message = {"role": "user", "content": message.content or ""}

    # Generate a bot message
    new_chat_history, bot_message = await guardrails.generate_message(
        last_user_message, rails, chat_history
    )

    cl.user_session.set("chat_history", new_chat_history)

    await cl.Message(content=bot_message["content"]).send()
