import logging

import chainlit as cl

import asyncio

from src import guardrails as guardrails


logging.basicConfig(level=logging.DEBUG)

rails, streaming_handler = guardrails.initialize_guardrails(verbose=False)

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
    
    if streaming_handler:

        msg = cl.Message(content="")
        await msg.send()
        
        async def process_tokens():
            async for chunk in streaming_handler:
                logging.debug(f"CHUNK: {chunk}")
                # Or do something else with the token
                await msg.stream_token(chunk)

        asyncio.create_task(process_tokens())
        
        message_history.append({"role": "assistant", "content": msg.content})
        await msg.update()
        
        bot_message = await rails.generate_async(
            messages=message_history, streaming_handler=streaming_handler
        )

        msg = cl.Message(content=bot_message["content"])
        await msg.send()

        

    else:
        bot_message = rails.generate(messages=message_history)
        # Send bot message
        msg = cl.Message(content=bot_message["content"])
        await msg.send()
