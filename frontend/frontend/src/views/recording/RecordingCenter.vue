<template>
  <n-card title="录制会话">
    <template #header-extra>
      <n-button v-if="fromAppId" size="small" @click="router.push(`/applications/${fromAppId}`)">← 返回应用详情</n-button>
    </template>
    <n-space vertical :size="12">
      <n-card title="会话列表" size="small">
        <template #header-extra>
          <n-space align="center" wrap>
            <n-input
              v-model:value="sessionKeyword"
              placeholder="搜索会话名称"
              clearable
              style="width: 180px"
              @keyup.enter="onSessionFilterChange"
              @clear="onSessionFilterChange"
            />
            <n-select
              v-model:value="filterAppId"
              :options="appOptions"
              placeholder="选择应用"
              clearable
              style="width: 180px"
              @update:value="onAppChange"
            />
            <n-select
              v-model:value="sessionStatus"
              :options="sessionStatusOptions"
              placeholder="会话状态"
              clearable
              style="width: 130px"
              @update:value="onSessionFilterChange"
            />
            <n-date-picker
              v-model:value="sessionStartedRange"
              type="datetimerange"
              clearable
              :shortcuts="dateShortcuts"
              style="width: 320px"
              start-placeholder="会话开始时间"
              end-placeholder="会话结束时间"
              @update:value="onSessionFilterChange"
              @clear="onSessionFilterChange"
            />
            <n-button @click="onSessionFilterChange">搜索</n-button>
            <n-button @click="clearSessionFilters">清空筛选</n-button>
            <n-button @click="showHarModal = true">导入 HAR</n-button>
            <n-button
              :disabled="selectedSessionIds.length === 0"
              :loading="batchDeletingSessions"
              @click="deleteSelectedSessions"
            >
              批量删除
            </n-button>
            <n-button
              type="error"
              ghost
              :disabled="sessionRows.length === 0"
              :loading="batchDeletingSessions"
              @click="deleteAllSessions"
            >
              全部删除
            </n-button>
          </n-space>
        </template>
        <n-data-table
          remote
          :columns="sessionColumns"
          :data="sessionRows"
          :loading="sessionsLoading"
          :row-key="(r: any) => r.id"
          :checked-row-keys="selectedSessionIds"
          @update:checked-row-keys="selectedSessionIds = $event as string[]"
          @update:sorter="onSessionSorterChange"
        />
        <n-space justify="space-between" align="center" style="margin-top:12px">
          <span style="font-size:13px;color:#666">共 {{ sessionPagination.itemCount }} 个会话</span>
          <n-pagination
            v-model:page="sessionPagination.page"
            v-model:page-size="sessionPagination.pageSize"
            :page-sizes="sessionPagination.pageSizes"
            :item-count="sessionPagination.itemCount"
            show-size-picker
            :show-quick-jumper="true"
            :disabled="sessionsLoading"
            @update:page="loadSessionsPage"
            @update:page-size="(size) => { sessionPagination.pageSize = size; sessionPagination.page = 1; loadSessionsPage() }"
          />
        </n-space>
      </n-card>

      <div ref="interfacesSectionRef">
      <n-card :title="activeSessionTitle" size="small">
        <template #header-extra>
          <n-space align="center" wrap>
            <n-tag v-if="activeSession" size="small" type="success">
              当前会话: {{ activeSession.name || activeSession.id.slice(0, 8) }}
            </n-tag>
            <n-select
              v-model:value="filterSessionId"
              :options="sessionOptions"
              placeholder="选择会话"
              clearable
              style="width: 240px"
              @update:value="load"
            />
            <n-button v-if="filterSessionId" quaternary @click="router.push(`/recording/sessions/${filterSessionId}`)">
              会话详情
            </n-button>
          </n-space>
        </template>
        <n-space v-if="!filterSessionId" vertical :size="8">
          <span style="color:#666;font-size:13px">
            先在上面的会话列表里选择一个录制会话，再查看该会话下录到的接口。
          </span>
        </n-space>
        <n-space v-else vertical :size="12">
      <n-space align="center" wrap>
        <n-input
          v-model:value="filterPathKeyword"
          placeholder="接口路径 / 交易码"
          clearable
          style="width: 200px"
          @keyup.enter="load"
          @clear="load"
        />
        <n-select
          v-model:value="filterType"
          :options="typeOptions"
          placeholder="入口类型"
          clearable
          style="width: 130px"
          @update:value="load"
        />
        <n-date-picker
          v-model:value="filterDateRange"
          type="datetimerange"
          clearable
          :shortcuts="dateShortcuts"
          style="width: 340px"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          @update:value="load"
          @clear="load"
        />
        <n-select
          v-model:value="filterQuality"
          :options="qualityOptions"
          placeholder="响应质量"
          clearable
          style="width: 130px"
          @update:value="applyQualityFilter"
        />
        <n-select
          v-model:value="filterRecordStatus"
          :options="recordStatusOptions"
          placeholder="录制状态"
          clearable
          style="width: 130px"
          @update:value="load"
        />
        <n-button @click="load">搜索</n-button>
        <n-button
          size="small"
          :type="failedSelected ? 'warning' : 'default'"
          :secondary="!failedSelected"
          @click="toggleFailedRows"
          :disabled="filteredRecordings.length === 0"
        >{{ failedSelected ? '撤销选中' : '选中失败项' }}</n-button>
        <n-button size="small" @click="clearRecordingFilters">清空筛选</n-button>
      </n-space>

      <n-data-table
        remote
        :columns="columns"
        :data="filteredRecordings"
        :loading="loading"
        :row-key="(r: any) => r.id"
        :checked-row-keys="selectedIds"
        :scroll-x="1050"
        @update:checked-row-keys="selectedIds = $event as string[]"
        @update:sorter="onRecordingSorterChange"
      />

      <n-space justify="end" style="margin-top:12px">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="pagination.pageSizes"
          :item-count="pagination.itemCount"
          show-size-picker
          :show-quick-jumper="true"
          :disabled="loading"
          @update:page="loadPage"
          @update:page-size="(size) => { pagination.pageSize = size; pagination.page = 1; loadPage() }"
        >
          <template #prefix>
            <span style="font-size:13px;color:#666">共 {{ pagination.itemCount }} 条</span>
          </template>
        </n-pagination>
      </n-space>

      <n-space v-if="selectedIds.length > 0" align="center">
        <span>已选 {{ selectedIds.length }} 条</span>
        <n-button size="small" type="primary" @click="showAddToCase = true">加入测试用例</n-button>
        <n-button size="small" @click="showTagModal = true">批量打标签</n-button>
        <n-button size="small" type="error" :loading="batchDeleting" @click="deleteSelected">批量删除</n-button>
      </n-space>
        </n-space>
      </n-card>
      </div>
    </n-space>
  </n-card>

  <!-- HAR 导入弹窗 -->
  <n-modal v-model:show="showHarModal" preset="dialog" title="导入 HAR 文件">
    <n-space vertical>
      <span style="color:#666;font-size:13px">选择应用和 .har 文件，将自动创建录制会话并导入 HTTP 请求条目</span>
      <n-select
        v-model:value="harAppId"
        :options="appOptions"
        placeholder="选择目标应用（必选）"
        style="width:100%"
      />
      <n-upload
        :key="harUploadKey"
        :max="1"
        accept=".har"
        :default-upload="false"
        @change="onHarFileChange"
      >
        <n-button>选择 .har 文件</n-button>
      </n-upload>
      <span v-if="harFileName" style="color:#18a058;font-size:13px">已选: {{ harFileName }}</span>
    </n-space>
    <template #action>
      <n-button @click="showHarModal = false">取消</n-button>
      <n-button type="primary" :loading="harImporting" :disabled="!harAppId || !harFile" @click="importHar">导入</n-button>
    </template>
  </n-modal>

  <!-- 加入测试用例弹窗 -->
  <n-modal v-model:show="showAddToCase" preset="dialog" title="加入测试用例">
    <n-select
      v-model:value="targetCaseId"
      :options="caseOptions"
      placeholder="选择测试用例"
      filterable
    />
    <template #action>
      <n-button @click="showAddToCase = false">取消</n-button>
      <n-button type="primary" @click="addToCase">确认</n-button>
    </template>
  </n-modal>

  <!-- 批量打标签弹窗 -->
  <n-modal v-model:show="showTagModal" preset="dialog" title="批量设置标签">
    <n-space vertical>
      <span style="color:#666;font-size:13px">将以下标签设置给选中的 {{ selectedIds.length }} 条录制（会覆盖已有标签）</span>
      <n-dynamic-tags v-model:value="batchTags" />
    </n-space>
    <template #action>
      <n-button @click="showTagModal = false">取消</n-button>
      <n-button type="primary" :loading="tagging" @click="applyBatchTags">确认</n-button>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onActivated, h, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NCard, NSpace, NSelect, NButton, NDataTable, NTag, NModal, NInput,
  NIcon, NDynamicTags, NUpload, NPagination, NDatePicker, useMessage, useDialog,
} from 'naive-ui'
import { recordingApi, sessionApi, type Recording, type Session } from '@/api/recordings'
import { fmtTime } from '@/utils/time'
import { applicationApi } from '@/api/applications'
import { testCaseApi } from '@/api/testCases'
import { getQueryDateRange, getQueryText, setQueryDateRange, setQueryText } from '@/utils/filterQuery'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const recordings = ref<Recording[]>([])
const loading = ref(false)
const sessionsLoading = ref(false)
const batchDeleting = ref(false)
const tagging = ref(false)
const batchDeletingSessions = ref(false)
const selectedSessionIds = ref<string[]>([])
const selectedIds = ref<string[]>([])

// 从应用详情跳入时携带 app_id，用于显示返回按钮
const fromAppId = ref<string | null>(route.query.app_id as string || null)
const filterAppId = ref<string | null>(getQueryText(route.query, 'app_id'))
const filterSessionId = ref<string | null>(getQueryText(route.query, 'session_id'))
const sessionKeyword = ref(getQueryText(route.query, 'session_keyword') || '')
const sessionStatus = ref<string | null>(getQueryText(route.query, 'session_status'))
const sessionStartedRange = ref<[number, number] | null>(getQueryDateRange(route.query, 'session_started_from', 'session_started_to'))
const filterType = ref<string | null>(getQueryText(route.query, 'entry_type'))
const filterDateRange = ref<[number, number] | null>(getQueryDateRange(route.query, 'created_from', 'created_to'))
const filterQuality = ref<string | null>(getQueryText(route.query, 'quality'))
const filterPathKeyword = ref(getQueryText(route.query, 'path_keyword') || '')
const filterRecordStatus = ref<string | null>(getQueryText(route.query, 'record_status'))

const now = Date.now()
const dateShortcuts = {
  '今天': () => [new Date().setHours(0, 0, 0, 0), now] as [number, number],
  '最近3天': () => [now - 3 * 86400000, now] as [number, number],
  '最近7天': () => [now - 7 * 86400000, now] as [number, number],
  '最近30天': () => [now - 30 * 86400000, now] as [number, number],
}

const appOptions = ref<{ label: string; value: string }[]>([])
const allSessions = ref<Session[]>([])
const sessionOptions = ref<{ label: string; value: string }[]>([])
const caseOptions = ref<{ label: string; value: string }[]>([])
const showAddToCase = ref(false)
const showTagModal = ref(false)
const batchTags = ref<string[]>([])
const targetCaseId = ref<string | null>(null)

// HAR import state
const showHarModal = ref(false)
const harAppId = ref<string | null>(null)
const harFile = ref<File | null>(null)
const harFileName = ref('')
const harImporting = ref(false)
const harUploadKey = ref(0)

watch(showHarModal, (val) => {
  if (val) {
    harAppId.value = null
    harFile.value = null
    harFileName.value = ''
    harUploadKey.value++  // 强制 NUpload 重新挂载，清空内部文件列表
  }
})

function onHarFileChange({ file }: any) {
  harFile.value = file.file ?? null
  harFileName.value = file.name
}

async function importHar() {
  if (!harAppId.value || !harFile.value) return
  harImporting.value = true
  try {
    const fd = new FormData()
    fd.append('app_id', harAppId.value)
    fd.append('file', harFile.value)
    const res = await recordingApi.importHar(fd)
    message.success(`已导入 ${res.data.imported} 条录制`)
    showHarModal.value = false
    harFile.value = null
    harFileName.value = ''
    harAppId.value = null
    await init()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '导入失败')
  } finally {
    harImporting.value = false
  }
}

const pagination = reactive({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [20, 50, 100],
  itemCount: 0,
  onChange: (page: number) => { pagination.page = page; loadPage() },
  onUpdatePageSize: (pageSize: number) => { pagination.pageSize = pageSize; pagination.page = 1; loadPage() },
})

const sessionPagination = reactive({
  page: 1,
  pageSize: 10,
  pageSizes: [10, 20, 50],
  itemCount: 0,
})

const sessionSortState = ref<{ columnKey: string; order: 'ascend' | 'descend' }>({
  columnKey: 'started_at',
  order: 'descend',
})

const recordingSortState = ref<{ columnKey: string; order: 'ascend' | 'descend' }>({
  columnKey: 'created_at',
  order: 'descend',
})

const interfacesSectionRef = ref<HTMLElement | null>(null)
const activeSessionSnapshot = ref<Session | null>(null)

const sessionStatusColor: Record<string, any> = {
  ACTIVE: 'success',
  COLLECTING: 'warning',
  DONE: 'info',
  ERROR: 'error',
}

const sessionStatusLabel: Record<string, string> = {
  ACTIVE: '录制中',
  COLLECTING: '采集中',
  DONE: '已完成',
  ERROR: '错误',
}

const sessionRows = computed(() => allSessions.value)

const activeSession = computed(() =>
  allSessions.value.find(s => s.id === filterSessionId.value) || activeSessionSnapshot.value
)

const activeSessionTitle = computed(() =>
  activeSession.value
    ? `会话接口 - ${activeSession.value.name || activeSession.value.id.slice(0, 8)}`
    : '会话接口'
)

const sessionColumns = computed(() => [
  { type: 'selection' as const, width: 40 },
  {
    title: '名称',
    key: 'name',
    render: (r: Session) => r.name || r.id.slice(0, 8),
  },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render: (r: Session) =>
      h(NTag, { size: 'small', type: sessionStatusColor[r.status] || 'default' }, () => sessionStatusLabel[r.status] || r.status),
  },
  { title: '录制数', key: 'record_count', width: 80 },
  {
    title: '开始时间',
    key: 'started_at',
    width: 170,
    sorter: true,
    sortOrder: sessionSortState.value.columnKey === 'started_at' ? sessionSortState.value.order : false,
    render: (r: Session) => fmtTime(r.started_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 290,
    render: (r: Session) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, {
          size: 'small',
          secondary: true,
          onClick: () => openSession(r),
        }, () => '查看接口'),
        filterSessionId.value === r.id
          ? h(NTag, { size: 'small', type: 'success', bordered: false }, () => '当前查看')
          : null,
        h(NButton, {
          size: 'small',
          onClick: () => router.push(`/recording/sessions/${r.id}`),
        }, () => '会话详情'),
        h(NButton, {
          size: 'small',
          type: 'error',
          secondary: true,
          disabled: r.status === 'ACTIVE',
          onClick: () => deleteSession(r),
        }, () => '删除'),
      ]),
  },
])

function onAppChange(appId: string | null) {
  filterSessionId.value = null
  activeSessionSnapshot.value = null
  onSessionFilterChange()
  load()
}

async function openSession(session: Session) {
  activeSessionSnapshot.value = session
  filterSessionId.value = session.id
  await load()
  await nextTick()
  interfacesSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function clearRecordingFilters() {
  filterType.value = null
  filterDateRange.value = null
  filterQuality.value = null
  filterPathKeyword.value = ''
  filterRecordStatus.value = null
  load()
}

function onSessionFilterChange() {
  sessionPagination.page = 1
  selectedSessionIds.value = []
  loadSessionsPage()
}

function onSessionSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (!sorter || sorter.order === false) {
    sessionSortState.value = { columnKey: 'started_at', order: 'descend' }
  } else {
    sessionSortState.value = { columnKey: sorter.columnKey, order: sorter.order }
  }
  sessionPagination.page = 1
  loadSessionsPage()
}

function onRecordingSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (!sorter || sorter.order === false) {
    recordingSortState.value = { columnKey: 'created_at', order: 'descend' }
  } else {
    recordingSortState.value = { columnKey: sorter.columnKey, order: sorter.order }
  }
  pagination.page = 1
  loadPage()
}

function clearSessionFilters() {
  filterAppId.value = null
  filterSessionId.value = null
  sessionKeyword.value = ''
  sessionStatus.value = null
  sessionStartedRange.value = null
  activeSessionSnapshot.value = null
  onSessionFilterChange()
  load()
}

watch(showAddToCase, async (val) => {
  if (val) {
    const res = await testCaseApi.list({ app_id: filterAppId.value || undefined, limit: 500 })
    caseOptions.value = res.data.items.map(c => ({ label: c.name, value: c.id }))
    targetCaseId.value = null
  }
})

const typeOptions = [
  { label: 'HTTP', value: 'HTTP' },
  { label: 'DUBBO', value: 'DUBBO' },
  { label: 'MYBATIS', value: 'MYBATIS' },
  { label: 'JAVA', value: 'JAVA' },
]

const sessionStatusOptions = [
  { label: '录制中', value: 'ACTIVE' },
  { label: '采集中', value: 'COLLECTING' },
  { label: '已完成', value: 'DONE' },
  { label: '错误', value: 'ERROR' },
]

const qualityOptions = [
  { label: '✅ 成功 (2xx)', value: '2xx' },
  { label: '❌ 失败 (4xx)', value: '4xx' },
  { label: '❌ 服务错误 (5xx)', value: '5xx' },
  { label: '⚠️ 空响应', value: 'empty' },
  { label: '❓ 未知', value: 'unknown' },
]

const recordStatusOptions = [
  { label: '原始', value: 'RAW' },
  { label: '已解析', value: 'PARSED' },
  { label: '已加入用例', value: 'ADDED_TO_CASE' },
  { label: '通过', value: 'PASS' },
  { label: '失败', value: 'FAIL' },
  { label: '错误', value: 'ERROR' },
]

/**
 * Detect response quality from response_body.
 * Checks for: JSON {"status": NNN, ...} or XML <code>NNN</code> / <status>NNN</status>
 */
function getResponseQuality(r: Recording): '2xx' | '4xx' | '5xx' | 'empty' | 'unknown' {
  const body = r.response_body
  if (!body || !body.trim()) return 'empty'

  // Try JSON
  try {
    const obj = JSON.parse(body)
    const code = obj.status ?? obj.code ?? obj.statusCode ?? obj.httpStatus
    if (typeof code === 'number') {
      if (code >= 200 && code < 300) return '2xx'
      if (code >= 400 && code < 500) return '4xx'
      if (code >= 500) return '5xx'
    }
    if (typeof code === 'string') {
      const n = parseInt(code)
      if (!isNaN(n)) {
        if (n >= 200 && n < 300) return '2xx'
        if (n >= 400 && n < 500) return '4xx'
        if (n >= 500) return '5xx'
      }
    }
    // Has JSON content but no recognizable status code → treat as 2xx (success body)
    return '2xx'
  } catch {}

  // Try XML: look for <code>NNN</code> or <status>NNN</status> or <httpStatus>NNN</httpStatus>
  const xmlMatch = body.match(/<(?:code|status|httpStatus|errorCode)>(\d{3})<\//)
  if (xmlMatch) {
    const n = parseInt(xmlMatch[1])
    if (n >= 200 && n < 300) return '2xx'
    if (n >= 400 && n < 500) return '4xx'
    if (n >= 500) return '5xx'
  }

  // Has XML/text content but no recognizable status → treat as 2xx
  if (body.trim().startsWith('<') || body.trim().length > 10) return '2xx'
  return 'unknown'
}

const qualityColorMap: Record<string, 'success' | 'error' | 'warning' | 'default'> = {
  '2xx': 'success',
  '4xx': 'error',
  '5xx': 'error',
  'empty': 'warning',
  'unknown': 'default',
}

const qualityLabelMap: Record<string, string> = {
  '2xx': '成功',
  '4xx': '失败4xx',
  '5xx': '服务错误',
  'empty': '空响应',
  'unknown': '未知',
}

const filteredRecordings = computed(() => {
  if (!filterQuality.value) return recordings.value
  return recordings.value.filter(r => getResponseQuality(r) === filterQuality.value)
})

function applyQualityFilter() {
  selectedIds.value = []
}

const failedIds = computed(() =>
  filteredRecordings.value
    .filter(r => { const q = getResponseQuality(r); return q === '4xx' || q === '5xx' || q === 'empty' })
    .map(r => r.id)
)

const failedSelected = computed(() =>
  failedIds.value.length > 0 &&
  failedIds.value.every(id => selectedIds.value.includes(id))
)

function toggleFailedRows() {
  if (failedIds.value.length === 0) {
    message.info('当前页没有失败的录制')
    return
  }
  if (failedSelected.value) {
    // 撤销：移除所有失败项的选中
    selectedIds.value = selectedIds.value.filter(id => !failedIds.value.includes(id))
  } else {
    // 选中：合并已选 + 失败项（去重）
    const merged = new Set([...selectedIds.value, ...failedIds.value])
    selectedIds.value = [...merged]
    message.info(`已选中 ${failedIds.value.length} 条失败/空响应的录制`)
  }
}

const statusColor: Record<string, any> = {
  PASS: 'success', FAIL: 'error', ERROR: 'error', PARSED: 'info', RAW: 'default', ADDED_TO_CASE: 'success',
}

const statusLabel: Record<string, string> = {
  PASS: '通过', FAIL: '失败', ERROR: '错误', PARSED: '已解析', RAW: '原始', ADDED_TO_CASE: '已加入用例',
}

const columns = computed(() => [
  { type: 'selection' as const, width: 40 },
  {
    title: '入口类型', key: 'entry_type', width: 85,
    render: (r: Recording) => h(NTag, { size: 'small', type: 'info' }, () => r.entry_type || '-'),
  },
  { title: 'Host', key: 'host', width: 150, ellipsis: { tooltip: true } },
  { title: '路径', key: 'path', width: 200, ellipsis: { tooltip: true } },
  {
    title: '响应质量', key: 'resp_quality', width: 90,
    render: (r: Recording) => {
      const q = getResponseQuality(r)
      return h(NTag, { size: 'small', type: qualityColorMap[q] }, () => qualityLabelMap[q])
    },
  },
  {
    title: '标签', key: 'tags', width: 130,
    render: (r: Recording) =>
      r.tags?.length
        ? h(NSpace, { size: 4 }, () => r.tags!.map(t => h(NTag, { size: 'small', type: 'warning' }, () => t)))
        : '-',
  },
  {
    title: '耗时(ms)',
    key: 'duration_ms',
    width: 80,
    sorter: true,
    sortOrder: recordingSortState.value.columnKey === 'duration_ms' ? recordingSortState.value.order : false,
  },
  {
    title: '状态', key: 'status', width: 90,
    render: (r: Recording) =>
      h(NTag, { size: 'small', type: statusColor[r.status] || 'default' }, () => statusLabel[r.status] || r.status),
  },
  {
    title: '时间',
    key: 'created_at',
    width: 155,
    sorter: true,
    sortOrder: recordingSortState.value.columnKey === 'created_at' ? recordingSortState.value.order : false,
    render: (r: Recording) => fmtTime(r.created_at),
  },
  {
    title: '操作', key: 'actions', width: 110,
    render: (r: Recording) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, { size: 'small', onClick: () => router.push(`/recordings/${r.id}`) }, () => '查看'),
        h(NButton, { size: 'small', type: 'error', onClick: () => deleteSingle(r.id) }, () => '删除'),
      ]),
  },
])

// 筛选条件变化时重置到第 1 页
async function load() {
  pagination.page = 1
  selectedIds.value = []
  await loadPage()
}

// 翻页/改页大小时调用，不重置页码
async function loadPage() {
  if (!filterSessionId.value) {
    recordings.value = []
    pagination.itemCount = 0
    loading.value = false
    return
  }
  loading.value = true
  selectedIds.value = []
  try {
    const res = await recordingApi.list({
      app_id: filterAppId.value || undefined,
      session_id: filterSessionId.value || undefined,
      entry_type: filterType.value || undefined,
      status: filterRecordStatus.value || undefined,
      path_contains: filterPathKeyword.value || undefined,
      created_after: filterDateRange.value ? new Date(filterDateRange.value[0]).toISOString() : undefined,
      created_before: filterDateRange.value ? new Date(filterDateRange.value[1]).toISOString() : undefined,
      limit: pagination.pageSize,
      offset: (pagination.page - 1) * pagination.pageSize,
      sort_by: recordingSortState.value.columnKey,
      sort_order: recordingSortState.value.order === 'ascend' ? 'asc' : 'desc',
    })
    recordings.value = res.data.items
    pagination.itemCount = res.data.total
  } finally {
    loading.value = false
  }
}

async function deleteSingle(id: string) {
  dialog.warning({
    title: '确认删除', content: '删除后不可恢复，确认吗？',
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      await recordingApi.delete(id)
      message.success('已删除')
      selectedIds.value = selectedIds.value.filter(i => i !== id)
      await loadPage()
    },
  })
}

async function deleteSelected() {
  dialog.warning({
    title: '确认批量删除',
    content: `将删除选中的 ${selectedIds.value.length} 条录制，确认吗？`,
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      batchDeleting.value = true
      try {
        const count = selectedIds.value.length
        await recordingApi.batchDelete(selectedIds.value)
        message.success(`已删除 ${count} 条`)
        selectedIds.value = []
        await loadPage()
      } finally {
        batchDeleting.value = false
      }
    },
  })
}

async function applyBatchTags() {
  tagging.value = true
  try {
    for (const id of selectedIds.value) {
      await recordingApi.updateTags(id, batchTags.value)
    }
    message.success(`已为 ${selectedIds.value.length} 条录制设置标签`)
    showTagModal.value = false
    await load()
  } finally {
    tagging.value = false
  }
}

async function addToCase() {
  if (!targetCaseId.value) { message.warning('请选择测试用例'); return }
  const res = await testCaseApi.addRecordings(targetCaseId.value, selectedIds.value)
  message.success(`已添加 ${res.data.added} 条录制到用例`)
  showAddToCase.value = false
  selectedIds.value = []
}

function clearDeletedSessions(deletedIds: string[]) {
  const deleted = new Set(deletedIds)
  allSessions.value = allSessions.value.filter(s => !deleted.has(s.id))
  selectedSessionIds.value = selectedSessionIds.value.filter(id => !deleted.has(id))
  sessionOptions.value = sessionOptions.value.filter(opt => !deleted.has(opt.value))
  sessionPagination.itemCount = Math.max(0, sessionPagination.itemCount - deletedIds.length)
  if (filterSessionId.value && deleted.has(filterSessionId.value)) {
    filterSessionId.value = null
    activeSessionSnapshot.value = null
    recordings.value = []
    pagination.itemCount = 0
    selectedIds.value = []
  }
}

async function deleteSession(session: Session) {
  if (session.status === 'ACTIVE') {
    message.warning('请先停止录制再删除')
    return
  }
  dialog.warning({
    title: '确认删除',
    content: `将删除会话“${session.name || session.id.slice(0, 8)}”及其全部录制数据，确认吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      await sessionApi.delete(session.id)
      clearDeletedSessions([session.id])
      await loadSessionsPage()
      message.success('会话已删除')
    },
  })
}

async function deleteSelectedSessions() {
  if (selectedSessionIds.value.length === 0) return
  const active = sessionRows.value.filter(s => selectedSessionIds.value.includes(s.id) && s.status === 'ACTIVE')
  if (active.length) {
    message.warning('选中的会话中有正在录制的会话，请先停止录制再删除')
    return
  }
  dialog.warning({
    title: '确认批量删除',
    content: `将删除选中的 ${selectedSessionIds.value.length} 个录制会话及其全部录制数据，确认吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      batchDeletingSessions.value = true
      try {
        const ids = [...selectedSessionIds.value]
        await sessionApi.batchDelete(ids)
        clearDeletedSessions(ids)
        await loadSessionsPage()
        message.success(`已删除 ${ids.length} 个会话`)
      } finally {
        batchDeletingSessions.value = false
      }
    },
  })
}

async function deleteAllSessions() {
  if (sessionRows.value.length === 0) return
  const active = sessionRows.value.filter(s => s.status === 'ACTIVE')
  if (active.length) {
    message.warning('当前列表中有正在录制的会话，请先停止录制再删除')
    return
  }
  dialog.warning({
    title: '确认全部删除',
    content: `将删除当前列表中的 ${sessionRows.value.length} 个录制会话及其全部录制数据，确认吗？`,
    positiveText: '全部删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      batchDeletingSessions.value = true
      try {
        const ids = sessionRows.value.map(s => s.id)
        await sessionApi.batchDelete(ids)
        clearDeletedSessions(ids)
        await loadSessionsPage()
        message.success(`已删除当前列表中的 ${ids.length} 个会话`)
      } finally {
        batchDeletingSessions.value = false
      }
    },
  })
}

async function loadSessionsPage() {
  sessionsLoading.value = true
  try {
    const sessionsRes = await sessionApi.search({
      app_id: filterAppId.value || undefined,
      name: sessionKeyword.value || undefined,
      status: sessionStatus.value || undefined,
      started_after: sessionStartedRange.value ? new Date(sessionStartedRange.value[0]).toISOString() : undefined,
      started_before: sessionStartedRange.value ? new Date(sessionStartedRange.value[1]).toISOString() : undefined,
      limit: sessionPagination.pageSize,
      offset: (sessionPagination.page - 1) * sessionPagination.pageSize,
      sort_by: sessionSortState.value.columnKey,
      sort_order: sessionSortState.value.order === 'ascend' ? 'asc' : 'desc',
    })
    allSessions.value = sessionsRes.data.items
    sessionPagination.itemCount = sessionsRes.data.total

    if (filterSessionId.value) {
      const s = sessionsRes.data.items.find(s => s.id === filterSessionId.value)
      if (s) {
        filterAppId.value = s.app_id
        activeSessionSnapshot.value = s
      } else if (!activeSessionSnapshot.value || activeSessionSnapshot.value.id !== filterSessionId.value) {
        try {
          const detail = await sessionApi.get(filterSessionId.value)
          activeSessionSnapshot.value = detail.data
        } catch {
          activeSessionSnapshot.value = null
        }
      }
    }

    const optionSource = [...sessionsRes.data.items]
    if (activeSessionSnapshot.value && !optionSource.some(s => s.id === activeSessionSnapshot.value!.id)) {
      optionSource.unshift(activeSessionSnapshot.value)
    }
    sessionOptions.value = optionSource.map(s => ({ label: `${s.name || s.id.slice(0, 8)} (${s.status})`, value: s.id }))
  } finally {
    sessionsLoading.value = false
  }
}

async function init() {
  const appsRes = await applicationApi.list()
  appOptions.value = appsRes.data.map(a => ({ label: a.name, value: a.id }))

  await loadSessionsPage()
  await loadPage()
}

onMounted(init)
onActivated(init)

watch([
  filterAppId,
  filterSessionId,
  sessionKeyword,
  sessionStatus,
  sessionStartedRange,
  filterType,
  filterDateRange,
  filterQuality,
  filterPathKeyword,
  filterRecordStatus,
], () => {
  const query: Record<string, string> = {}
  setQueryText(query, 'app_id', filterAppId.value)
  setQueryText(query, 'session_id', filterSessionId.value)
  setQueryText(query, 'session_keyword', sessionKeyword.value.trim() || null)
  setQueryText(query, 'session_status', sessionStatus.value)
  setQueryDateRange(query, sessionStartedRange.value, 'session_started_from', 'session_started_to')
  setQueryText(query, 'entry_type', filterType.value)
  setQueryText(query, 'quality', filterQuality.value)
  setQueryText(query, 'path_keyword', filterPathKeyword.value.trim() || null)
  setQueryText(query, 'record_status', filterRecordStatus.value)
  setQueryDateRange(query, filterDateRange.value, 'created_from', 'created_to')
  router.replace({ query })
})
</script>
