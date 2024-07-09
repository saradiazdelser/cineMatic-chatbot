import uvicorn
import yaml
from chainlit.utils import mount_chainlit
from fastapi import FastAPI

from src.api import public, router_api


def setup_logging(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f.read())
    return config


app = FastAPI()

# Include the API router in the app
app.include_router(router_api, prefix="/api")

# Include /public directory for static files
app.mount("/public", public, name="public")

# Include Chainlit frontend
mount_chainlit(app=app, target="src/frontend.py", path="/chatbot")


if __name__ == "__main__":
    uvicorn.run(app, log_config=setup_logging("src/logging.yaml"))
