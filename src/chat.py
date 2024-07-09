import logging
from pathlib import Path
from typing import Dict, List, Tuple

from huggingface_hub import InferenceClient
from jinja2 import Environment, Template
from nemoguardrails import LLMRails, RailsConfig

from src.config.actions import format_chat_history, retrieve_information
from src.settings import INFERENCE_ENDPOINT

logger = logging.getLogger(__name__)


class Chat:
    def __init__(self):
        self.rails: LLMRails = None
        self.client: InferenceClient = None
        self.prompt_template: Template = None
        self.system_prompt: str = None
        self.initialize_guardrails()
        self.initialize_client()

    @staticmethod
    def post_processing(text: str) -> str:
        # Encode the string to UTF-8 bytes, ignoring errors
        utf8_encoded_text = text.encode("utf-8", "ignore")
        # Decode the bytes back to a UTF-8 string
        cleaned_text = utf8_encoded_text.decode("utf-8")
        return cleaned_text

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

    def initialize_client(self) -> InferenceClient:
        self.client = InferenceClient(model=INFERENCE_ENDPOINT)

    def initialize_guardrails(
        self, path_to_config: Path = Path().cwd() / "src" / "config"
    ) -> LLMRails:
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
        self.rails.register_action_param("rag_prompt", config.custom_data["rag_prompt"])

        logger.info("Successfully initialized guardrails")
        return self.rails

    async def generate_moderated_message(
        self, user_message: Dict[str, str], chat_history: List[Dict[str, str]] = []
    ) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
        """Generate a bot message based on the user message using the NeMo Guardrails framework for moderation.
        Args:
            user_message (Dict[str, str]): User message
            chat_history (List[Dict[str, str]], optional): Chat history. Defaults to [].
        Returns:
            List[Dict[str, str]]: Updated chat history
            Dict[str, str]: Bot message
        """
        # Save user message to history
        chat_history.append(user_message)

        # Generate bot message
        self.rails.register_action_param("chat_history", chat_history)
        response = await self.rails.generate_async(
            messages=chat_history, return_context=True
        )
        bot_message = response[0]

        bot_message["content"] = self.post_processing(bot_message["content"])

        # Save bot message to history
        chat_history.append(bot_message)

        # clean
        return chat_history, bot_message

    async def generate_unmoderated_message(
        self,
        user_message: Dict[str, str],
        chat_history: List[Dict[str, str]] = [],
    ) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
        """Generate a bot message based on the user message using the unmoderated chatbot.
        Args:
            user_message (Dict[str, str]): User message
            chat_history (List[Dict[str, str]], optional): Chat history. Defaults to [].
        Returns:
            List[Dict[str, str]]: Updated chat history
            Dict[str, str]: Bot message
        """
        # Save user message to history
        chat_history.append(user_message)

        # Get RAG
        action_result = await retrieve_information()
        relevant_context: str = action_result.return_value

        # Generate bot message
        prompt = self.prompt_template.render(
            general_instructions=self.system_prompt,
            relevant_context=relevant_context,
            history=format_chat_history(chat_history),
        )
        response = await self.client.text_generation(prompt=prompt)
        response = self.post_processing(response)

        bot_message = {"role": "bot", "content": response}

        # Save bot message to history
        chat_history.append(bot_message)

        # clean
        return chat_history, bot_message
