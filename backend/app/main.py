from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import search, agentic_search

app = FastAPI(title="Agentic AI Search API", version="0.1.0")

# CORS for local dev / RN emulators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(agentic_search.router)


@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
