import logging
import os
import sys

def setup_logging():
    """Central logging config, controlled by LOG_LEVEL env var."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("uvicorn").setLevel(log_level)       # align uvicorn
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)
