import logging

from src import api

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(levelname)s] %(name)s {%(pathname)s:%(lineno)d} %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "level": "DEBUG",
            "handlers": ["default"],
        },
    },
}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api.app, log_config=log_config)
