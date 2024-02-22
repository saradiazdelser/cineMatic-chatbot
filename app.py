import logging
import chainlit as cl

from src import guardrails as guardrails

logging.basicConfig(level=logging.DEBUG)
rails = guardrails.initialize_guardrails(verbose=True)

info = rails.explain()
print(info.print_llm_calls_summary())

for call in range(len(info.llm_calls)):
    print(info.llm_calls[call].prompt)
    print(info.llm_calls[call].completion)


@cl.on_message  # called every time a user sends a message
async def main(message: cl.Message):
    """Receive a user message and return a bot message"""

    message_history = []
    message_history.append({"role": "user", "content": message.content})

    bot_message = rails.generate(messages=message_history)

    info = rails.explain()
    print(info.print_llm_calls_summary())

    for call in range(len(info.llm_calls)):
        print(info.llm_calls[call].prompt)
        print(info.llm_calls[call].completion)

    # Send bot message
    msg = cl.Message(content=bot_message["content"])
    await msg.send()
