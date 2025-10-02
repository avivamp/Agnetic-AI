import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("agentic-ai")
logging.basicConfig(level=logging.INFO)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round(time.time() - start, 3)

        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} duration={duration}s"
        )

        return response
