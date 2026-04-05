from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import get_settings
from app.database import Base, engine
from app.routers import ai_reply, auth, chat_config, feedback, summarizer, tone

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)

# Configure CORS based on environment
if settings.app_env == "production":
    # In production, restrict to specific frontend URLs
    allowed_origins = [
        os.getenv("FRONTEND_URL", "https://personaai.app"),
        "https://personaai.app",
    ]
else:
    # In development, allow more origins
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8081",
        "*",  # Allow all in development for testing
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


@app.get(f"{settings.api_prefix}/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(chat_config.router, prefix=settings.api_prefix)
app.include_router(ai_reply.router, prefix=settings.api_prefix)
app.include_router(summarizer.router, prefix=settings.api_prefix)
app.include_router(tone.router, prefix=settings.api_prefix)
app.include_router(feedback.router, prefix=settings.api_prefix)
