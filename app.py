import os

import uvicorn
import yaml
from chainlit.utils import mount_chainlit
from fastapi import FastAPI

from src.api import public, redirect_middleware, router


def setup_logging(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f.read())
    return config


app = FastAPI()

# Register middleware
app.middleware("http")(redirect_middleware)

# Include the API router in the app
app.include_router(router, prefix="/api")

# Include /public directory for static files
app.mount("/public", public, name="public")

ENDPOINTS = {route.name: route.path for route in app.routes}

# Include Chainlit frontend
mount_chainlit(app=app, target="src/frontend.py", path="/chatbot")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get("HOST"),
        port=int(os.environ.get("PORT")),
        reload=bool(os.environ.get("RELOAD_FLAG")),
    )
