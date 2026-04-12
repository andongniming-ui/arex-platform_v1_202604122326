import client from './client'
import type { PagedResult } from './types'

export interface Session {
  id: string
  app_id: string
  name?: string
  description?: string
  status: string
  started_at: string
  stopped_at?: string
  record_count: number
  created_by?: string
  error_message?: string
}

export interface Recording {
  id: string
  session_id: string
  app_id: string
  trace_id?: string
  entry_type?: string
  entry_app?: string
  host?: string
  path?: string
  request_body?: string
  response_body?: string
  sub_invocations?: any[]
  duration_ms?: number
  timestamp?: string
  tags?: string[]
  status: string
  created_at: string
}

export const sessionApi = {
  list: (app_id?: string, limit = 20, offset = 0) =>
    client.get<PagedResult<Session>>('/sessions', { params: { app_id, limit, offset } }),
  search: (params?: {
    app_id?: string
    name?: string
    status?: string
    started_after?: string
    started_before?: string
    limit?: number
    offset?: number
    sort_by?: string
    sort_order?: string
  }) => client.get<PagedResult<Session>>('/sessions', { params }),
  get: (id: string) => client.get<Session>(`/sessions/${id}`),
  create: (data: { app_id: string; name?: string; description?: string; created_by?: string }) =>
    client.post<Session>('/sessions', data),
  stop: (id: string) => client.put<{ status: string }>(`/sessions/${id}/stop`),
  delete: (id: string) => client.delete(`/sessions/${id}`),
  batchDelete: (ids: string[]) => client.delete('/sessions/batch', { data: { ids } }),
  directRecord: (id: string, payload: {
    method?: string
    url: string
    headers?: Record<string, string>
    body?: string
    operation?: string
  }) => client.post<{ recording_id: string; status_code: number; duration_ms: number; response: string }>(
    `/sessions/${id}/direct-record`, payload
  ),
}

export const recordingApi = {
  list: (params?: {
    session_id?: string
    app_id?: string
    entry_type?: string
    status?: string
    path_contains?: string
    created_after?: string
    created_before?: string
    limit?: number
    offset?: number
    sort_by?: string
    sort_order?: string
  }) => client.get<PagedResult<Recording>>('/recordings', { params }),
  get: (id: string) => client.get<Recording>(`/recordings/${id}`),
  delete: (id: string) => client.delete(`/recordings/${id}`),
  batchDelete: (ids: string[]) => client.delete('/recordings/batch', { data: { ids } }),
  updateTags: (id: string, tags: string[]) =>
    client.patch<Recording>(`/recordings/${id}/tags`, { tags }),
  recapture: (id: string) => client.post<Recording>(`/recordings/${id}/recapture`),
  importHar: (formData: FormData) =>
    client.post<{ imported: number; session_id: string }>('/recordings/import-har', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  updateRequest: (id: string, requestBody: string) =>
    client.patch<Recording>(`/recordings/${id}/request`, { request_body: requestBody }),
}

export const configApi = {
  get: (app_id: string) => client.get(`/configs/${app_id}`),
  upsert: (app_id: string, data: any) => client.put(`/configs/${app_id}`, data),
  push: (app_id: string) => client.post(`/configs/${app_id}/push`),
  getDefault: (app_id: string) => client.get(`/configs/${app_id}/default`),
}
