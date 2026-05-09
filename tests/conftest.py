import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db, Base
from src.auth.manager import current_user, current_optional_user
from src.auth.models import User
from unittest.mock import MagicMock

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_client(db_session):
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    async def override_get_db():
        yield db_session

    async def override_current_user():
        return mock_user

    async def override_current_optional_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[current_user] = override_current_user
    app.dependency_overrides[current_optional_user] = override_current_optional_user

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()