<template>
  <n-card title="回放历史">
    <template #header-extra>
      <n-space align="center" wrap>
        <n-input
          v-model:value="filterKeyword"
          placeholder="搜索用例名称"
          clearable
          style="width: 160px"
          @update:value="onFilterChange"
          @clear="onFilterChange"
        />
        <n-select
          v-model:value="filterCaseId"
          :options="caseOptions"
          placeholder="按用例筛选"
          clearable
          filterable
          style="width: 160px"
          @update:value="onFilterChange"
        />
        <n-select
          v-model:value="filterAppId"
          :options="appOptions"
          placeholder="按应用筛选"
          clearable
          style="width: 160px"
          @update:value="onFilterChange"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          placeholder="按状态筛选"
          clearable
          style="width: 130px"
          @update:value="onFilterChange"
        />
        <n-date-picker
          v-model:value="filterCreatedRange"
          type="datetimerange"
          clearable
          :shortcuts="dateShortcuts"
          style="width: 320px"
          start-placeholder="回放开始时间"
          end-placeholder="回放结束时间"
          @update:value="onFilterChange"
          @clear="onFilterChange"
        />
        <n-button size="small" @click="clearFilters">清空筛选</n-button>
        <n-button size="small" @click="loadJobs">刷新</n-button>
      </n-space>
    </template>
    <n-space align="center" style="margin-bottom:10px">
      <span style="color:#999;font-size:13px">共 {{ jobTotal }} 条</span>
    </n-space>
    <n-data-table
      :columns="jobColumns"
      :data="jobs"
      :loading="jobsLoading"
      :pagination="jobPagination"
      :scroll-x="900"
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
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, h, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NSpace, NDataTable, NTag, NButton, NInput, NSelect, NPopconfirm, NDatePicker, useMessage, useDialog,
} from 'naive-ui'
import { replayApi, type ReplayJob, type ReplayJobCreate } from '@/api/replays'
import { usePageSummary } from '@/composables/usePageSummary'
import { fmtTime } from '@/utils/time'
import { testCaseApi } from '@/api/testCases'
import { applicationApi } from '@/api/applications'
import { createDateShortcuts, type DateRangeValue } from '@/utils/dateRange'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const { setPageSummary, clearPageSummary } = usePageSummary()

const caseOptions = ref<{ label: string; value: string }[]>([])
const appOptions = ref<{ label: string; value: string }[]>([])
const caseMap = ref<Record<string, string>>({})
const appMap = ref<Record<string, string>>({})
const jobs = ref<ReplayJob[]>([])
const jobsLoading = ref(false)
const jobTotal = ref(0)
const selectedIds = ref<string[]>([])
const batchDeleting = ref(false)
const replayingIds = ref<Set<string>>(new Set())

// 回放历史筛选
const filterKeyword = ref('')
const filterCaseId = ref<string | null>(null)
const filterAppId = ref<string | null>(null)
const filterStatus = ref<string | null>(null)
const filterCreatedRange = ref<DateRangeValue>(null)
const sortOrder = ref<'ascend' | 'descend'>('descend')
const dateShortcuts = createDateShortcuts()
const statusOptions = [
  { label: '已完成', value: 'DONE' },
  { label: '运行中', value: 'RUNNING' },
  { label: '失败', value: 'FAILED' },
  { label: '待处理', value: 'PENDING' },
  { label: '已取消', value: 'CANCELLED' },
]

const jobPagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  itemCount: 0,
  onChange: (page: number) => {
    jobPagination.page = page
    loadJobs()
  },
  onUpdatePageSize: (size: number) => {
    jobPagination.pageSize = size
    jobPagination.page = 1
    loadJobs()
  },
})

const statusColor: Record<string, any> = {
  DONE: 'success', RUNNING: 'info', PENDING: 'default', FAILED: 'error', CANCELLED: 'warning',
}

const statusLabel: Record<string, string> = {
  DONE: '已完成', RUNNING: '运行中', PENDING: '待处理', FAILED: '失败', CANCELLED: '已取消',
}

const jobColumns = computed(() => [
  { type: 'selection' as const, width: 40 },
  {
    title: '用例',
    key: 'case_id',
    render: (r: ReplayJob) => caseMap.value[r.case_id] || r.case_id.slice(0, 8),
  },
  {
    title: '目标应用',
    key: 'target_app_id',
    width: 150,
    render: (r: ReplayJob) => appMap.value[r.target_app_id] || r.target_app_id.slice(0, 8),
    ellipsis: { tooltip: true },
  },
  {
    title: '状态',
    key: 'status',
    render: (r: ReplayJob) =>
      h(NTag, { size: 'small', type: statusColor[r.status] || 'default' }, () => statusLabel[r.status] || r.status),
  },
  {
    title: '通过率',
    key: 'progress',
    width: 160,
    render: (r: ReplayJob) => {
      const sent = r.sent_count ?? 0
      const pass = r.success_count ?? 0
      const fail = r.fail_count ?? 0
      if (!sent) return h('span', { style: 'color:#999' }, '-')
      const pct = Math.round(pass / sent * 100)
      const color = pct >= 90 ? '#18a058' : pct >= 60 ? '#f0a020' : '#d03050'
      return h('span', { style: `color:${color};font-weight:bold` },
        `${pass}/${sent} (${pct}%) 失败:${fail}`)
    },
  },
  { title: '环境', key: 'environment', render: (r: ReplayJob) => r.environment || '-' },
  {
    title: 'Mock',
    key: 'mock',
    width: 70,
    render: (r: ReplayJob) =>
      r.use_sub_invocation_mocks
        ? h(NTag, { size: 'small', type: 'warning' }, () => 'Mock')
        : h('span', { style: 'color:#ccc' }, '-'),
  },
  {
    title: '创建时间',
    key: 'created_at',
    sorter: true,
    sortOrder: sortOrder.value,
    render: (r: ReplayJob) => fmtTime(r.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 240,
    render: (r: ReplayJob) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, {
          size: 'small',
          onClick: () => router.push(`/results/${r.id}`),
        }, () => '查看结果'),
        h(NButton, {
          size: 'small',
          type: 'primary',
          ghost: true,
          loading: replayingIds.value.has(r.id),
          onClick: () => reReplay(r),
        }, () => '重新回放'),
        h(NPopconfirm, { onPositiveClick: () => deleteJob(r.id) }, {
          trigger: () => h(NButton, { size: 'small', type: 'error' }, () => '删除'),
          default: () => '确认删除该回放记录？',
        }),
      ]),
  },
])

// 当筛选条件变化时重置到第一页再加载
function onFilterChange() {
  jobPagination.page = 1
  selectedIds.value = []
  loadJobs()
}

function clearFilters() {
  filterKeyword.value = ''
  filterCaseId.value = null
  filterAppId.value = null
  filterStatus.value = null
  filterCreatedRange.value = null
  onFilterChange()
}

function onSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (sorter?.columnKey === 'created_at') {
    sortOrder.value = sorter.order || 'descend'
    loadJobs()
  }
}

async function loadJobs() {
  jobsLoading.value = true
  try {
    const res = await replayApi.list({
      keyword: filterKeyword.value.trim() || undefined,
      case_id: filterCaseId.value || undefined,
      app_id: filterAppId.value || undefined,
      status: filterStatus.value || undefined,
      created_after: filterCreatedRange.value ? new Date(filterCreatedRange.value[0]).toISOString() : undefined,
      created_before: filterCreatedRange.value ? new Date(filterCreatedRange.value[1]).toISOString() : undefined,
      limit: jobPagination.pageSize,
      offset: (jobPagination.page - 1) * jobPagination.pageSize,
    })
    jobs.value = res.data.items
    jobTotal.value = res.data.total
    jobs.value = [...jobs.value].sort((a, b) => {
      const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      return sortOrder.value === 'ascend' ? diff : -diff
    })
    jobPagination.itemCount = jobTotal.value
  } finally {
    jobsLoading.value = false
  }
}

async function reReplay(r: ReplayJob) {
  replayingIds.value = new Set([...replayingIds.value, r.id])
  try {
    const payload: ReplayJobCreate = {
      case_id: r.case_id,
      target_app_id: r.target_app_id,
      environment: r.environment,
      concurrency: r.concurrency,
      delay_ms: r.delay_ms,
      override_host: r.override_host,
      ignore_fields: r.ignore_fields,
      diff_rules: r.diff_rules,
      assertions: r.assertions,
      perf_threshold_ms: r.perf_threshold_ms,
      use_sub_invocation_mocks: r.use_sub_invocation_mocks,
      webhook_url: r.webhook_url,
      notify_type: r.notify_type,
      smart_noise_reduction: r.smart_noise_reduction,
      repeat_count: r.repeat_count,
      header_transforms: r.header_transforms,
      retry_count: r.retry_count,
    }
    const res = await replayApi.create(payload)
    message.success('已创建新回放任务')
    router.push(`/results/${res.data.id}`)
  } catch {
    message.error('创建回放任务失败')
  } finally {
    const s = new Set(replayingIds.value)
    s.delete(r.id)
    replayingIds.value = s
  }
}

async function deleteJob(id: string) {
  await replayApi.delete(id)
  message.success('已删除')
  jobs.value = jobs.value.filter(j => j.id !== id)
  selectedIds.value = selectedIds.value.filter(i => i !== id)
}

async function deleteSelected() {
  dialog.warning({
    title: '确认批量删除',
    content: `将删除选中的 ${selectedIds.value.length} 条回放记录，确认吗？`,
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      batchDeleting.value = true
      try {
        await replayApi.batchDelete(selectedIds.value)
        message.success(`已删除 ${selectedIds.value.length} 条`)
        jobs.value = jobs.value.filter(j => !selectedIds.value.includes(j.id))
        selectedIds.value = []
        jobTotal.value = jobs.value.length
        jobPagination.itemCount = jobTotal.value
      } finally {
        batchDeleting.value = false
      }
    },
  })
}

onMounted(async () => {
  await Promise.all([
    testCaseApi.listAll().then(items => {
      caseOptions.value = items.map(c => ({ label: c.name, value: c.id }))
      caseMap.value = Object.fromEntries(items.map(c => [c.id, c.name]))
    }).catch(() => {}),
    applicationApi.list().then(appsRes => {
      appOptions.value = appsRes.data.map(a => ({ label: a.name, value: a.id }))
      appMap.value = Object.fromEntries(appsRes.data.map(a => [a.id, a.name]))
    }).catch(() => {}),
    loadJobs(),
  ])
})

watch(jobTotal, (count) => {
  setPageSummary(`共 ${count} 条回放记录`)
}, { immediate: true })

onBeforeUnmount(clearPageSummary)
</script>
