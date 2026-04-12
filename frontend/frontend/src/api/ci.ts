import client from './client'

export interface CIReplayRequest {
  case_id: string
  target_app_id: string
  ignore_fields?: string[]
  diff_rules?: object[]
  assertions?: object[]
  pass_threshold?: number
  timeout_seconds?: number
  concurrency?: number
  delay_ms?: number
  override_host?: string | null
  environment?: string | null
}

export interface CIReplayResponse {
  passed: boolean
  timed_out: boolean
  job_id: string
  status: string
  total_count: number
  success_count: number
  fail_count: number
  error_count: number
  pass_rate: number
  pass_threshold: number
  duration_seconds: number
  report_url?: string | null
}

export const ciApi = {
  replay: (data: CIReplayRequest) =>
    client.post<CIReplayResponse>('/ci/replay', data),
}
