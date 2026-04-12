import client from './client'
import type { DiffRule } from './replays'
import type { PagedResult } from './types'

export interface CompareRequest {
  name?: string
  case_id: string
  app_a_id: string
  app_b_id: string
  ignore_fields?: string[]
  diff_rules?: DiffRule[]
  concurrency?: number
  delay_ms?: number
}

export interface CompareRun {
  id: string
  name?: string
  case_id: string
  app_a_id: string
  app_b_id: string
  status: string
  ignore_fields?: string[]
  diff_rules?: DiffRule[]
  total_count: number
  agreed_count: number
  diverged_count: number
  created_at: string
  finished_at?: string
}

export interface CompareResult {
  id: string
  run_id: string
  recording_id: string
  path?: string
  entry_type?: string
  status_a?: string
  resp_a?: string
  diff_score_a?: number
  duration_a_ms?: number
  status_b?: string
  resp_b?: string
  diff_score_b?: number
  duration_b_ms?: number
  diff_a_vs_b?: string
  diff_score_a_vs_b?: number
  created_at: string
  service_id?: string
}

export const compareApi = {
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
    client.get<PagedResult<CompareRun>>('/compare', { params }),
  get: (id: string) => client.get<CompareRun>(`/compare/${id}`),
  create: (data: CompareRequest) => client.post<CompareRun>('/compare', data),
  delete: (id: string) => client.delete(`/compare/${id}`),
  batchDelete: (ids: string[]) => client.delete('/compare/batch', { data: { ids } }),
  results: (id: string, params?: { path_contains?: string; agreement?: string; limit?: number; offset?: number }) =>
    client.get<PagedResult<CompareResult>>(`/compare/${id}/results`, { params }),
  reportUrl: (id: string) => `${client.defaults.baseURL}/compare/${id}/report`,
}
