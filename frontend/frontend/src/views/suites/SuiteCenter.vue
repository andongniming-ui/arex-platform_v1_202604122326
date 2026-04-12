<template>
  <n-space vertical :size="16">
    <n-card title="回放套件">
      <template #header-extra>
        <n-space wrap>
          <n-input
            v-model:value="searchSuiteName"
            placeholder="搜索套件名称"
            clearable
            style="width: 180px"
          />
          <n-date-picker
            v-model:value="searchSuiteCreatedRange"
            type="datetimerange"
            clearable
            :shortcuts="dateShortcuts"
            style="width: 320px"
            start-placeholder="创建开始时间"
            end-placeholder="创建结束时间"
          />
          <n-button size="small" @click="clearFilters">清空筛选</n-button>
          <n-button type="primary" size="small" @click="openCreate">+ 新建套件</n-button>
        </n-space>
      </template>
      <n-space align="center" style="margin-bottom:10px">
        <span style="color:#999;font-size:13px">共 {{ filteredSuites.length }} 条</span>
      </n-space>
      <n-data-table
        :columns="suiteColumns"
        :data="filteredSuites"
        :loading="loading"
        :row-key="(r: Suite) => r.id"
        :pagination="suitePagination"
        @update:sorter="onSorterChange"
      />
    </n-card>

    <!-- Suite Detail / Run Panel -->
    <n-card v-if="activeSuite" :title="`套件：${activeSuite.name}`">
      <template #header-extra>
        <n-space>
          <n-button size="small" @click="openEdit(activeSuite)">编辑</n-button>
          <n-popconfirm @positive-click="deleteSuite(activeSuite.id)">
            <template #trigger>
              <n-button size="small" type="error">删除</n-button>
            </template>
            确认删除套件？
          </n-popconfirm>
        </n-space>
      </template>

      <n-tabs type="line" animated>
        <n-tab-pane name="run" tab="执行套件">
          <n-form label-placement="left" label-width="130px" style="max-width:560px;margin-top:12px">
            <n-form-item label="回放目标应用" required>
              <n-select
                v-model:value="runForm.target_app_id"
                :options="appOptions"
                placeholder="选择目标应用"
              />
            </n-form-item>
            <n-form-item label="环境标签">
              <n-input v-model:value="runForm.environment" placeholder="staging / test（留空用套件默认）" />
            </n-form-item>
            <n-form-item label="Host 覆盖">
              <n-input v-model:value="runForm.override_host" placeholder="留空用套件默认" />
            </n-form-item>
            <n-form-item label="并发数">
              <n-input-number v-model:value="runForm.concurrency" :min="1" :max="20" placeholder="留空用套件默认" />
            </n-form-item>
            <n-form-item label="性能阈值(ms)">
              <n-input-number v-model:value="runForm.perf_threshold_ms" :min="0" placeholder="超过此耗时标记 PERF FAIL" />
            </n-form-item>
            <n-form-item>
              <n-button type="primary" :loading="running" @click="runSuite">执行套件</n-button>
            </n-form-item>
          </n-form>

          <n-divider />
          <div style="font-weight:600;margin-bottom:8px">执行历史 <span style="color:#999;font-size:13px;font-weight:normal">共 {{ suiteRuns.length }} 条</span></div>
          <n-data-table :columns="runColumns" :data="suiteRuns" :loading="runsLoading" size="small" :pagination="runsPagination" />
          <n-button size="tiny" style="margin-top:8px" @click="loadRuns(activeSuite.id)">刷新</n-button>
        </n-tab-pane>

        <n-tab-pane name="cases" tab="包含用例">
          <n-space vertical :size="8" style="margin-top:12px">
            <n-tag v-for="cid in activeSuite.case_ids" :key="cid" closable @close="removeCase(cid)">
              {{ caseMap[cid] || cid.slice(0, 8) }}
            </n-tag>
            <n-select
              v-model:value="addCaseId"
              :options="caseOptions"
              filterable
              clearable
              placeholder="添加测试用例"
              style="width:300px"
              @update:value="addCase"
            />
          </n-space>
        </n-tab-pane>
      </n-tabs>
    </n-card>

    <!-- Create/Edit Modal -->
    <n-modal v-model:show="showForm" preset="dialog" :title="editingId ? '编辑套件' : '新建套件'" style="width:520px">
      <n-form :model="form" label-placement="left" label-width="130px">
        <n-form-item label="套件名称" required>
          <n-input v-model:value="form.name" placeholder="如：用户模块回归测试" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="form.description" type="textarea" :rows="2" />
        </n-form-item>
        <n-form-item label="默认目标应用">
          <n-select v-model:value="form.default_target_app_id" :options="appOptions" clearable placeholder="运行时可覆盖" />
        </n-form-item>
        <n-form-item label="默认环境">
          <n-input v-model:value="form.default_environment" placeholder="staging" />
        </n-form-item>
        <n-form-item label="默认并发数">
          <n-input-number v-model:value="form.default_concurrency" :min="1" :max="20" />
        </n-form-item>
        <n-form-item label="默认延迟(ms)">
          <n-input-number v-model:value="form.default_delay_ms" :min="0" />
        </n-form-item>
        <n-form-item label="默认性能阈值(ms)">
          <n-input-number v-model:value="form.default_perf_threshold_ms" :min="0" clearable placeholder="不限制" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showForm = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="saveSuite">保存</n-button>
      </template>
    </n-modal>
  </n-space>
</template>

<script setup lang="ts">
import { ref, reactive, computed, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NSpace, NButton, NDataTable, NModal, NForm, NFormItem,
  NInput, NInputNumber, NSelect, NTag, NTabs, NTabPane, NDatePicker,
  NDivider, NPopconfirm, useMessage,
} from 'naive-ui'

import { suiteApi, type Suite, type SuiteRun } from '@/api/suites'
import { applicationApi } from '@/api/applications'
import { testCaseApi } from '@/api/testCases'
import { fmtTime } from '@/utils/time'
import { createDateShortcuts, inDateRange, type DateRangeValue } from '@/utils/dateRange'

const router = useRouter()
const message = useMessage()

const suites = ref<Suite[]>([])
const loading = ref(false)
const activeSuite = ref<Suite | null>(null)
const suiteRuns = ref<SuiteRun[]>([])
const runsLoading = ref(false)
const running = ref(false)
const saving = ref(false)
const showForm = ref(false)
const editingId = ref<string | null>(null)
const addCaseId = ref<string | null>(null)

const appOptions = ref<{ label: string; value: string }[]>([])
const caseOptions = ref<{ label: string; value: string }[]>([])
const caseMap = ref<Record<string, string>>({})

const runForm = ref({
  target_app_id: '',
  environment: '',
  override_host: '',
  concurrency: undefined as number | undefined,
  perf_threshold_ms: undefined as number | undefined,
})

const form = ref({
  name: '',
  description: '',
  default_target_app_id: undefined as string | undefined,
  default_environment: '',
  default_concurrency: 1,
  default_delay_ms: 0,
  default_perf_threshold_ms: undefined as number | undefined,
})

const searchSuiteName = ref('')
const searchSuiteCreatedRange = ref<DateRangeValue>(null)
const sortOrder = ref<'ascend' | 'descend'>('descend')
const dateShortcuts = createDateShortcuts()
const filteredSuites = computed(() => {
  let list = suites.value
  if (searchSuiteName.value) {
    const kw = searchSuiteName.value.toLowerCase()
    list = list.filter(s => s.name.toLowerCase().includes(kw))
  }
  if (searchSuiteCreatedRange.value) {
    list = list.filter(s => inDateRange(s.created_at, searchSuiteCreatedRange.value))
  }
  list = [...list].sort((a, b) => {
    const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    return sortOrder.value === 'ascend' ? diff : -diff
  })
  return list
})

const suitePagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => { suitePagination.page = page },
  onUpdatePageSize: (size: number) => { suitePagination.pageSize = size; suitePagination.page = 1 },
})

const runsPagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => { runsPagination.page = page },
  onUpdatePageSize: (size: number) => { runsPagination.pageSize = size; runsPagination.page = 1 },
})

const passRateColor = (rate: number) => rate >= 0.9 ? '#18a058' : rate >= 0.6 ? '#f0a020' : '#d03050'

const suiteColumns = computed(() => [
  { title: '名称', key: 'name' },
  {
    title: '用例数', key: 'case_count',
    render: (r: Suite) => r.case_ids?.length ?? 0,
  },
  { title: '默认环境', key: 'default_environment', render: (r: Suite) => r.default_environment || '-' },
  { title: '创建时间', key: 'created_at', sorter: true, sortOrder: sortOrder.value, render: (r: Suite) => fmtTime(r.created_at) },
  {
    title: '操作', key: 'actions', width: 120,
    render: (r: Suite) => h(NButton, { size: 'small', onClick: () => openSuite(r) }, () => '查看/执行'),
  },
])

function clearFilters() {
  searchSuiteName.value = ''
  searchSuiteCreatedRange.value = null
}

function onSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (sorter?.columnKey === 'created_at') {
    sortOrder.value = sorter.order || 'descend'
  }
}

const runColumns = [
  {
    title: '状态', key: 'status', width: 90,
    render: (r: SuiteRun) => h('span', {
      style: `color:${r.status === 'DONE' ? '#18a058' : r.status === 'FAILED' ? '#d03050' : '#f0a020'}`,
    }, r.status === 'DONE' ? '已完成' : r.status === 'FAILED' ? '失败' : '运行中'),
  },
  {
    title: '用例', key: 'cases',
    render: (r: SuiteRun) => `${r.passed_cases}/${r.total_cases} 通过`,
  },
  {
    title: '通过率', key: 'rate',
    render: (r: SuiteRun) => {
      const pct = Math.round((r.overall_pass_rate ?? 0) * 100)
      return h('span', { style: `color:${passRateColor(r.overall_pass_rate ?? 0)};font-weight:bold` }, `${pct}%`)
    },
  },
  { title: '开始时间', key: 'started_at', render: (r: SuiteRun) => fmtTime(r.started_at) },
  {
    title: '操作', key: 'actions', width: 120,
    render: (r: SuiteRun) => r.job_ids?.length
      ? h(NButton, {
          size: 'small',
          onClick: () => router.push(`/results/${r.job_ids[0]}`),
        }, () => '查看第1个任务')
      : '-',
  },
]

async function loadSuites() {
  loading.value = true
  try {
    const res = await suiteApi.list()
    suites.value = res.data
  } finally {
    loading.value = false
  }
}

async function loadRuns(suiteId: string) {
  runsLoading.value = true
  try {
    const res = await suiteApi.listRuns(suiteId)
    suiteRuns.value = res.data
  } finally {
    runsLoading.value = false
  }
}

function openSuite(suite: Suite) {
  activeSuite.value = suite
  runsPagination.page = 1
  runForm.value = {
    target_app_id: suite.default_target_app_id || '',
    environment: suite.default_environment || '',
    override_host: suite.default_override_host || '',
    concurrency: undefined,
    perf_threshold_ms: suite.default_perf_threshold_ms ?? undefined,
  }
  loadRuns(suite.id)
}

function openCreate() {
  editingId.value = null
  form.value = {
    name: '',
    description: '',
    default_target_app_id: undefined,
    default_environment: '',
    default_concurrency: 1,
    default_delay_ms: 0,
    default_perf_threshold_ms: undefined,
  }
  showForm.value = true
}

function openEdit(suite: Suite) {
  editingId.value = suite.id
  form.value = {
    name: suite.name,
    description: suite.description || '',
    default_target_app_id: suite.default_target_app_id || undefined,
    default_environment: suite.default_environment || '',
    default_concurrency: suite.default_concurrency ?? 1,
    default_delay_ms: suite.default_delay_ms ?? 0,
    default_perf_threshold_ms: suite.default_perf_threshold_ms ?? undefined,
  }
  showForm.value = true
}

async function saveSuite() {
  if (!form.value.name) { message.warning('请填写套件名称'); return }
  saving.value = true
  try {
    const payload = { ...form.value } as any
    if (!payload.default_environment) delete payload.default_environment
    if (!payload.description) delete payload.description
    if (!payload.default_perf_threshold_ms) delete payload.default_perf_threshold_ms

    if (editingId.value) {
      const res = await suiteApi.update(editingId.value, payload)
      const idx = suites.value.findIndex(s => s.id === editingId.value)
      if (idx >= 0) suites.value[idx] = res.data
      if (activeSuite.value?.id === editingId.value) activeSuite.value = res.data
    } else {
      const res = await suiteApi.create(payload)
      suites.value.unshift(res.data)
    }
    showForm.value = false
    message.success('保存成功')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteSuite(id: string) {
  try {
    await suiteApi.delete(id)
    suites.value = suites.value.filter(s => s.id !== id)
    if (activeSuite.value?.id === id) activeSuite.value = null
    message.success('已删除')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '删除失败')
  }
}

async function runSuite() {
  if (!activeSuite.value) return
  if (!runForm.value.target_app_id) { message.warning('请选择目标应用'); return }
  running.value = true
  try {
    const payload: any = { target_app_id: runForm.value.target_app_id }
    if (runForm.value.environment) payload.environment = runForm.value.environment
    if (runForm.value.override_host) payload.override_host = runForm.value.override_host
    if (runForm.value.concurrency) payload.concurrency = runForm.value.concurrency
    if (runForm.value.perf_threshold_ms) payload.perf_threshold_ms = runForm.value.perf_threshold_ms
    await suiteApi.run(activeSuite.value.id, payload)
    message.success('套件已开始执行')
    await loadRuns(activeSuite.value.id)
  } catch (e: any) {
    message.error(e.response?.data?.detail || '执行失败')
  } finally {
    running.value = false
  }
}

async function addCase(caseId: string | null) {
  if (!caseId || !activeSuite.value) return
  const existing = activeSuite.value.case_ids || []
  if (existing.includes(caseId)) { message.warning('用例已在套件中'); addCaseId.value = null; return }
  const newIds = [...existing, caseId]
  const res = await suiteApi.update(activeSuite.value.id, { case_ids: newIds })
  activeSuite.value = res.data
  const idx = suites.value.findIndex(s => s.id === activeSuite.value!.id)
  if (idx >= 0) suites.value[idx] = res.data
  addCaseId.value = null
  message.success('已添加')
}

async function removeCase(caseId: string) {
  if (!activeSuite.value) return
  const newIds = (activeSuite.value.case_ids || []).filter(id => id !== caseId)
  const res = await suiteApi.update(activeSuite.value.id, { case_ids: newIds })
  activeSuite.value = res.data
  const idx = suites.value.findIndex(s => s.id === activeSuite.value!.id)
  if (idx >= 0) suites.value[idx] = res.data
}

onMounted(async () => {
  const [appsRes, casesRes] = await Promise.all([
    applicationApi.list(),
    testCaseApi.listAll(),
  ])
  appOptions.value = appsRes.data.map(a => ({ label: a.name, value: a.id }))
  caseOptions.value = casesRes.map(c => ({ label: c.name, value: c.id }))
  caseMap.value = Object.fromEntries(casesRes.map(c => [c.id, c.name]))
  await loadSuites()
})
</script>
