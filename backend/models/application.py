import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Application(Base):
    __tablename__ = "application"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # SSH connectivity
    ssh_host: Mapped[str] = mapped_column(String(256), nullable=False)
    ssh_port: Mapped[int] = mapped_column(Integer, default=22)
    ssh_user: Mapped[str] = mapped_column(String(64), nullable=False)
    ssh_auth_type: Mapped[str] = mapped_column(String(16), default="KEY")  # KEY or PASSWORD
    ssh_key_path: Mapped[str | None] = mapped_column(String(512))  # absolute path on platform host
    ssh_password: Mapped[str | None] = mapped_column(String(256))  # stored encrypted

    # JVM-Sandbox Repeater ports
    sandbox_port: Mapped[int] = mapped_column(Integer, default=39393)  # sandbox management port
    repeater_port: Mapped[int] = mapped_column(Integer, default=8080)  # target app HTTP port

    # Application identification on target host
    java_jar_name: Mapped[str | None] = mapped_column(String(256))  # used for PID discovery via jps
    java_pid: Mapped[int | None] = mapped_column(Integer)
    sandbox_home: Mapped[str] = mapped_column(String(512), default="/root/.sandbox")
    repeater_data_dir: Mapped[str] = mapped_column(
        String(512), default="/root/.sandbox-module/repeater-data/record"
    )

    # Recording controls
    sample_rate: Mapped[float] = mapped_column(Float, default=1.0)     # 0.0–1.0, 1.0 = record all
    desensitize_rules: Mapped[list | None] = mapped_column(JSON)        # [{field, action, ...}]
    operation_id_tags: Mapped[list | None] = mapped_column(JSON)

    # XML request template — used as default body when replay lacks request body
    xml_request_template: Mapped[str | None] = mapped_column(Text)

    # Default replay config — auto-loaded when creating a replay job for this app
    default_ignore_fields: Mapped[list | None] = mapped_column(JSON)
    default_diff_rules: Mapped[list | None] = mapped_column(JSON)
    default_assertions: Mapped[list | None] = mapped_column(JSON)
    default_perf_threshold_ms: Mapped[int | None] = mapped_column(Integer)

    # Agent lifecycle state
    agent_status: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    # UNKNOWN / ATTACHED / DETACHED / ERROR
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    sessions: Mapped[list["RecordingSession"]] = relationship(
        "RecordingSession", back_populates="application", cascade="all, delete-orphan"
    )
    repeater_config: Mapped["RepeaterConfig | None"] = relationship(
        "RepeaterConfig", back_populates="application", uselist=False, cascade="all, delete-orphan"
    )
