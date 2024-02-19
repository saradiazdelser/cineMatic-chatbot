def generate_prompt(user_message: str) ->str:
    """Generate prompt with context from question"""
    # TODO context retrieval
    # TODO build prompt (add instructions)
    # TODO return prompt
    prompt = f"[INST] Answer the following question: {user_message}. Respond in a natural way, like you are having a conversation with a friend.[/INST]"
        
    return prompt
