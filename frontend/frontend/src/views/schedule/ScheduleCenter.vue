<template>
  <n-space vertical :size="16">
    <n-card title="定时回放">
      <template #header-extra>
        <n-space wrap>
          <n-input
            v-model:value="searchKeyword"
            placeholder="搜索任务/用例名称"
            clearable
            style="width: 180px"
          />
          <n-select
            v-model:value="searchAppId"
            :options="appOptions"
            placeholder="按应用筛选"
            clearable
            style="width: 150px"
          />
          <n-select
            v-model:value="searchEnabled"
            :options="enabledOptions"
            placeholder="启用状态"
            clearable
            style="width: 110px"
          />
          <n-date-picker
            v-model:value="searchCreatedRange"
            type="datetimerange"
            clearable
            :shortcuts="dateShortcuts"
            style="width: 320px"
            start-placeholder="创建开始时间"
            end-placeholder="创建结束时间"
          />
          <n-button @click="clearFilters">清空筛选</n-button>
          <n-button type="primary" @click="openCreate">+ 新建定时任务</n-button>
        </n-space>
      </template>
      <n-space align="center" style="margin-bottom:10px">
        <span style="color:#999;font-size:13px">共 {{ filteredSchedules.length }} 条</span>
      </n-space>
      <n-data-table
        :columns="columns"
        :data="filteredSchedules"
        :loading="loading"
        :pagination="{ pageSize: 10, showSizePicker: true, pageSizes: [10, 20, 50] }"
        :row-key="(r: any) => r.id"
        :checked-row-keys="selectedIds"
        @update:checked-row-keys="selectedIds = $event as string[]"
        @update:sorter="onSorterChange"
      />
      <n-space v-if="selectedIds.length > 0" align="center" style="margin-top:10px">
        <span>已选 {{ selectedIds.length }} 条</span>
        <n-button size="small" type="error" :loading="batchDeleting" @click="deleteSelected">批量删除</n-button>
      </n-space>
    </n-card>
  </n-space>

  <!-- 新建/编辑弹窗 -->
  <n-modal v-model:show="showModal" preset="card" :title="editing ? '编辑定时任务' : '新建定时任务'" style="width:560px">
    <n-form :model="form" label-placement="left" label-width="120px" :rules="rules" ref="formRef">
      <n-form-item label="任务名称" path="name">
        <n-input v-model:value="form.name" placeholder="每日回归 / 冒烟测试..." />
      </n-form-item>
      <n-form-item label="测试用例" path="case_id">
        <n-select v-model:value="form.case_id" :options="caseOptions" filterable placeholder="选择测试用例" />
      </n-form-item>
      <n-form-item label="目标应用" path="target_app_id">
        <n-select v-model:value="form.target_app_id" :options="appOptions" placeholder="选择目标应用" />
      </n-form-item>
      <n-form-item label="Cron 表达式" path="cron_expr">
        <n-input v-model:value="form.cron_expr" placeholder="分 时 日 月 周，如 0 2 * * *" />
        <template #feedback>
          <span style="color:#999;font-size:12px">
            5字段标准cron：{{ cronPreview }}
          </span>
        </template>
      </n-form-item>
      <n-form-item label="并发数">
        <n-input-number v-model:value="form.concurrency" :min="1" :max="20" />
      </n-form-item>
      <n-form-item label="请求间隔(ms)">
        <n-input-number v-model:value="form.delay_ms" :min="0" />
      </n-form-item>
      <n-form-item label="环境标签">
        <n-input v-model:value="form.environment" placeholder="staging / prod（留空默认 scheduled）" />
      </n-form-item>
      <n-form-item label="Host 覆盖">
        <n-input v-model:value="form.override_host" placeholder="留空使用应用默认 host" />
      </n-form-item>
      <n-form-item label="性能阈值(ms)">
        <n-input-number v-model:value="form.perf_threshold_ms" :min="0" clearable placeholder="留空不启用" />
      </n-form-item>
      <n-form-item label="忽略字段">
        <n-dynamic-tags v-model:value="form.ignore_fields" />
      </n-form-item>
      <n-form-item label="通知 URL">
        <n-input v-model:value="form.webhook_url" placeholder="完成后回调，留空不通知" />
      </n-form-item>
      <n-form-item label="通知类型">
        <n-select v-model:value="form.notify_type" :options="notifyOptions" clearable placeholder="选择通知格式" />
      </n-form-item>
      <n-form-item label="启用">
        <n-switch v-model:value="form.enabled" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, h, watch } from 'vue'
import {
  NCard, NSpace, NButton, NDataTable, NModal, NForm, NFormItem,
  NInput, NInputNumber, NSelect, NSwitch, NDynamicTags, NTag, NPopconfirm, NDatePicker, useMessage, useDialog,
  NInputGroup,
} from 'naive-ui'
import { scheduleApi, type Schedule } from '@/api/schedules'
import { testCaseApi } from '@/api/testCases'
import { applicationApi } from '@/api/applications'
import { usePageSummary } from '@/composables/usePageSummary'
import { fmtTime } from '@/utils/time'
import { createDateShortcuts, inDateRange, type DateRangeValue } from '@/utils/dateRange'

const message = useMessage()
const dialog = useDialog()
const { setPageSummary, clearPageSummary } = usePageSummary()
const schedules = ref<Schedule[]>([])
const loading = ref(false)
const selectedIds = ref<string[]>([])
const batchDeleting = ref(false)

// 搜索筛选
const searchKeyword = ref('')
const searchAppId = ref<string | null>(null)
const searchEnabled = ref<string | null>(null)
const searchCreatedRange = ref<DateRangeValue>(null)
const sortOrder = ref<'ascend' | 'descend'>('descend')
const dateShortcuts = createDateShortcuts()

const filteredSchedules = computed(() => {
  let list = schedules.value
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(s =>
      s.name.toLowerCase().includes(kw) ||
      (caseMap.value[s.case_id] || '').toLowerCase().includes(kw)
    )
  }
  if (searchAppId.value) {
    list = list.filter(s => s.target_app_id === searchAppId.value)
  }
  if (searchEnabled.value !== null) {
    list = list.filter(s => s.enabled === (searchEnabled.value === 'true'))
  }
  if (searchCreatedRange.value) {
    list = list.filter(s => inDateRange(s.created_at, searchCreatedRange.value))
  }
  list = [...list].sort((a, b) => {
    const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    return sortOrder.value === 'ascend' ? diff : -diff
  })
  return list
})

const enabledOptions = [
  { label: '已启用', value: 'true' },
  { label: '已禁用', value: 'false' },
]
const saving = ref(false)
const showModal = ref(false)
const editing = ref<string | null>(null)
const formRef = ref()

const caseOptions = ref<{ label: string; value: string }[]>([])
const appOptions = ref<{ label: string; value: string }[]>([])
const caseMap = ref<Record<string, string>>({})
const appMap = ref<Record<string, string>>({})
const caseRecordingCount = ref<Record<string, number>>({})

const notifyOptions = [
  { label: '通用 JSON', value: 'generic' },
  { label: '钉钉 Webhook', value: 'dingtalk' },
  { label: '企业微信', value: 'wecom' },
]

const emptyForm = () => ({
  name: '', case_id: '', target_app_id: '',
  cron_expr: '0 2 * * *', enabled: true,
  concurrency: 1, delay_ms: 0,
  environment: '', override_host: '',
  perf_threshold_ms: null as number | null,
  ignore_fields: [] as string[],
  webhook_url: '', notify_type: null as string | null,
})
const form = ref(emptyForm())

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  case_id: [{ required: true, message: '请选择测试用例', trigger: 'change' }],
  target_app_id: [{ required: true, message: '请选择目标应用', trigger: 'change' }],
  cron_expr: [{ required: true, message: '请输入 cron 表达式', trigger: 'blur' }],
}

// Human-readable cron preview
const CRON_PRESETS: Record<string, string> = {
  '0 2 * * *': '每天 02:00',
  '0 9 * * *': '每天 09:00',
  '0 9 * * 1-5': '工作日 09:00',
  '0 */2 * * *': '每2小时',
  '*/30 * * * *': '每30分钟',
}
const cronPreview = computed(() => CRON_PRESETS[form.value.cron_expr] || '(自定义)')

const columns = computed(() => [
  { type: 'selection' as const, width: 40 },
  { title: '任务名称', key: 'name' },
  { title: '测试用例', key: 'case_id', render: (r: Schedule) => caseMap.value[r.case_id] || r.case_id.slice(0, 8) },
  { title: '目标应用', key: 'target_app_id', render: (r: Schedule) => appMap.value[r.target_app_id] || r.target_app_id.slice(0, 8) },
  { title: 'Cron', key: 'cron_expr', render: (r: Schedule) => h('code', r.cron_expr) },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
    sorter: true,
    sortOrder: sortOrder.value,
    render: (r: Schedule) => fmtTime(r.created_at),
  },
  {
    title: '状态', key: 'enabled', width: 80,
    render: (r: Schedule) =>
      h(NTag, { size: 'small', type: r.enabled ? 'success' : 'default' }, () => r.enabled ? '启用' : '禁用'),
  },
  { title: '最近执行', key: 'last_run_at', width: 160, render: (r: Schedule) => fmtTime(r.last_run_at) },
  {
    title: '操作', key: 'actions', width: 220,
    render: (r: Schedule) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, { size: 'small', onClick: () => openEdit(r) }, () => '编辑'),
        h(NButton, {
          size: 'small', type: r.enabled ? 'warning' : 'success',
          onClick: () => toggleEnabled(r),
        }, () => r.enabled ? '禁用' : '启用'),
        h(NButton, { size: 'small', type: 'info', onClick: () => runNow(r.id) }, () => '立即执行'),
        h(NPopconfirm, { onPositiveClick: () => handleDelete(r.id) }, {
          trigger: () => h(NButton, { size: 'small', type: 'error' }, () => '删除'),
          default: () => '确认删除该定时任务？',
        }),
      ]),
  },
])

function clearFilters() {
  searchKeyword.value = ''
  searchAppId.value = null
  searchEnabled.value = null
  searchCreatedRange.value = null
}

function onSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (sorter?.columnKey === 'created_at') {
    sortOrder.value = sorter.order || 'descend'
  }
}

function openCreate() {
  editing.value = null
  form.value = emptyForm()
  showModal.value = true
}

function openEdit(s: Schedule) {
  editing.value = s.id
  form.value = {
    name: s.name, case_id: s.case_id, target_app_id: s.target_app_id,
    cron_expr: s.cron_expr, enabled: s.enabled,
    concurrency: s.concurrency, delay_ms: s.delay_ms,
    environment: s.environment || '', override_host: s.override_host || '',
    perf_threshold_ms: s.perf_threshold_ms ?? null,
    ignore_fields: s.ignore_fields || [],
    webhook_url: s.webhook_url || '', notify_type: s.notify_type || null,
  }
  showModal.value = true
}

async function handleSave() {
  try { await formRef.value?.validate() } catch { return }
  if ((caseRecordingCount.value[form.value.case_id] ?? 0) === 0) {
    message.warning('该测试用例还没有添加任何录制接口，请先在测试用例库中添加录制后再创建定时任务')
    return
  }
  saving.value = true
  const payload: any = { ...form.value }
  if (!payload.webhook_url) delete payload.webhook_url
  if (!payload.notify_type) delete payload.notify_type
  if (!payload.ignore_fields?.length) delete payload.ignore_fields
  if (!payload.environment) delete payload.environment
  if (!payload.override_host) delete payload.override_host
  if (!payload.perf_threshold_ms) delete payload.perf_threshold_ms
  try {
    if (editing.value) {
      await scheduleApi.update(editing.value, payload)
      message.success('定时任务已更新')
    } else {
      await scheduleApi.create(payload)
      message.success('定时任务已创建')
    }
    showModal.value = false
    await load()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function toggleEnabled(s: Schedule) {
  await scheduleApi.update(s.id, { enabled: !s.enabled })
  message.success(s.enabled ? '已禁用' : '已启用')
  await load()
}

async function runNow(id: string) {
  await scheduleApi.runNow(id)
  message.success('已触发立即执行，回放任务已在后台启动')
}

async function handleDelete(id: string) {
  await scheduleApi.delete(id)
  message.success('已删除')
  selectedIds.value = selectedIds.value.filter(i => i !== id)
  await load()
}

async function deleteSelected() {
  dialog.warning({
    title: '确认批量删除',
    content: `将删除选中的 ${selectedIds.value.length} 个定时任务，确认吗？`,
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      batchDeleting.value = true
      try {
        await scheduleApi.batchDelete(selectedIds.value)
        message.success(`已删除 ${selectedIds.value.length} 个定时任务`)
        selectedIds.value = []
        await load()
      } finally {
        batchDeleting.value = false
      }
    },
  })
}

async function load() {
  loading.value = true
  try {
    const res = await scheduleApi.list()
    schedules.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const [casesRes, appsRes] = await Promise.all([
    testCaseApi.listAll(),
    applicationApi.list(),
  ])
  caseOptions.value = casesRes.map(c => ({ label: c.name, value: c.id }))
  caseMap.value = Object.fromEntries(casesRes.map(c => [c.id, c.name]))
  caseRecordingCount.value = Object.fromEntries(casesRes.map(c => [c.id, c.recording_count]))
  appOptions.value = appsRes.data.map(a => ({ label: a.name, value: a.id }))
  appMap.value = Object.fromEntries(appsRes.data.map(a => [a.id, a.name]))
  await load()
})

watch(() => filteredSchedules.value.length, (count) => {
  setPageSummary(`共 ${count} 条定时任务`)
}, { immediate: true })

onBeforeUnmount(clearPageSummary)
</script>
