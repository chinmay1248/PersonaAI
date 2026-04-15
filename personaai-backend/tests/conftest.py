import os
from collections.abc import Generator

import pytest

os.environ["DATABASE_URL"] = "sqlite:///./.test_personaai.db"
os.environ["OPENAI_API_KEY"] = ""

from app.database import Base, engine  # noqa: E402
import app.models  # noqa: E402,F401


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database() -> Generator[None, None, None]:
    """Create a fresh database for the entire test session."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables() -> Generator[None, None, None]:
    """Roll back any leftover data between individual tests to ensure isolation."""
    yield
    # After each test, clear all tables to prevent leaking state
    from sqlalchemy import text

    with engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
