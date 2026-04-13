import type { Application, ApplicationCreate } from '@/api/applications'

export type ApplicationAuthType = 'KEY' | 'PASSWORD'

export interface ApplicationEditorModel {
  name: string
  description: string
  ssh_host: string
  ssh_port: number
  ssh_user: string
  ssh_auth_type: ApplicationAuthType
  ssh_key_path: string
  ssh_password: string
  java_jar_name: string
  sandbox_port: number
  repeater_port: number
  sandbox_home: string
  repeater_data_dir: string
  sample_rate_percent: number
  operation_id_tags: string[]
  default_ignore_fields: string[]
}

export function createEmptyApplicationEditorModel(): ApplicationEditorModel {
  return {
    name: '',
    description: '',
    ssh_host: '',
    ssh_port: 22,
    ssh_user: 'root',
    ssh_auth_type: 'KEY',
    ssh_key_path: '',
    ssh_password: '',
    java_jar_name: '',
    sandbox_port: 39393,
    repeater_port: 8080,
    sandbox_home: '/root/.sandbox',
    repeater_data_dir: '/root/.sandbox-module/repeater-data/record',
    sample_rate_percent: 100,
    operation_id_tags: [],
    default_ignore_fields: [],
  }
}

export function createApplicationEditorModel(app: Application): ApplicationEditorModel {
  return {
    name: app.name,
    description: app.description || '',
    ssh_host: app.ssh_host,
    ssh_port: app.ssh_port ?? 22,
    ssh_user: app.ssh_user,
    ssh_auth_type: app.ssh_auth_type || 'KEY',
    ssh_key_path: '',
    ssh_password: '',
    java_jar_name: app.java_jar_name || '',
    sandbox_port: app.sandbox_port ?? 39393,
    repeater_port: app.repeater_port ?? 8080,
    sandbox_home: app.sandbox_home || '/root/.sandbox',
    repeater_data_dir: app.repeater_data_dir || '/root/.sandbox-module/repeater-data/record',
    sample_rate_percent: Math.round((app.sample_rate ?? 1) * 100),
    operation_id_tags: [...(app.operation_id_tags ?? [])],
    default_ignore_fields: [...(app.default_ignore_fields ?? [])],
  }
}

export function buildApplicationPayload(model: ApplicationEditorModel): ApplicationCreate {
  return {
    name: model.name.trim(),
    description: model.description.trim() || undefined,
    ssh_host: model.ssh_host.trim(),
    ssh_port: model.ssh_port,
    ssh_user: model.ssh_user.trim(),
    ssh_auth_type: model.ssh_auth_type,
    ssh_key_path:
      model.ssh_auth_type === 'KEY' && model.ssh_key_path.trim()
        ? model.ssh_key_path.trim()
        : undefined,
    ssh_password:
      model.ssh_auth_type === 'PASSWORD' && model.ssh_password
        ? model.ssh_password
        : undefined,
    java_jar_name: model.java_jar_name.trim() || undefined,
    sandbox_port: model.sandbox_port,
    repeater_port: model.repeater_port,
    sandbox_home: model.sandbox_home.trim(),
    repeater_data_dir: model.repeater_data_dir.trim(),
    sample_rate: (model.sample_rate_percent || 100) / 100,
    operation_id_tags: model.operation_id_tags.length ? [...model.operation_id_tags] : undefined,
    default_ignore_fields: model.default_ignore_fields.length
      ? [...model.default_ignore_fields]
      : undefined,
  }
}
