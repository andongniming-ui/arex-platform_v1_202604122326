from pydantic import BaseModel, Field
from datetime import datetime


class ReplayJobCreate(BaseModel):
    case_id: str
    target_app_id: str
    environment: str | None = None
    concurrency: int = Field(default=1, ge=1, le=20)
    delay_ms: int = Field(default=0, ge=0)
    override_host: str | None = None
    ignore_fields: list[str] | None = None   # field names to ignore in diff
    diff_rules: list[dict] | None = None       # Smart Diff Rules
    assertions: list[dict] | None = None       # Assertion Rules
    perf_threshold_ms: int | None = Field(default=None, ge=1)       # Flag results exceeding this latency (ms)
    use_sub_invocation_mocks: bool = False     # Mock downstream DB/RPC calls via Repeater agent
    webhook_url: str | None = None             # POST here when job finishes
    notify_type: str | None = None           # generic / dingtalk / wecom
    created_by: str | None = None
    # P0: 智能降噪
    smart_noise_reduction: bool = False       # 启用内置智能降噪规则
    # P0: 流量放大
    repeat_count: int = Field(default=1, ge=1, le=100)                     # 每条录制回放次数
    # P1: 请求头转换
    header_transforms: list[dict] | None = None  # 请求头转换规则
    # P1: 失败重试
    retry_count: int = Field(default=0, ge=0, le=5)                      # 失败重试次数


class ReplayJobOut(BaseModel):
    id: str
    case_id: str
    target_app_id: str
    environment: str | None
    status: str
    total_count: int
    sent_count: int
    success_count: int
    fail_count: int
    concurrency: int
    delay_ms: int
    override_host: str | None
    ignore_fields: list[str] | None
    diff_rules: list[dict] | None
    assertions: list[dict] | None
    perf_threshold_ms: int | None
    use_sub_invocation_mocks: bool
    webhook_url: str | None
    notify_type: str | None
    # P0: 智能降噪
    smart_noise_reduction: bool = False
    # P0: 流量放大
    repeat_count: int = 1
    # P1: 请求头转换
    header_transforms: list[dict] | None = None
    # P1: 失败重试
    retry_count: int = 0
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReplayResultOut(BaseModel):
    id: str
    job_id: str
    recording_id: str
    status: str | None
    original_response: str | None
    replayed_response: str | None
    diff_json: str | None
    diff_score: float | None
    error_message: str | None
    duration_ms: int | None
    replayed_status_code: int | None = None
    assertion_results: list[dict] | None = None
    replayed_at: datetime
    # Failure analysis
    failure_category: str | None = None
    failure_reason: str | None = None
    # Denormalized from Recording for display
    recording_path: str | None = None
    recording_entry_type: str | None = None
    recording_service_id: str | None = None
    recording_request_body: str | None = None

    model_config = {"from_attributes": True}


class ResultSummary(BaseModel):
    job_id: str
    status: str
    total_count: int
    success_count: int
    fail_count: int
    error_count: int
    pass_rate: float
