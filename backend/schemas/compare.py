from pydantic import BaseModel, Field
from datetime import datetime


class CompareRequest(BaseModel):
    name: str | None = None
    case_id: str
    app_a_id: str
    app_b_id: str
    ignore_fields: list[str] | None = None
    diff_rules: list[dict] | None = None
    concurrency: int = Field(default=1, ge=1, le=20)
    delay_ms: int = Field(default=0, ge=0)


class CompareRunOut(BaseModel):
    id: str
    name: str | None
    case_id: str
    app_a_id: str
    app_b_id: str
    status: str
    ignore_fields: list[str] | None
    diff_rules: list[dict] | None
    total_count: int
    agreed_count: int
    diverged_count: int
    created_at: datetime
    finished_at: datetime | None

    model_config = {"from_attributes": True}


class CompareResultOut(BaseModel):
    id: str
    run_id: str
    recording_id: str
    path: str | None
    entry_type: str | None
    status_a: str | None
    resp_a: str | None
    diff_score_a: float | None
    duration_a_ms: int | None
    status_b: str | None
    resp_b: str | None
    diff_score_b: float | None
    duration_b_ms: int | None
    diff_a_vs_b: str | None
    diff_score_a_vs_b: float | None
    created_at: datetime
    service_id: str | None = None

    model_config = {"from_attributes": True}
