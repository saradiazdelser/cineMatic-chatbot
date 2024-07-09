import argparse

# set logging level
import logging
import sys
from pathlib import Path

import uvicorn

logging.basicConfig(level=logging.DEBUG)

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

parser = argparse.ArgumentParser()
# Get the port number from the command line
parser.add_argument("--port", type=int, default=8000)
# Get host from the command line
parser.add_argument("--host", type=str, default="localhost")

args = parser.parse_args()


if __name__ == "__main__":
    uvicorn.run("src.api:db", host=args.host, port=args.port)  # Run the server
