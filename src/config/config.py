from nemoguardrails import LLMRails  # The NeMo railing class

from src.config.actions import retrieve_relevant_chunks


def init(app: LLMRails):
    # Register the custom `retrieve_relevant_chunks` action
    app.register_action(retrieve_relevant_chunks, "retrieve_relevant_chunks")
