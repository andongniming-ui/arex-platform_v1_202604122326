"""
Shared pytest fixtures for API integration tests.
Each test function gets an isolated SQLite database file.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool


@pytest.fixture
def client(tmp_path):
    """
    Returns a TestClient wired to a fresh per-test SQLite database.

    Isolation strategy:
    1. Patch `database.engine` / `database.async_session_factory` to a temp SQLite file.
    2. Override the `get_db` FastAPI dependency.
    3. Patch `scheduler.start` / `scheduler.shutdown` to be no-ops so the singleton
       APScheduler does not raise SchedulerAlreadyRunningError across tests.
    4. TestClient's lifespan calls `init_db()` using the patched engine → tables created
       inside the TestClient's event loop (no cross-loop contamination).
    5. NullPool prevents connection-pool cleanup errors when the event loop tears down.
    """
    import database
    from database import get_db
    from main import app
    from fastapi.testclient import TestClient

    db_file = str(tmp_path / "test.db")
    db_url = f"sqlite+aiosqlite:///{db_file}"

    test_engine = create_async_engine(db_url, echo=False, poolclass=NullPool)
    test_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    # Patch module-level singletons (also used by background workers)
    old_engine = database.engine
    old_factory = database.async_session_factory
    database.engine = test_engine
    database.async_session_factory = test_factory

    async def _override_get_db():
        async with test_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db

    # Patch APScheduler so the singleton doesn't raise across tests.
    # schedule-specific tests that need real APScheduler behaviour should
    # use their own fixture setup.
    # Also patch SSH executor and arex_client so tests don't block on real connections.
    with patch("main.scheduler") as mock_sched, \
         patch("api.v1.schedule.scheduler") as mock_sched2, \
         patch("api.v1.sessions.ArexClient") as mock_arex_client, \
         patch("services.session_service.ArexClient") as mock_service_arex_client:
        mock_sched.running = False
        mock_sched.add_job = MagicMock()
        mock_sched.remove_job = MagicMock()
        mock_sched.get_job = MagicMock(return_value=None)
        mock_sched2.running = False
        mock_sched2.add_job = MagicMock()
        mock_sched2.remove_job = MagicMock()
        mock_sched2.get_job = MagicMock(return_value=None)
        # ArexClient mock: return empty recordings by default
        mock_arex_instance = AsyncMock()
        mock_arex_instance.query_recordings.return_value = {"body": {"sources": []}}
        mock_arex_instance.health_check.return_value = True
        mock_arex_client.return_value = mock_arex_instance
        mock_service_arex_client.return_value = mock_arex_instance

        with TestClient(app, raise_server_exceptions=False) as c:
            yield c

    # Always restore module state
    app.dependency_overrides.clear()
    database.engine = old_engine
    database.async_session_factory = old_factory
