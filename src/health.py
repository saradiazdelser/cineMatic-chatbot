import logging
import traceback

import requests

from src.settings import (
    ALIGNSCORE_ENDPOINT,
    FACTCHECKING,
    INFERENCE_HEALTH_ENDPOINT,
    RETRIEVAL_ENDPOINT,
)

logger = logging.getLogger(__name__)


def health_check():
    # Custom health check to verify connectivity to the rag api
    try:
        rag_response = requests.post(
            url=RETRIEVAL_ENDPOINT,
            headers={"Content-Type": "application/json", "accept": "application/json"},
            json={
                "text": "King Kong",
                "limit": 1,
                "threshold": 0.85,
                "indexes": ["imbd_movies"],
            },
            timeout=1,
        )
        rag_status = (
            "ok"
            if (rag_response.status_code == 200 and rag_response.json())
            else "error"
        )
    except Exception:
        logger.error(traceback.format_exc())
        rag_status = "error"

    # Custom health check to verify connectivity to the llm
    try:
        llm_response = requests.get(
            url=INFERENCE_HEALTH_ENDPOINT,
            timeout=1,
        )
        llm_status = "ok" if (llm_response.status_code == 200) else "error"
    except Exception:
        logger.error(traceback.format_exc())
        llm_status = "error"

    # Custom health check to verify connectivity to the align score server
    try:
        if FACTCHECKING:
            alignscore_response = requests.get(url=ALIGNSCORE_ENDPOINT, timeout=1)
            alignscore_status = (
                "ok" if alignscore_response.status_code == 200 else "error"
            )
        else:
            alignscore_status = "disabled"
    except Exception:
        logger.error(traceback.format_exc())
        alignscore_status = "error"

    # Constructing the health status response
    health_status = {
        "status": (
            "ok"
            if rag_status == "ok"
            and llm_status == "ok"
            and alignscore_status in ["ok", "disabled"]
            else "error"
        ),
        "details": {
            "rag": rag_status,
            "llm": llm_status,
            "alignscore": alignscore_status,
        },
    }

    logger.info(f"Health Status: {health_status}")
    return health_status
