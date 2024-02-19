import logging

import chainlit as cl

from src import constants as ct
from src import guardrails as guardrails
from src import utils as ut

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




# @cl.on_message  # this function will be called every time a user inputs a message in the UI
# async def alt_main(message: cl.Message):
#     user_message = message.content
    
#     prompt = ut.generate_prompt(user_message)

#     json = {
#         "text": prompt,
#         **ct.params
#         }
    
#     response = requests.post(ct.generate_url, json=json, stream=True)
#     response.encoding = "utf-8"
    
#     # Send bot message
#     msg = cl.Message(content="")
#     for text in response.iter_content(chunk_size=1, decode_unicode=True):
#         await msg.stream_token(text)

#     await msg.send()

