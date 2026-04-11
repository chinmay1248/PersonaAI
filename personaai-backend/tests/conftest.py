import os
from collections.abc import Generator

import pytest

os.environ["DATABASE_URL"] = "sqlite:///./.test_personaai.db"
os.environ["OPENAI_API_KEY"] = ""

from app.database import Base, engine  # noqa: E402
import app.models  # noqa: E402,F401


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
