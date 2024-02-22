import logging
import chainlit as cl

from src import guardrails as guardrails

logging.basicConfig(level=logging.DEBUG)
rails = guardrails.initialize_guardrails(verbose=True)


@cl.on_message  # called every time a user sends a message
async def main(message: cl.Message):
    """Receive a user message and return a bot message"""

    message_history = []
    message_history.append({"role": "user", "content": message.content})

    bot_message = rails.generate(messages=message_history)

    # Send bot message
    msg = cl.Message(content=bot_message["content"])
    await msg.send()
