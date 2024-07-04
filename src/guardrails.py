import logging
from pathlib import Path

from nemoguardrails import LLMRails, RailsConfig

logger = logging.getLogger(__name__)


def filter_choose(options: list):
    """Randomly choose and option from the given list"""
    try:
        import random

        return random.choice(options)
    except:
        return ""


def initialize_guardrails(
    path_to_config: Path = Path().cwd() / "src" / "config",
) -> LLMRails:
    """Load configuration and initialize rails"""
    try:
        if not path_to_config.exists():
            raise (ValueError(f"path_to_config: {path_to_config} does NOT exist"))
    except Exception as e:
        logger.error(e)
        exit(0)

    config = RailsConfig.from_path(str(path_to_config))
    rails = LLMRails(config)

    # Register custom context variables
    rails.register_prompt_context("rag_prompt", config.custom_data["rag_prompt"])
    rails.register_prompt_context("cannot_answer", config.bot_messages["cannot answer"])
    rails.register_filter("choose", filter_choose)

    logger.info("Successfully intialized guardrails")

    return rails


async def generate_message(user_message: str, rails: LLMRails, chat_history: list = []):
    """Generate a bot message based on the user message"""
    # Save user message to history
    chat_history.append(user_message)

    # Generate bot message
    rails.register_prompt_context("chat_history", chat_history)
    response = await rails.generate_async(messages=chat_history, return_context=True)
    bot_message = response[0]

    # Save bot message to history
    chat_history.append(bot_message)
    return chat_history, bot_message
