import logging

import chainlit as cl


from src import guardrails as guardrails


logging.basicConfig(level=logging.DEBUG)

rails = guardrails.initialize_guardrails(verbose=True)


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message  # called every time a user sends a message
async def main(message: cl.Message):
    """Receive a user message and return a bot message"""

    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    bot_message = rails.generate(messages=message_history)
    # Send bot message
    msg = cl.Message(content=bot_message["content"])
    await msg.send()
