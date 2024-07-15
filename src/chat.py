import logging
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List, Tuple

from huggingface_hub import InferenceClient
from jinja2 import Environment, Template
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.llm.output_parsers import verbose_v1_parser

from src.config.actions import format_chat_history, retrieve_information
from src.settings import INFERENCE_ENDPOINT

logger = logging.getLogger(__name__)

def verbose_v2_parser(s: str):
    text = verbose_v1_parser(s)
    return text.lower()

class ChatBot:
    def __init__(self, memory_size: int = 10):
        self.rails: LLMRails = None
        self.client: InferenceClient = None
        self.prompt_template: Template = None
        self.system_prompt: str = None
        self.history: Deque[Dict] = deque(maxlen=memory_size)
        self.initialize_guardrails()
        self.initialize_client()

    def __str__(self) -> str:
        return (
            "ChatBot(rails={}, client={}, prompt_template={}, system_prompt={})".format(
                str(self.rails),
                str(self.client),
                str(self.prompt_template),
                str(self.system_prompt),
            )
        )

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def post_processing(text: str) -> str:
        # Encode the string to UTF-8 bytes, ignoring errors
        utf8_encoded_text = text.encode("utf-8", "ignore")
        # Decode the bytes back to a UTF-8 string
        cleaned_text = utf8_encoded_text.decode("utf-8")
        return cleaned_text

    def clear_history(self):
        """Clear conversation history."""
        self.history.clear()
        logger.info("Conversation history cleared.")

    def get_history(self) -> List[Dict]:
        """Get current conversation history."""
        return list(self.history)

    def add_history(self, message: Dict[str, str]):
        """Add message to conversation history."""
        self.history.append(message)

    def build_prompt_from_config(self, config: RailsConfig):
        """Build prompt template from RailsConfig object."""
        self.system_prompt = config.instructions
        generate_bot_message = [
            prompt.content
            for prompt in config.prompts
            if prompt.task == "generate_bot_message"
        ][0]

        # Create a Jinja2 template from the prompt
        # Custom Jinja2 function to ignore filters
        def ignore_missing_filters(value, *args, **kwargs):
            return value

        # Create a custom environment
        env = Environment()

        # Add a fallback for missing filters
        env.filters["colang"] = ignore_missing_filters
        env.filters["verbose_v1"] = ignore_missing_filters

        self.prompt_template = env.from_string(generate_bot_message)
        return

    def initialize_client(self):
        self.client = InferenceClient(model=INFERENCE_ENDPOINT)

    def initialize_guardrails(
        self, path_to_config: Path = Path().cwd() / "src" / "config"
    ):
        """Load configuration and initialize rails"""
        try:
            if not path_to_config.exists():
                raise ValueError(
                    f"Could not find path to guardrails configuration file. '{path_to_config}' does not exist."
                )
        except Exception as e:
            logger.error(e)
            exit(0)

        config = RailsConfig.from_path(str(path_to_config))
        self.build_prompt_from_config(
            config
        )  # Build prompt template for unmoderated chat
        self.rails = LLMRails(config, verbose=True)

        # Register custom context variables
        self.rails.register_action_param(name="rag_prompt", value=config.custom_data["rag_prompt"])
        self.rails.register_output_parser(output_parser=verbose_v2_parser, name="verbose_v2")

        logger.info("Successfully initialized guardrails")
        return

    async def generate_moderated_message(
        self, user_message: Dict[str, str]
    ) -> Dict[str, str]:
        """Generate a bot message based on the user message using the NeMo Guardrails framework for moderation.
        Args:
            user_message (Dict[str, str]): User message
        Returns:
            Dict[str, str]: Bot message
        """
        # Save user message to history
        self.add_history(user_message)
        chat_history = self.get_history()

        # Generate bot message
        self.rails.register_action_param("chat_history", chat_history)
        response = await self.rails.generate_async(
            messages=chat_history, return_context=True
        )
        bot_message = response[0]
        bot_message["content"] = self.post_processing(bot_message["content"])

        # Save bot message to history
        self.add_history(bot_message)

        return bot_message

    async def generate_unmoderated_message(
        self,
        user_message: Dict[str, str],
    ) -> Dict[str, str]:
        """Generate a bot message based on the user message using the unmoderated chatbot.
        Args:
            user_message (Dict[str, str]): User message
        Returns:
            Dict[str, str]: Bot message
        """
        # Save user message to history
        self.add_history(user_message)
        chat_history = self.get_history()

        # Get RAG
        action_result = await retrieve_information(chat_history=chat_history)
        relevant_context: str = action_result.return_value

        # Generate bot message
        prompt = self.prompt_template.render(
            general_instructions=self.system_prompt,
            relevant_context=relevant_context,
            history=format_chat_history(chat_history),
        )

        logger.info(f"Prompt :: {prompt}")
        response = self.client.text_generation(prompt=prompt, max_new_tokens=100)
        response = self.post_processing(response)
        bot_message = {"role": "bot", "content": response}

        # Save bot message to history
        self.add_history(bot_message)

        return bot_message
