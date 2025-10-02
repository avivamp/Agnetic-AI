from fastapi import FastAPI
from app.logging_config import setup_logging

# Setup logging before anything else
setup_logging()

from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logging import LoggingMiddleware
from .routers import search, agentic_search  # import after logging is set

app = FastAPI(title="Agentic AI Search API", version="0.1.0")
app.add_middleware(LoggingMiddleware)

# CORS for local dev / RN emulators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(search.router)
app.include_router(agentic_search.router)
app.include_router(metrics.router)


@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
