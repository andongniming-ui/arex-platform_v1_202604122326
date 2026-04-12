import client from './client'
import type { PagedResult } from './types'

export interface DiffRule {
  type: 'ignore' | 'numeric_tolerance' | 'regex_match' | 'type_only'
  path: string
  tolerance?: number   // for numeric_tolerance
  pattern?: string     // for regex_match
}

export interface AssertionRule {
  type: 'status_code_eq' | 'response_not_empty' | 'json_path_eq' | 'json_path_contains' | 'json_path_exists' | 'json_path_regex' | 'diff_score_lte'
  path?: string
  value?: string | number
  pattern?: string
}

export interface ReplayJobCreate {
  case_id: string
  target_app_id: string
  environment?: string
  concurrency?: number
  delay_ms?: number
  override_host?: string
  ignore_fields?: string[]
  diff_rules?: DiffRule[]
  assertions?: AssertionRule[]
  perf_threshold_ms?: number
  use_sub_invocation_mocks?: boolean
  webhook_url?: string
  notify_type?: string
  // P0: 智能降噪
  smart_noise_reduction?: boolean
  // P0: 流量放大
  repeat_count?: number
  // P1: 请求头转换
  header_transforms?: HeaderTransform[]
  // P1: 失败重试
  retry_count?: number
}

export interface HeaderTransform {
  type: 'replace' | 'remove' | 'add'
  key: string
  value?: string
}

export interface ReplayJob {
  id: string
  case_id: string
  target_app_id: string
  environment?: string
  status: string
  total_count: number
  sent_count: number
  success_count: number
  fail_count: number
  concurrency: number
  delay_ms: number
  override_host?: string
  ignore_fields?: string[]
  diff_rules?: DiffRule[]
  assertions?: AssertionRule[]
  perf_threshold_ms?: number
  use_sub_invocation_mocks: boolean
  webhook_url?: string
  notify_type?: string
  // P0: 智能降噪
  smart_noise_reduction?: boolean
  // P0: 流量放大
  repeat_count?: number
  // P1: 请求头转换
  header_transforms?: HeaderTransform[]
  // P1: 失败重试
  retry_count?: number
  started_at?: string
  finished_at?: string
  created_at: string
}

export interface AssertionResult {
  type: string
  passed: boolean
  message: string
}

export interface ReplayResult {
  id: string
  job_id: string
  recording_id: string
  status?: string
  original_response?: string
  replayed_response?: string
  diff_json?: string
  diff_score?: number
  error_message?: string
  duration_ms?: number
  replayed_status_code?: number
  assertion_results?: AssertionResult[]
  replayed_at: string
  // Failure analysis
  failure_category?: string
  failure_reason?: string
  // Denormalized from Recording
  recording_path?: string
  recording_entry_type?: string
  recording_service_id?: string
  recording_request_body?: string
}

export type FailureCategory = 'ENVIRONMENT' | 'DATA_ISSUE' | 'BUG' | 'PERFORMANCE' | 'UNKNOWN'

export interface FailureAnalysisResult {
  id: string
  recording_id: string
  recording_path?: string
  recording_entry_type?: string
  status: string
  failure_reason?: string
  replayed_status_code?: number
  diff_score?: number
  error_message?: string
  duration_ms?: number
  replayed_at?: string
}

export interface FailureCategoryStats {
  count: number
  percentage: number
  results: FailureAnalysisResult[]
}

export interface FailureAnalysis {
  job_id: string
  total_failures: number
  categories: {
    ENVIRONMENT: FailureCategoryStats
    DATA_ISSUE: FailureCategoryStats
    BUG: FailureCategoryStats
    PERFORMANCE: FailureCategoryStats
    UNKNOWN: FailureCategoryStats
  }
}

export interface ResultSummary {
  job_id: string
  status: string
  total_count: number
  success_count: number
  fail_count: number
  error_count: number
  pass_rate: number
}

export const replayApi = {
  create: (data: ReplayJobCreate) => client.post<ReplayJob>('/replays', data),
  list: (params?: {
    keyword?: string
    case_id?: string
    app_id?: string
    status?: string
    created_after?: string
    created_before?: string
    limit?: number
    offset?: number
  }) =>
    client.get<PagedResult<ReplayJob>>('/replays', { params }),
  get: (id: string) => client.get<ReplayJob>(`/replays/${id}`),
  cancel: (id: string) => client.put(`/replays/${id}/cancel`),
  delete: (id: string) => client.delete(`/replays/${id}`),
  batchDelete: (ids: string[]) => client.delete('/replays/batch', { data: { ids } }),
  summary: (id: string) => client.get<ResultSummary>(`/replays/${id}/summary`),
  results: (id: string, params?: {
    status?: string
    replayed_after?: string
    replayed_before?: string
    sort_by?: string
    sort_order?: string
    limit?: number
    offset?: number
  }) =>
    client.get<PagedResult<ReplayResult>>(`/replays/${id}/results`, { params }),
  getResult: (jobId: string, resultId: string) =>
    client.get<ReplayResult>(`/replays/${jobId}/results/${resultId}`),
  analysis: (id: string) => client.get<FailureAnalysis>(`/replays/${id}/analysis`),
  reportUrl: (id: string) => `/api/v1/replays/${id}/report`,
  // P2-2: 保存回放结果为测试用例
  saveToTestCase: (jobId: string, data: { case_name: string; case_description?: string; recording_ids: string[] }) =>
    client.post<{ test_case_id: string; test_case_name: string; added_count: number }>(
      `/replays/${jobId}/save-to-testcase`,
      data
    ),
}
