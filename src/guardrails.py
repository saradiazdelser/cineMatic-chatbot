import logging
from pathlib import Path
from typing import Dict

from nemoguardrails import LLMRails, RailsConfig

logger = logging.getLogger(__name__)


def filter_choose(cannot_answer: list):
    """Randomly choose and option from the given list"""
    try:
        import random

        return random.choice(cannot_answer)
    except:
        return ""


def post_processing(text):
    # Encode the string to UTF-8 bytes, ignoring errors
    utf8_encoded_text = text.encode("utf-8", "ignore")
    # Decode the bytes back to a UTF-8 string
    cleaned_text = utf8_encoded_text.decode("utf-8")
    return cleaned_text


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
    rails = LLMRails(config, verbose=True)

    # Register custom context variables
    rails.register_action_param("rag_prompt", config.custom_data["rag_prompt"])

    rails.register_prompt_context("cannot_answer", config.bot_messages["cannot answer"])
    rails.register_filter("choose", filter_choose)

    logger.info("Successfully intialized guardrails")

    return rails


async def generate_message(
    user_message: Dict[str, str], rails: LLMRails, chat_history: list = []
):
    """Generate a bot message based on the user message"""
    # Save user message to history
    chat_history.append(user_message)

    # Generate bot message
    rails.register_action_param("chat_history", chat_history)
    response = await rails.generate_async(messages=chat_history, return_context=True)
    bot_message = response[0]

    bot_message["content"] = post_processing(bot_message["content"])

    # Save bot message to history
    chat_history.append(bot_message)

    # clean
    return chat_history, bot_message
