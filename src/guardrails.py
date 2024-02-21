import logging

from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.streaming import StreamingHandler
from pathlib import Path


def initialize_guardrails(path_to_config:Path=Path().cwd() / "src" / "config", verbose:bool=False)-> LLMRails:
    """Load configuration and initialize rails"""
    try:
        if not path_to_config.exists():
            raise(ValueError(f"Path_to_config: {path_to_config} does NOT exist"))
    except Exception as e:
        logging.error(e)
        exit(0)

    config = RailsConfig.from_path(str(path_to_config))
    
    streaming_handler = None
    
    try:
        if config.streaming:
            streaming_handler = StreamingHandler()    
    
    except:
        logging.info("No streaming")    
    
    rails = LLMRails(config, verbose=verbose)
    # test
    # _ = rails.generate(messages=[{"role": "user", "content": "Hi there!"}])
    logging.info('Successfully intialized guardrails')
    
    return rails, streaming_handler
