from pydantic import BaseModel, Field
from datetime import datetime


class SuiteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    description: str | None = None
    case_ids: list[str] = Field(default_factory=list)
    case_app_map: dict[str, str] | None = None
    default_target_app_id: str | None = None
    default_environment: str | None = None
    default_override_host: str | None = None
    default_concurrency: int = Field(default=1, ge=1, le=20)
    default_delay_ms: int = Field(default=0, ge=0)
    default_ignore_fields: list[str] | None = None
    default_diff_rules: list[dict] | None = None
    default_assertions: list[dict] | None = None
    default_perf_threshold_ms: int | None = Field(default=None, ge=1)


class SuiteUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    case_ids: list[str] | None = None
    case_app_map: dict[str, str] | None = None
    default_target_app_id: str | None = None
    default_environment: str | None = None
    default_override_host: str | None = None
    default_concurrency: int | None = Field(default=None, ge=1, le=20)
    default_delay_ms: int | None = Field(default=None, ge=0)
    default_ignore_fields: list[str] | None = None
    default_diff_rules: list[dict] | None = None
    default_assertions: list[dict] | None = None
    default_perf_threshold_ms: int | None = Field(default=None, ge=1)


class SuiteOut(BaseModel):
    id: str
    name: str
    description: str | None
    case_ids: list[str]
    case_app_map: dict[str, str] | None
    default_target_app_id: str | None
    default_environment: str | None
    default_override_host: str | None
    default_concurrency: int
    default_delay_ms: int
    default_ignore_fields: list[str] | None
    default_diff_rules: list[dict] | None
    default_assertions: list[dict] | None
    default_perf_threshold_ms: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SuiteRunRequest(BaseModel):
    target_app_id: str | None = None  # global default; required if case_app_map doesn't cover all cases
    case_app_map: dict[str, str] | None = None  # per-case override: {case_id: app_id}
    # Optional overrides for this specific run
    environment: str | None = None
    override_host: str | None = None
    concurrency: int | None = Field(default=None, ge=1, le=20)
    ignore_fields: list[str] | None = None
    diff_rules: list[dict] | None = None
    assertions: list[dict] | None = None
    perf_threshold_ms: int | None = Field(default=None, ge=1)


class SuiteRunOut(BaseModel):
    id: str
    suite_id: str
    target_app_id: str | None
    status: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    total_requests: int
    passed_requests: int
    overall_pass_rate: float
    job_ids: list[str]
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
