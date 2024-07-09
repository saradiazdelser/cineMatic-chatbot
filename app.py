import yaml

from src import api


def setup_logging(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f.read())
    return config


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api.app, log_config=setup_logging("src/logging.yaml"))
