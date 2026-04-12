from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class ApplicationCreate(BaseModel):
    name: str = Field(..., max_length=128)
    description: str | None = None
    ssh_host: str
    ssh_port: int = 22
    ssh_user: str
    ssh_auth_type: Literal["KEY", "PASSWORD"] = "KEY"
    ssh_key_path: str | None = None
    ssh_password: str | None = None
    sandbox_port: int = 39393
    repeater_port: int = 8080
    java_jar_name: str | None = None
    sandbox_home: str = "/root/.sandbox"
    repeater_data_dir: str = "/root/.sandbox-module/repeater-data/record"
    sample_rate: float = 1.0
    desensitize_rules: list[dict] | None = None
    operation_id_tags: list[str] | None = None
    xml_request_template: str | None = None
    default_ignore_fields: list[str] | None = None
    default_diff_rules: list[dict] | None = None
    default_assertions: list[dict] | None = None
    default_perf_threshold_ms: int | None = None


class ApplicationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    ssh_host: str | None = None
    ssh_port: int | None = None
    ssh_user: str | None = None
    ssh_auth_type: Literal["KEY", "PASSWORD"] | None = None
    ssh_key_path: str | None = None
    ssh_password: str | None = None
    sandbox_port: int | None = None
    repeater_port: int | None = None
    java_jar_name: str | None = None
    sandbox_home: str | None = None
    repeater_data_dir: str | None = None
    sample_rate: float | None = None
    desensitize_rules: list[dict] | None = None
    operation_id_tags: list[str] | None = None
    xml_request_template: str | None = None
    default_ignore_fields: list[str] | None = None
    default_diff_rules: list[dict] | None = None
    default_assertions: list[dict] | None = None
    default_perf_threshold_ms: int | None = None


class ApplicationOut(BaseModel):
    id: str
    name: str
    description: str | None
    ssh_host: str
    ssh_port: int
    ssh_user: str
    ssh_auth_type: str
    sandbox_port: int
    repeater_port: int
    java_jar_name: str | None
    java_pid: int | None
    sandbox_home: str
    repeater_data_dir: str
    sample_rate: float
    desensitize_rules: list[dict] | None
    operation_id_tags: list[str] | None
    xml_request_template: str | None
    default_ignore_fields: list[str] | None
    default_diff_rules: list[dict] | None
    default_assertions: list[dict] | None
    default_perf_threshold_ms: int | None
    agent_status: str
    last_heartbeat: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SSHTestResult(BaseModel):
    success: bool
    message: str
    pid: int | None = None
