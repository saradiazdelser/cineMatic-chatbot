from nemoguardrails import LLMRails  # The NeMo railing class

from src.config.actions import retrieve_information


def init(app: LLMRails):
    # Register the custom `retrieve_information` action and overwrite the default one
    app.register_action(retrieve_information, "retrieve_information")
