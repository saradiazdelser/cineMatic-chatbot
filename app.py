import logging

import chainlit as cl

from src import guardrails as guardrails

logging.basicConfig(level=logging.DEBUG)

rails = guardrails.initialize_guardrails(verbose=True)


@cl.on_message  # called every time a user sends a message
async def main(message: cl.Message):
    """Receive a user message and return a bot message"""
    user_message = message.content
        
    # generate
    bot_message = rails.generate(
        messages=[{"role": "user", "content": user_message}]
    )
    
    # Send bot message
    msg = cl.Message(content=bot_message)
    await msg.send()
