from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.routers import ai_reply, auth, chat_config, chat_history, feedback, summarizer, tone

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Startup/shutdown events for the application."""
    import app.models  # noqa: F401

    _sync_schema()
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
            print("Demo user created: demo@persona.ai / StrongPass123")
        else:
            print("Demo user already exists")
    except Exception as exc:
        db.rollback()
        print(f"Failed to seed demo user: {exc}")
    finally:
        db.close()


def _sync_schema() -> None:
    """Bring the local database schema up to date before serving requests."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    has_version_table = "alembic_version" in table_names

    if not table_names or table_names == {"alembic_version"}:
        _run_migrations()
        return

    if not has_version_table or not _has_recorded_alembic_revision():
        Base.metadata.create_all(bind=engine)
        _apply_legacy_schema_fixes()
        _stamp_head()
        return

    _run_migrations()


def _run_migrations() -> None:
    """Apply Alembic migrations using the configured database URL."""
    project_root = Path(__file__).resolve().parents[1]
    alembic_config = Config(str(project_root / "alembic.ini"))
    alembic_config.set_main_option("sqlalchemy.url", settings.resolved_database_url)
    command.upgrade(alembic_config, "head")


def _stamp_head() -> None:
    """Mark a legacy schema as being at the latest Alembic revision."""
    project_root = Path(__file__).resolve().parents[1]
    alembic_config = Config(str(project_root / "alembic.ini"))
    alembic_config.set_main_option("sqlalchemy.url", settings.resolved_database_url)
    command.stamp(alembic_config, "head")


def _has_recorded_alembic_revision() -> bool:
    """Return True when alembic_version exists and contains a revision row."""
    with engine.connect() as connection:
        version_count = connection.execute(text("SELECT COUNT(*) FROM alembic_version")).scalar_one()
    return version_count > 0


def _apply_legacy_schema_fixes() -> None:
    """Patch older local databases that predate Alembic-managed changes."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "tone_profiles" not in table_names:
        return

    tone_profile_columns = {column["name"] for column in inspector.get_columns("tone_profiles")}
    if "tone_shifts" in tone_profile_columns:
        return

    with engine.begin() as connection:
        if connection.dialect.name == "sqlite":
            connection.execute(
                text("ALTER TABLE tone_profiles ADD COLUMN tone_shifts JSON NOT NULL DEFAULT '{}'")
            )
        else:
            connection.execute(
                text(
                    "ALTER TABLE tone_profiles "
                    "ADD COLUMN IF NOT EXISTS tone_shifts JSON DEFAULT '{}'::json NOT NULL"
                )
            )


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# CORS: Allow all origins.
# Mobile React Native apps send Origin: null or no origin at all,
# so we must use a wildcard.  The API is protected by JWT tokens.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.resolved_cors_allowed_origins,
    allow_origin_regex=settings.cors_allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.get(f"{settings.api_prefix}/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.get(f"{settings.api_prefix}/meta")
def metadata() -> dict[str, object]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "api_prefix": settings.api_prefix,
        "llm_enabled": settings.llm_enabled,
        "llm_provider": settings.normalized_llm_provider,
        "clients": {
            "browser_extension": {
                "supported_hosts": [
                    "web.whatsapp.com",
                    "web.telegram.org",
                    "k.telegram.org",
                    "a.telegram.org",
                ],
                "features": ["reply_suggestions", "summaries", "tone_training"],
            }
        },
    }


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(chat_config.router, prefix=settings.api_prefix)
app.include_router(ai_reply.router, prefix=settings.api_prefix)
app.include_router(summarizer.router, prefix=settings.api_prefix)
app.include_router(tone.router, prefix=settings.api_prefix)
app.include_router(feedback.router, prefix=settings.api_prefix)
app.include_router(chat_history.router, prefix=settings.api_prefix)
