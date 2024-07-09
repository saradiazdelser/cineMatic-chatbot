from typing import List

import chainlit as cl

from chat import Chat, LLMRails

chat = Chat()


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Moderated",
            markdown_description="Chatbot is moderated using the NVIDIA **NeMo Guardrails** framework.",
            icon="public/moderated_icon.jpg",
        ),
        cl.ChatProfile(
            name="Unmoderated",
            markdown_description="Chatbot uses no moderation framework. Questions go directly to the model.",
            icon="public/unmoderated_icon.jpg",
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    rails: LLMRails = chat.rails
    cl.user_session.set("rails", rails)
    cl.user_session.set("chat_history", [])


@cl.on_message  # called every time a user sends a message
async def main(message: cl.Message):
    """Receive a user message and return a bot message"""
    # Retrieve user variables
    chat_profile = cl.user_session.get("chat_profile")
    chat_history: List = cl.user_session.get("chat_history")
    last_user_message = {"role": "user", "content": message.content or ""}

    if chat_profile == "Moderated":
        # Generate a bot message
        new_chat_history, bot_message = await chat.generate_moderated_message(
            last_user_message, chat_history
        )

    else:
        new_chat_history, bot_message = await chat.generate_unmoderated_message(
            last_user_message, chat_history
        )
    cl.user_session.set("chat_history", new_chat_history)

    await cl.Message(content=bot_message["content"]).send()
