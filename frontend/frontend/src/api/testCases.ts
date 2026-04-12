import client from './client'
import type { Recording } from './recordings'
import type { PagedResult } from './types'
export type { Recording }

export interface TestCase {
  id: string
  name: string
  description?: string
  app_id?: string
  tags?: string[]
  status: string
  recording_count: number
  created_by?: string
  created_at: string
  updated_at: string
}

export const testCaseApi = {
  list: (params?: {
    app_id?: string
    tag?: string
    created_after?: string
    created_before?: string
    limit?: number
    offset?: number
  }) =>
    client.get<PagedResult<TestCase>>('/test-cases', { params }),
  get: (id: string) => client.get<TestCase>(`/test-cases/${id}`),
  create: (data: { name: string; description?: string; app_id?: string; tags?: string[]; created_by?: string }) =>
    client.post<TestCase>('/test-cases', data),
  update: (id: string, data: Partial<{ name: string; description: string; app_id: string; tags: string[]; status: string }>) =>
    client.put<TestCase>(`/test-cases/${id}`, data),
  delete: (id: string) => client.delete(`/test-cases/${id}`),
  batchDelete: (ids: string[]) => client.delete('/test-cases/batch', { data: { ids } }),
  getRecordings: (id: string) =>
    client.get<Recording[]>(`/test-cases/${id}/recordings`),
  addRecordings: (id: string, recording_ids: string[]) =>
    client.post<{ added: number }>(`/test-cases/${id}/recordings`, { recording_ids }),
  removeRecording: (caseId: string, recordingId: string) =>
    client.delete(`/test-cases/${caseId}/recordings/${recordingId}`),
  clone: (id: string) => client.post<TestCase>(`/test-cases/${id}/clone`),
  suggestIgnore: (id: string) =>
    client.get<{
      suggested_fields: string[]
      details: { field: string; paths_affected: number }[]
      analyzed_paths: number
      total_paths: number
    }>(`/test-cases/${id}/suggest-ignore`),
  listAll: async (params?: {
    app_id?: string
    tag?: string
    created_after?: string
    created_before?: string
  }) => {
    const pageSize = 200
    let offset = 0
    let total = Infinity
    const items: TestCase[] = []
    while (offset < total) {
      const res = await client.get<PagedResult<TestCase>>('/test-cases', {
        params: {
          ...params,
          limit: pageSize,
          offset,
        },
      })
      items.push(...res.data.items)
      total = res.data.total
      offset += pageSize
      if (res.data.items.length === 0) break
    }
    return items
  },
}
