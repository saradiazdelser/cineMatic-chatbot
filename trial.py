
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.streaming import StreamingHandler
import asyncio
from pathlib import Path

async def main():

    path_to_config = str(Path().cwd() / "src" / "config")
    config = RailsConfig.from_path(str(path_to_config))

    rails = LLMRails(config, verbose=False)

    history = [{"role": "user", "content": "What is the capital of France?"}]

    streaming_handler = StreamingHandler()

    print("HERE")

    
    async def process_tokens():
        async for chunk in streaming_handler:
            print(f"CHUNK: {chunk}")
            # Or do something else with the token

    asyncio.create_task(process_tokens())
    
    result = await rails.generate_async(
        messages=history, streaming_handler=streaming_handler
    )
    print(result)

    print("EXIT")
asyncio.run(main())