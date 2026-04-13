from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import settings
import logging

logger = logging.getLogger(__name__)


engine = create_async_engine(
    settings.db_url,
    echo=settings.debug,
    future=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def init_db():
    # Ensure all models are imported so Base.metadata knows about every table
    import models.application  # noqa: F401
    import models.recording    # noqa: F401
    import models.replay       # noqa: F401
    import models.schedule     # noqa: F401
    import models.suite        # noqa: F401
    import models.compare      # noqa: F401
    import models.test_case    # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Add new columns to existing tables without a full migration framework.
        # ALTER TABLE ADD COLUMN is idempotent on Postgres but raises on SQLite if column exists,
        # so we swallow OperationalError / ProgrammingError safely.
        new_columns = [
            ("recording", "tags", "TEXT"),
            ("replay_job", "webhook_url", "VARCHAR(512)"),
            ("replay_job", "notify_type", "VARCHAR(32)"),
            # Phase 1 & 2 new columns
            ("replay_job", "diff_rules", "TEXT"),
            ("replay_job", "assertions", "TEXT"),
            ("replay_job", "perf_threshold_ms", "INTEGER"),
            ("replay_result", "replayed_status_code", "INTEGER"),
            ("replay_result", "assertion_results", "TEXT"),
            ("application", "sample_rate", "REAL DEFAULT 1.0"),
            ("application", "desensitize_rules", "TEXT"),
            ("application", "operation_id_tags", "TEXT"),
            # Phase 3: application defaults
            ("application", "default_ignore_fields", "TEXT"),
            ("application", "default_diff_rules", "TEXT"),
            ("application", "default_assertions", "TEXT"),
            ("application", "default_perf_threshold_ms", "INTEGER"),
            # Mock sub-invocations
            ("replay_job", "use_sub_invocation_mocks", "BOOLEAN DEFAULT 0"),
            # Phase 3: schedule enhancements
            ("scheduled_replay", "diff_rules", "TEXT"),
            ("scheduled_replay", "assertions", "TEXT"),
            ("scheduled_replay", "perf_threshold_ms", "INTEGER"),
            ("scheduled_replay", "override_host", "VARCHAR(256)"),
            ("scheduled_replay", "environment", "VARCHAR(64)"),
            # Suite per-case target app map
            ("replay_suite", "case_app_map", "TEXT"),
            # Failure analysis
            ("replay_result", "failure_category", "VARCHAR(32)"),
            ("replay_result", "failure_reason", "TEXT"),
            # Session error details
            ("recording_session", "error_message", "TEXT"),
            # XML request template for auto-fill on replay
            ("application", "xml_request_template", "TEXT"),
        ]
        import sqlalchemy as _sa
        is_pg = "postgresql" in str(settings.db_url)
        for table, col, col_type in new_columns:
            try:
                if is_pg:
                    sql = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type}"
                else:
                    sql = f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"
                await conn.execute(_sa.text(sql))
            except Exception as e:
                logger.debug(f"Column {table}.{col} may already exist: {e}")
