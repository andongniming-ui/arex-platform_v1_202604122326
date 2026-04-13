import client from './client'

export type ApplicationAuthType = 'KEY' | 'PASSWORD'

export interface DesensitizeRule {
  field: string
  action: 'remove' | 'mask' | 'partial' | 'hash'
  keep_start?: number
  keep_end?: number
}

export interface ApplicationCreate {
  name: string
  description?: string
  ssh_host: string
  ssh_port?: number
  ssh_user: string
  ssh_auth_type?: ApplicationAuthType
  ssh_key_path?: string
  ssh_password?: string
  sandbox_port?: number
  repeater_port?: number
  java_jar_name?: string
  sandbox_home?: string
  repeater_data_dir?: string
  sample_rate?: number
  desensitize_rules?: DesensitizeRule[] | null
  operation_id_tags?: string[] | null
  xml_request_template?: string | null
  default_ignore_fields?: string[] | null
  default_diff_rules?: object[] | null
  default_assertions?: object[] | null
  default_perf_threshold_ms?: number | null
}

export interface Application {
  id: string
  name: string
  description?: string
  ssh_host: string
  ssh_port?: number
  ssh_user: string
  ssh_auth_type: ApplicationAuthType
  sandbox_port?: number
  repeater_port?: number
  java_jar_name?: string
  sandbox_home?: string
  repeater_data_dir?: string
  agent_status: string
  java_pid: number | null
  last_heartbeat: string | null
  sample_rate: number
  desensitize_rules: DesensitizeRule[] | null
  operation_id_tags: string[] | null
  xml_request_template?: string | null
  default_ignore_fields: string[] | null
  default_diff_rules: object[] | null
  default_assertions: object[] | null
  default_perf_threshold_ms: number | null
  created_at: string
  updated_at: string
}

export type ApplicationUpdate = Partial<ApplicationCreate>

export const applicationApi = {
  list: () => client.get<Application[]>('/applications'),
  get: (id: string) => client.get<Application>(`/applications/${id}`),
  create: (data: ApplicationCreate) => client.post<Application>('/applications', data),
  update: (id: string, data: ApplicationUpdate) =>
    client.put<Application>(`/applications/${id}`, data),
  delete: (id: string) => client.delete(`/applications/${id}`),

  // Agent operations
  sshTest: (id: string) => client.post<{ success: boolean; message: string }>(`/applications/${id}/agent/ssh-test`),
  discoverPid: (id: string) => client.post<{ pid: number | null }>(`/applications/${id}/agent/discover-pid`),
  attachAgent: (id: string) => client.post<{ agent_status: string; pid: number }>(`/applications/${id}/agent/attach`),
  detachAgent: (id: string) => client.post<{ agent_status: string }>(`/applications/${id}/agent/detach`),
  agentStatus: (id: string) => client.get<{ alive: boolean; agent_status: string }>(`/applications/${id}/agent/status`),
}
