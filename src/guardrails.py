import logging

from nemoguardrails import LLMRails, RailsConfig


def initialize_guardrails(path_to_config:str="/home/sdiaz/Projects/guardrails-demo/src/config",verbose:bool=False)-> LLMRails:
    """Load configuration and initialize rails"""
    # TODO add exception handling (if config is not a dir)
    config = RailsConfig.from_path(path_to_config)
    rails = LLMRails(config, verbose=verbose)
    
    # test
    bot_message = rails.generate(messages=[{"role": "user", "content": "Hi there!"}])
    print(bot_message)
    logging.info('Successfully intialized guardrails')
    
    return rails
