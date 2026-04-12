<template>
  <n-card title="应用管理">
    <template #header-extra>
      <n-space wrap>
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索应用名称 / Host"
          clearable
          style="width: 200px"
        />
        <n-select
          v-model:value="searchAgentStatus"
          :options="agentStatusOptions"
          placeholder="Agent 状态"
          clearable
          style="width: 130px"
        />
        <n-date-picker
          v-model:value="searchCreatedRange"
          type="datetimerange"
          clearable
          :shortcuts="dateShortcuts"
          style="width: 320px"
          start-placeholder="注册开始时间"
          end-placeholder="注册结束时间"
        />
        <n-button @click="clearFilters">清空筛选</n-button>
        <n-button type="primary" @click="openCreate">+ 注册应用</n-button>
      </n-space>
    </template>

    <span style="color:#999;font-size:13px;margin-bottom:10px;display:block">共 {{ filteredApps.length }} 条</span>
    <n-data-table
      :columns="columns"
      :data="filteredApps"
      :loading="loading"
      :row-key="(row: any) => row.id"
      :pagination="{ pageSize: 10, showSizePicker: true, pageSizes: [10, 20, 50] }"
      @update:sorter="onSorterChange"
    />
  </n-card>

  <!-- Create / Edit dialog -->
  <n-modal v-model:show="showForm" preset="dialog" :title="editingId ? '编辑应用' : '注册新应用'" style="width: 760px">
    <n-form :model="form" label-placement="left" label-width="120px">
      <n-form-item label="应用名称" required>
        <n-input v-model:value="form.name" placeholder="my-service" :disabled="!!editingId" />
      </n-form-item>
      <n-form-item label="应用说明">
        <n-input v-model:value="form.description" placeholder="例如：PL2 录制源 / VT 缺陷环境" />
      </n-form-item>
      <n-form-item label="SSH Host" required>
        <n-input v-model:value="form.ssh_host" placeholder="192.168.1.100" />
      </n-form-item>
      <n-form-item label="SSH User" required>
        <n-input v-model:value="form.ssh_user" placeholder="root" />
      </n-form-item>
      <n-form-item label="认证方式">
        <n-select v-model:value="form.ssh_auth_type" :options="authOptions" />
      </n-form-item>
      <n-form-item v-if="form.ssh_auth_type === 'KEY'" label="私钥路径">
        <n-input v-model:value="form.ssh_key_path" placeholder="/root/.ssh/id_rsa" />
      </n-form-item>
      <n-form-item v-else label="SSH 密码">
        <n-input v-model:value="form.ssh_password" type="password" />
      </n-form-item>
      <n-form-item label="JAR 名称">
        <n-input v-model:value="form.java_jar_name" placeholder="my-service.jar" />
      </n-form-item>
      <n-form-item label="应用端口">
        <n-input-number v-model:value="form.repeater_port" :min="1" :max="65535" />
      </n-form-item>
      <n-form-item label="高级配置">
        <n-space vertical style="width: 100%">
          <n-button tertiary size="small" @click="showAdvancedFields = !showAdvancedFields">
            {{ showAdvancedFields ? '收起高级配置' : '展开高级配置' }}
          </n-button>
          <n-alert v-if="showAdvancedFields" type="info" :show-icon="false">
            银行 / XML 场景建议配置“接口识别字段”和“默认忽略字段”。同一路径多交易码接口会按这里配置的字段识别，例如
            <n-text code>service_id</n-text>、
            <n-text code>trand_id</n-text>。
          </n-alert>
        </n-space>
      </n-form-item>
      <template v-if="showAdvancedFields">
        <n-form-item label="SSH 端口">
          <n-input-number v-model:value="form.ssh_port" :min="1" :max="65535" />
        </n-form-item>
        <n-form-item label="Sandbox 端口">
          <n-input-number v-model:value="form.sandbox_port" :min="1" :max="65535" />
        </n-form-item>
        <n-form-item label="Sandbox 路径">
          <n-input v-model:value="form.sandbox_home" placeholder="/root/.sandbox" />
        </n-form-item>
        <n-form-item label="录制数据目录">
          <n-input v-model:value="form.repeater_data_dir" placeholder="/root/.sandbox-module/repeater-data/record" />
        </n-form-item>
        <n-form-item label="采样率">
          <n-space align="center">
            <n-input-number v-model:value="form.sample_rate_percent" :min="1" :max="100" />
            <span>%</span>
          </n-space>
        </n-form-item>
        <n-form-item label="接口识别字段">
          <n-dynamic-tags v-model:value="form.operation_id_tags" />
          <template #feedback>
            留空也可用，系统会自动识别 <n-text code>service_id</n-text>、<n-text code>trand_id</n-text>、<n-text code>transCode</n-text> 等常见字段。
          </template>
        </n-form-item>
        <n-form-item label="默认忽略字段">
          <n-dynamic-tags v-model:value="form.default_ignore_fields" />
          <template #feedback>
            这里的字段会在发起回放时作为默认值自动带入。
          </template>
        </n-form-item>
      </template>
    </n-form>
    <template #action>
      <n-button @click="showForm = false">取消</n-button>
      <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NButton, NDataTable, NModal, NForm, NFormItem,
  NInput, NInputNumber, NSelect, NTag, NSpace, NDatePicker, NDynamicTags, NAlert, NText, useMessage, useDialog,
} from 'naive-ui'
import { applicationApi, type Application } from '@/api/applications'
import { createDateShortcuts, inDateRange, type DateRangeValue } from '@/utils/dateRange'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const apps = ref<Application[]>([])
const loading = ref(false)
const showForm = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const showAdvancedFields = ref(false)

const searchKeyword = ref('')
const searchAgentStatus = ref<string | null>(null)
const searchCreatedRange = ref<DateRangeValue>(null)
const sortOrder = ref<'ascend' | 'descend'>('descend')
const dateShortcuts = createDateShortcuts()

const filteredApps = computed(() => {
  let list = apps.value
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(a =>
      a.name.toLowerCase().includes(kw) ||
      (a.ssh_host || '').toLowerCase().includes(kw)
    )
  }
  if (searchAgentStatus.value) {
    list = list.filter(a => a.agent_status === searchAgentStatus.value)
  }
  if (searchCreatedRange.value) {
    list = list.filter(a => inDateRange(a.created_at, searchCreatedRange.value))
  }
  list = [...list].sort((a, b) => {
    const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    return sortOrder.value === 'ascend' ? diff : -diff
  })
  return list
})

const agentStatusLabel: Record<string, string> = {
  ATTACHED: '已挂载',
  DETACHED: '已卸载',
  ERROR: '错误',
  UNKNOWN: '未知',
}

const agentStatusOptions = [
  { label: '已挂载', value: 'ATTACHED' },
  { label: '已卸载', value: 'DETACHED' },
  { label: '错误', value: 'ERROR' },
  { label: '未知', value: 'UNKNOWN' },
]

const authOptions = [
  { label: 'SSH Key', value: 'KEY' },
  { label: '密码', value: 'PASSWORD' },
]

const emptyForm = () => ({
  name: '',
  description: '',
  ssh_host: '',
  ssh_port: 22,
  ssh_user: 'root',
  ssh_auth_type: 'KEY' as 'KEY' | 'PASSWORD',
  ssh_key_path: '',
  ssh_password: '',
  java_jar_name: '',
  sandbox_port: 39393,
  repeater_port: 8080,
  sandbox_home: '/root/.sandbox',
  repeater_data_dir: '/root/.sandbox-module/repeater-data/record',
  sample_rate_percent: 100,
  operation_id_tags: [] as string[],
  default_ignore_fields: [] as string[],
})

const form = ref(emptyForm())

const statusColor: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
  ATTACHED: 'success',
  DETACHED: 'warning',
  ERROR: 'error',
  UNKNOWN: 'default',
}

const columns = computed(() => [
  { title: '应用名称', key: 'name' },
  { title: 'SSH Host', key: 'ssh_host' },
  {
    title: '注册时间',
    key: 'created_at',
    width: 170,
    sorter: true,
    sortOrder: sortOrder.value,
    render: (row: Application) => new Date(row.created_at).toLocaleString(),
  },
  {
    title: 'Agent 状态',
    key: 'agent_status',
    render: (row: Application) =>
      h(NTag, { type: statusColor[row.agent_status] || 'default', size: 'small' }, () => agentStatusLabel[row.agent_status] || row.agent_status),
  },
  { title: 'PID', key: 'java_pid', render: (row: Application) => row.java_pid || '-' },
  {
    title: '操作',
    key: 'actions',
    render: (row: Application) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, { size: 'small', onClick: () => openEdit(row) }, () => '编辑'),
        h(NButton, { size: 'small', type: 'primary', onClick: () => router.push(`/applications/${row.id}`) }, () => '详情'),
        h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row) }, () => '删除'),
      ]),
  },
])

function clearFilters() {
  searchKeyword.value = ''
  searchAgentStatus.value = null
  searchCreatedRange.value = null
}

function onSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (sorter?.columnKey === 'created_at') {
    sortOrder.value = sorter.order || 'descend'
  }
}

function openCreate() {
  editingId.value = null
  form.value = emptyForm()
  showAdvancedFields.value = false
  showForm.value = true
}

function openEdit(row: Application) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    description: row.description || '',
    ssh_host: row.ssh_host,
    ssh_port: row.ssh_port ?? 22,
    ssh_user: row.ssh_user,
    ssh_auth_type: (row.ssh_auth_type as 'KEY' | 'PASSWORD') || 'KEY',
    ssh_key_path: row.ssh_key_path || '',
    ssh_password: row.ssh_password || '',
    java_jar_name: row.java_jar_name || '',
    sandbox_port: row.sandbox_port ?? 39393,
    repeater_port: row.repeater_port ?? 8080,
    sandbox_home: row.sandbox_home || '/root/.sandbox',
    repeater_data_dir: row.repeater_data_dir || '/root/.sandbox-module/repeater-data/record',
    sample_rate_percent: Math.round((row.sample_rate ?? 1) * 100),
    operation_id_tags: [...(row.operation_id_tags ?? [])],
    default_ignore_fields: [...(row.default_ignore_fields ?? [])],
  }
  showAdvancedFields.value = true
  showForm.value = true
}

async function loadApps() {
  loading.value = true
  try {
    const res = await applicationApi.list()
    apps.value = res.data
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!form.value.name.trim()) { message.warning('请填写应用名称'); return }
  if (!form.value.ssh_host.trim()) { message.warning('请填写 SSH Host'); return }
  if (!form.value.ssh_user.trim()) { message.warning('请填写 SSH User'); return }
  saving.value = true
  try {
    const payload: any = {
      ...form.value,
      sample_rate: (form.value.sample_rate_percent || 100) / 100,
      operation_id_tags: form.value.operation_id_tags.length ? form.value.operation_id_tags : undefined,
      default_ignore_fields: form.value.default_ignore_fields.length ? form.value.default_ignore_fields : undefined,
    }
    delete payload.sample_rate_percent
    if (!payload.ssh_key_path) delete payload.ssh_key_path
    if (!payload.ssh_password) delete payload.ssh_password
    if (!payload.description) delete payload.description
    if (editingId.value) {
      await applicationApi.update(editingId.value, payload)
      message.success('应用更新成功')
    } else {
      await applicationApi.create(payload)
      message.success('应用注册成功')
    }
    showForm.value = false
    await loadApps()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

function handleDelete(row: Application) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除应用「${row.name}」吗？关联的录制数据、回放任务和定时任务将一并删除，且不可恢复。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await applicationApi.delete(row.id)
        message.success('应用已删除')
        await loadApps()
      } catch (e: any) {
        message.error(e.response?.data?.detail || '删除失败')
      }
    },
  })
}

onMounted(loadApps)
</script>
