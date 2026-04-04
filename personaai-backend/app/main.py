from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import ai_reply, auth, chat_config, feedback, summarizer, tone

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
