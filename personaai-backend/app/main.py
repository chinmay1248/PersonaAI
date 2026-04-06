from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.routers import ai_reply, auth, chat_config, feedback, summarizer, tone

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Startup/shutdown events for the application."""
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Seed demo user so the pre-filled login credentials work out of the box
    _seed_demo_user()

    yield


def _seed_demo_user() -> None:
    """Create the demo@persona.ai user if it doesn't already exist."""
    from passlib.context import CryptContext
    from app.models.user import User

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "demo@persona.ai").one_or_none()
        if not existing:
            user = User(
                email="demo@persona.ai",
                password_hash=pwd_context.hash("StrongPass123"),
                display_name="Demo User",
            )
            db.add(user)
            db.commit()
            print("✅ Demo user created: demo@persona.ai / StrongPass123")
        else:
            print("✅ Demo user already exists")
    except Exception as exc:
        db.rollback()
        print(f"⚠️ Failed to seed demo user: {exc}")
    finally:
        db.close()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# CORS: Allow all origins.
# Mobile React Native apps send Origin: null or no origin at all,
# so we must use a wildcard.  The API is protected by JWT tokens.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{settings.api_prefix}/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(chat_config.router, prefix=settings.api_prefix)
app.include_router(ai_reply.router, prefix=settings.api_prefix)
app.include_router(summarizer.router, prefix=settings.api_prefix)
app.include_router(tone.router, prefix=settings.api_prefix)
app.include_router(feedback.router, prefix=settings.api_prefix)
