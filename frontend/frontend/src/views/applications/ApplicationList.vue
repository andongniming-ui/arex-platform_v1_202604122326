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
      :row-key="(row: Application) => row.id"
      :pagination="{ pageSize: 10, showSizePicker: true, pageSizes: [10, 20, 50] }"
      @update:sorter="onSorterChange"
    />
  </n-card>

  <!-- Create / Edit dialog -->
  <n-modal v-model:show="showForm" preset="dialog" :title="editingId ? '编辑应用' : '注册新应用'" style="width: 760px">
    <application-editor-form
      v-model="form"
      v-model:show-advanced="showAdvancedFields"
      :name-disabled="!!editingId"
    />
    <template #action>
      <n-button @click="showForm = false">取消</n-button>
      <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, h, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton, NCard, NDataTable, NDatePicker, NInput, NModal, NSelect, NSpace, NTag, useDialog, useMessage,
} from 'naive-ui'
import { applicationApi, type Application } from '@/api/applications'
import ApplicationEditorForm from '@/components/applications/ApplicationEditorForm.vue'
import { usePageSummary } from '@/composables/usePageSummary'
import { createDateShortcuts, inDateRange, type DateRangeValue } from '@/utils/dateRange'
import {
  buildApplicationPayload,
  createApplicationEditorModel,
  createEmptyApplicationEditorModel,
  type ApplicationEditorModel,
} from '@/utils/applicationEditor'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const { setPageSummary, clearPageSummary } = usePageSummary()
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

const form = ref<ApplicationEditorModel>(createEmptyApplicationEditorModel())

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
  form.value = createEmptyApplicationEditorModel()
  showAdvancedFields.value = false
  showForm.value = true
}

function openEdit(row: Application) {
  editingId.value = row.id
  form.value = createApplicationEditorModel(row)
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
    const payload = buildApplicationPayload(form.value)
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

watch(() => filteredApps.value.length, (count) => {
  setPageSummary(`共 ${count} 条应用`)
}, { immediate: true })

onBeforeUnmount(clearPageSummary)
</script>
