import os

INFERENCE_ENDPOINT = os.environ.get("INFERENCE_ENDPOINT")
INFERENCE_HEALTH_ENDPOINT = os.environ.get("INFERENCE_HEALTH_ENDPOINT")
RETRIEVAL_ENDPOINT = os.environ.get("RETRIEVAL_ENDPOINT")
ALIGNSCORE_ENDPOINT = os.environ.get("ALIGNSCORE_ENDPOINT")
FACTCHECKING = False

HOST = os.environ.get("HOST", "localhost")
PORT = os.environ.get("PORT", 8000)
ENDPOINTS = {
    "moderated": f"http://{HOST}:{PORT}/api/generate_moderated",
    "unmoderated": f"http://{HOST}:{PORT}/api/generate_unmoderated",
    "clear": f"http://{HOST}:{PORT}/api/clear",
}
