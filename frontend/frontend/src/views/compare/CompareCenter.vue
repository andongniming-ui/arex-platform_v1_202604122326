<template>
  <n-space vertical :size="16">
    <n-card title="双环境对比">
      <template #header-extra>
        <n-space align="center" wrap>
        <n-input
          v-model:value="searchRunName"
          placeholder="搜索名称/用例/应用"
          clearable
          style="width: 200px"
          @keyup.enter="onRunFilterChange"
          @clear="onRunFilterChange"
        />
          <n-select
            v-model:value="searchRunStatus"
            :options="runStatusOptions"
            placeholder="按状态筛选"
            clearable
            style="width: 130px"
          @update:value="onRunFilterChange"
        />
          <n-date-picker
            v-model:value="searchRunCreatedRange"
            type="datetimerange"
            clearable
            :shortcuts="dateShortcuts"
            style="width: 320px"
            start-placeholder="对比开始时间"
            end-placeholder="对比结束时间"
          @update:value="onRunFilterChange"
          @clear="onRunFilterChange"
        />
          <n-button size="small" @click="clearFilters">清空筛选</n-button>
          <n-button type="primary" size="small" @click="showCreate = true">+ 新建对比</n-button>
        </n-space>
      </template>

      <n-space align="center" style="margin-bottom:10px">
        <span style="color:#999;font-size:13px">共 {{ runsTotal }} 条</span>
      </n-space>
      <n-data-table
        :columns="runColumns"
        :data="filteredRuns"
        :loading="loading"
        :row-key="(r: CompareRun) => r.id"
        :checked-row-keys="selectedIds"
        :pagination="runsPagination"
        @update:checked-row-keys="selectedIds = $event as string[]"
        @update:sorter="onSorterChange"
      />
      <n-space v-if="selectedIds.length > 0" align="center" style="margin-top:10px">
        <span>已选 {{ selectedIds.length }} 条</span>
        <n-button size="small" type="error" :loading="batchDeleting" @click="deleteSelected">批量删除</n-button>
      </n-space>
    </n-card>

    <!-- Result Detail -->
    <n-card v-if="activeRun" :title="`对比结果：${activeRun.name || activeRun.id.slice(0, 8)}`">
      <template #header-extra>
        <n-space align="center">
          <n-button
            size="small"
            :disabled="activeRun.status !== 'DONE'"
            @click="exportReport(activeRun!.id)"
          >
            导出 HTML 报告
          </n-button>
          <n-popconfirm @positive-click="deleteRun(activeRun!.id)">
            <template #trigger>
              <n-button size="small" type="error">删除</n-button>
            </template>
            确认删除此对比记录？
          </n-popconfirm>
        </n-space>
      </template>

      <!-- Summary -->
      <n-descriptions bordered :column="4" style="margin-bottom:16px">
        <n-descriptions-item label="状态">
          <n-tag :type="activeRun.status === 'DONE' ? 'success' : activeRun.status === 'FAILED' ? 'error' : 'info'" size="small">
            {{ activeRun.status === 'DONE' ? '已完成' : activeRun.status === 'FAILED' ? '失败' : '运行中' }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="总录制数">{{ activeRun.total_count }}</n-descriptions-item>
        <n-descriptions-item label="一致">
          <span style="color:#18a058;font-weight:bold">{{ activeRun.agreed_count }}</span>
        </n-descriptions-item>
        <n-descriptions-item label="差异">
          <span style="color:#d03050;font-weight:bold">{{ activeRun.diverged_count }}</span>
        </n-descriptions-item>
      </n-descriptions>

      <!-- Results Filter -->
      <n-space style="margin-bottom:10px">
        <n-input
          v-model:value="searchResultPath"
          placeholder="按接口路径搜索"
          clearable
          style="width: 220px"
          @keyup.enter="onResultFilterChange"
          @clear="onResultFilterChange"
        />
        <n-select
          v-model:value="searchResultStatus"
          :options="compareStatusOptions"
          placeholder="一致性筛选"
          clearable
          style="width: 130px"
          @update:value="onResultFilterChange"
        />
        <n-button size="small" @click="loadResults(activeRun!.id)">刷新</n-button>
        <span style="color:#999;font-size:13px">共 {{ resultsTotal }} 条</span>
      </n-space>
      <!-- Results Table -->
      <n-data-table
        :columns="resultColumns"
        :data="filteredResults"
        :loading="resultsLoading"
        size="small"
        :scroll-x="1000"
        :pagination="resultsPagination"
      />
    </n-card>

    <!-- Create Modal -->
    <n-modal v-model:show="showCreate" preset="dialog" title="新建双环境对比" style="width:520px">
      <n-form :model="createForm" label-placement="left" label-width="120px">
        <n-form-item label="名称">
          <n-input v-model:value="createForm.name" placeholder="可选，便于识别" />
        </n-form-item>
        <n-form-item label="测试用例" required>
          <n-select v-model:value="createForm.case_id" :options="caseOptions" filterable placeholder="选择测试用例" />
        </n-form-item>
        <n-form-item label="应用 A" required>
          <n-select v-model:value="createForm.app_a_id" :options="appOptions" placeholder="基准环境" />
        </n-form-item>
        <n-form-item label="应用 B" required>
          <n-select v-model:value="createForm.app_b_id" :options="appOptions" placeholder="对比环境" />
        </n-form-item>
        <n-form-item label="忽略字段">
          <n-dynamic-tags v-model:value="createForm.ignore_fields" />
        </n-form-item>
        <n-form-item label="并发数">
          <n-input-number v-model:value="createForm.concurrency" :min="1" :max="10" />
        </n-form-item>
        <n-form-item label="请求间隔(ms)">
          <n-input-number v-model:value="createForm.delay_ms" :min="0" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showCreate = false">取消</n-button>
        <n-button type="primary" :loading="creating" @click="createRun">开始对比</n-button>
      </template>
    </n-modal>

    <!-- Detail Modal -->
    <n-modal v-model:show="showDetail" style="width:860px;max-height:90vh" :mask-closable="true">
      <n-card :title="`接口对比：${detailResult?.path || '-'}`" closable @close="showDetail = false">
        <n-descriptions bordered :column="2" style="margin-bottom:16px">
          <n-descriptions-item label="应用 A 状态">
            <n-tag :type="detailResult?.status_a === 'PASS' ? 'success' : 'error'" size="small">
              {{ detailResult?.status_a === 'PASS' ? '通过' : detailResult?.status_a === 'FAIL' ? '失败' : detailResult?.status_a || '-' }}
            </n-tag>
            &nbsp; {{ detailResult?.duration_a_ms ?? '-' }} ms &nbsp; 差异分: {{ fmtScore(detailResult?.diff_score_a) }}
          </n-descriptions-item>
          <n-descriptions-item label="应用 B 状态">
            <n-tag :type="detailResult?.status_b === 'PASS' ? 'success' : 'error'" size="small">
              {{ detailResult?.status_b === 'PASS' ? '通过' : detailResult?.status_b === 'FAIL' ? '失败' : detailResult?.status_b || '-' }}
            </n-tag>
            &nbsp; {{ detailResult?.duration_b_ms ?? '-' }} ms &nbsp; 差异分: {{ fmtScore(detailResult?.diff_score_b) }}
          </n-descriptions-item>
        </n-descriptions>
        <div style="font-weight:600;margin-bottom:6px">A vs B 直接差异（分: {{ fmtScore(detailResult?.diff_score_a_vs_b) }}）</div>
        <n-input
          :value="fmtJson(detailResult?.diff_a_vs_b)"
          type="textarea"
          :rows="10"
          readonly
          style="font-family:monospace;font-size:12px"
        />
        <n-grid :cols="2" :x-gap="12" style="margin-top:12px">
          <n-gi>
            <div style="font-weight:600;margin-bottom:4px">应用 A 响应</div>
            <n-input :value="fmtJson(detailResult?.resp_a)" type="textarea" :rows="10" readonly style="font-family:monospace;font-size:12px" />
          </n-gi>
          <n-gi>
            <div style="font-weight:600;margin-bottom:4px">应用 B 响应</div>
            <n-input :value="fmtJson(detailResult?.resp_b)" type="textarea" :rows="10" readonly style="font-family:monospace;font-size:12px" />
          </n-gi>
        </n-grid>
      </n-card>
    </n-modal>
  </n-space>
</template>

<script setup lang="ts">
import { ref, reactive, computed, h, onMounted, onBeforeUnmount, watch } from 'vue'
import {
  NCard, NSpace, NButton, NDataTable, NModal, NForm, NFormItem,
  NInput, NInputNumber, NSelect, NDynamicTags, NTag, NDescriptions,
  NDescriptionsItem, NGrid, NGi, NPopconfirm, useMessage, useDialog,
  NDatePicker,
} from 'naive-ui'
import { compareApi, type CompareRun, type CompareResult } from '@/api/compare'
import { applicationApi } from '@/api/applications'
import { testCaseApi } from '@/api/testCases'
import { usePageSummary } from '@/composables/usePageSummary'
import { fmtTime } from '@/utils/time'
import { createDateShortcuts, type DateRangeValue } from '@/utils/dateRange'

const message = useMessage()
const dialog = useDialog()
const { setPageSummary, clearPageSummary } = usePageSummary()

const runs = ref<CompareRun[]>([])
const loading = ref(false)
const selectedIds = ref<string[]>([])
const batchDeleting = ref(false)
const activeRun = ref<CompareRun | null>(null)
const results = ref<CompareResult[]>([])
const resultsLoading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const showDetail = ref(false)
const detailResult = ref<CompareResult | null>(null)

const searchRunName = ref('')
const searchRunStatus = ref<string | null>(null)
const searchRunCreatedRange = ref<DateRangeValue>(null)
const sortOrder = ref<'ascend' | 'descend'>('descend')
const dateShortcuts = createDateShortcuts()
const filteredRuns = computed(() => runs.value)
const runStatusOptions = [
  { label: '已完成', value: 'DONE' },
  { label: '运行中', value: 'RUNNING' },
  { label: '失败', value: 'FAILED' },
]

const runsPagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  itemCount: 0,
  onChange: (page: number) => { runsPagination.page = page; loadRuns() },
  onUpdatePageSize: (size: number) => { runsPagination.pageSize = size; runsPagination.page = 1; loadRuns() },
})

const searchResultPath = ref('')
const searchResultStatus = ref<string | null>(null)
const filteredResults = computed(() => {
  return results.value
})
const compareStatusOptions = [
  { label: '仅看差异', value: 'diverged' },
  { label: '仅看一致', value: 'agreed' },
]

const resultsPagination = reactive({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [20, 50, 100],
  itemCount: 0,
  onChange: (page: number) => {
    resultsPagination.page = page
    if (activeRun.value) loadResults(activeRun.value.id)
  },
  onUpdatePageSize: (size: number) => {
    resultsPagination.pageSize = size
    resultsPagination.page = 1
    if (activeRun.value) loadResults(activeRun.value.id)
  },
})

const runsTotal = ref(0)
const resultsTotal = ref(0)
const appOptions = ref<{ label: string; value: string }[]>([])
const caseOptions = ref<{ label: string; value: string }[]>([])
const appMap = ref<Record<string, string>>({})
const caseMap = ref<Record<string, string>>({})

const createForm = ref({
  name: '',
  case_id: '',
  app_a_id: '',
  app_b_id: '',
  ignore_fields: [] as string[],
  concurrency: 1,
  delay_ms: 0,
})

function fmtScore(s?: number | null) {
  if (s == null) return '-'
  return s.toFixed(3)
}

function fmtJson(s?: string | null) {
  if (!s) return ''
  try { return JSON.stringify(JSON.parse(s), null, 2) } catch { return s }
}

const statusTag = (s?: string | null) =>
  h(NTag, { type: s === 'PASS' ? 'success' : 'error', size: 'small' }, () => s === 'PASS' ? '通过' : s === 'FAIL' ? '失败' : s || '-')

const runColumns = computed(() => [
  { type: 'selection' as const, width: 40 },
  { title: '名称', key: 'name', render: (r: CompareRun) => r.name || '-' },
  { title: '测试用例', key: 'case', render: (r: CompareRun) => caseMap.value[r.case_id] || r.case_id.slice(0, 8) },
  { title: '应用 A', key: 'app_a', render: (r: CompareRun) => appMap.value[r.app_a_id] || r.app_a_id.slice(0, 8) },
  { title: '应用 B', key: 'app_b', render: (r: CompareRun) => appMap.value[r.app_b_id] || r.app_b_id.slice(0, 8) },
  {
    title: '状态', key: 'status', width: 90,
    render: (r: CompareRun) => h(NTag, {
      type: r.status === 'DONE' ? 'success' : r.status === 'FAILED' ? 'error' : 'info',
      size: 'small',
    }, () => r.status === 'DONE' ? '已完成' : r.status === 'FAILED' ? '失败' : '运行中'),
  },
  {
    title: '一致/差异', key: 'counts', width: 120,
    render: (r: CompareRun) =>
      h('span', null, [
        h('span', { style: 'color:#18a058' }, `${r.agreed_count}✓ `),
        h('span', { style: 'color:#d03050' }, `${r.diverged_count}✗`),
        h('span', { style: 'color:#999' }, ` / ${r.total_count}`),
      ]),
  },
  {
    title: '创建时间',
    key: 'created_at',
    sorter: true,
    sortOrder: sortOrder.value,
    render: (r: CompareRun) => fmtTime(r.created_at),
  },
  {
    title: '操作', key: 'actions', width: 100,
    render: (r: CompareRun) => h(NButton, { size: 'small', onClick: () => openRun(r) }, () => '查看结果'),
  },
])

const resultColumns = [
  {
    title: '接口', key: 'path',
    render: (r: CompareResult) => {
      const path = r.path || '-'
      if (!r.service_id) return h('span', { style: 'font-family:monospace;font-size:13px' }, path)
      return h('div', [
        h('span', { style: 'font-family:monospace;font-size:13px' }, path),
        h('div', { style: 'font-size:11px;color:#888;margin-top:2px;font-family:monospace;letter-spacing:0.5px' }, r.service_id),
      ])
    },
  },
  { title: 'A 状态', key: 'status_a', width: 80, render: (r: CompareResult) => statusTag(r.status_a) },
  { title: 'A 差异分', key: 'diff_a', width: 90, render: (r: CompareResult) => fmtScore(r.diff_score_a) },
  { title: 'B 状态', key: 'status_b', width: 80, render: (r: CompareResult) => statusTag(r.status_b) },
  { title: 'B 差异分', key: 'diff_b', width: 90, render: (r: CompareResult) => fmtScore(r.diff_score_b) },
  { title: 'A vs B', key: 'diff_ab', width: 90, render: (r: CompareResult) => fmtScore(r.diff_score_a_vs_b) },
  {
    title: '一致性', key: 'agree', width: 80,
    render: (r: CompareResult) => {
      const agreed = r.status_a === r.status_b
      return h(NTag, { type: agreed ? 'success' : 'error', size: 'small' }, () => agreed ? '一致' : '差异')
    },
  },
  {
    title: '操作', key: 'action', width: 80,
    render: (r: CompareResult) => h(NButton, {
      size: 'small',
      onClick: () => { detailResult.value = r; showDetail.value = true },
    }, () => '详情'),
  },
]

async function loadRuns() {
  loading.value = true
  try {
    const res = await compareApi.list({
      keyword: searchRunName.value.trim() || undefined,
      status: searchRunStatus.value || undefined,
      created_after: searchRunCreatedRange.value ? new Date(searchRunCreatedRange.value[0]).toISOString() : undefined,
      created_before: searchRunCreatedRange.value ? new Date(searchRunCreatedRange.value[1]).toISOString() : undefined,
      limit: runsPagination.pageSize,
      offset: (runsPagination.page - 1) * runsPagination.pageSize,
    })
    runs.value = res.data.items
    runs.value = [...runs.value].sort((a, b) => {
      const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      return sortOrder.value === 'ascend' ? diff : -diff
    })
    runsTotal.value = res.data.total
    runsPagination.itemCount = res.data.total
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  searchRunName.value = ''
  searchRunStatus.value = null
  searchRunCreatedRange.value = null
  runsPagination.page = 1
  loadRuns()
}

function onRunFilterChange() {
  runsPagination.page = 1
  loadRuns()
}

function onSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (sorter?.columnKey === 'created_at') {
    sortOrder.value = sorter.order || 'descend'
    loadRuns()
  }
}

async function openRun(run: CompareRun) {
  activeRun.value = run
  resultsPagination.page = 1
  searchResultPath.value = ''
  searchResultStatus.value = null
  await loadResults(run.id)
}

async function loadResults(runId: string) {
  resultsLoading.value = true
  try {
    const res = await compareApi.results(runId, {
      path_contains: searchResultPath.value.trim() || undefined,
      agreement: searchResultStatus.value || undefined,
      limit: resultsPagination.pageSize,
      offset: (resultsPagination.page - 1) * resultsPagination.pageSize,
    })
    results.value = res.data.items
    resultsTotal.value = res.data.total
    resultsPagination.itemCount = res.data.total
  } finally {
    resultsLoading.value = false
  }
}

function onResultFilterChange() {
  resultsPagination.page = 1
  if (activeRun.value) {
    loadResults(activeRun.value.id)
  }
}

async function createRun() {
  if (!createForm.value.case_id || !createForm.value.app_a_id || !createForm.value.app_b_id) {
    message.warning('请选择测试用例和两个应用')
    return
  }
  if (createForm.value.app_a_id === createForm.value.app_b_id) {
    message.warning('应用 A 和应用 B 不能相同')
    return
  }
  creating.value = true
  try {
    const payload: any = { ...createForm.value }
    if (!payload.name) delete payload.name
    if (!payload.ignore_fields?.length) delete payload.ignore_fields
    const res = await compareApi.create(payload)
    runs.value.unshift(res.data)
    showCreate.value = false
    message.success('对比任务已创建')
    await openRun(res.data)
  } catch (e: any) {
    message.error(e.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

async function deleteRun(id: string) {
  try {
    await compareApi.delete(id)
    runs.value = runs.value.filter(r => r.id !== id)
    selectedIds.value = selectedIds.value.filter(i => i !== id)
    if (activeRun.value?.id === id) activeRun.value = null
    runsTotal.value = runs.value.length
    message.success('已删除')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '删除失败')
  }
}

async function deleteSelected() {
  dialog.warning({
    title: '确认批量删除',
    content: `将删除选中的 ${selectedIds.value.length} 条对比记录，确认吗？`,
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      batchDeleting.value = true
      try {
        await compareApi.batchDelete(selectedIds.value)
        message.success(`已删除 ${selectedIds.value.length} 条`)
        if (activeRun.value && selectedIds.value.includes(activeRun.value.id)) activeRun.value = null
        runs.value = runs.value.filter(r => !selectedIds.value.includes(r.id))
        selectedIds.value = []
        runsTotal.value = runs.value.length
        runsPagination.itemCount = runsTotal.value
      } finally {
        batchDeleting.value = false
      }
    },
  })
}

function exportReport(runId: string) {
  window.open(compareApi.reportUrl(runId), '_blank')
}

onMounted(async () => {
  await Promise.all([
    applicationApi.list().then(appsRes => {
      appOptions.value = appsRes.data.map(a => ({ label: a.name, value: a.id }))
      appMap.value = Object.fromEntries(appsRes.data.map(a => [a.id, a.name]))
    }).catch(() => {}),
    testCaseApi.listAll().then(items => {
      caseOptions.value = items.map(c => ({ label: c.name, value: c.id }))
      caseMap.value = Object.fromEntries(items.map(c => [c.id, c.name]))
    }).catch(() => {}),
    loadRuns(),
  ])
})

watch([runsTotal, resultsTotal, activeRun], ([runCount, resultCount, currentRun]) => {
  if (currentRun) {
    setPageSummary(`共 ${resultCount} 条对比结果`)
    return
  }
  setPageSummary(`共 ${runCount} 条对比记录`)
}, { immediate: true })

onBeforeUnmount(clearPageSummary)
</script>
