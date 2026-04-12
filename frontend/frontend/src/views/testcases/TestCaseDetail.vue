<template>
  <n-card v-if="testCase" :title="testCase.name">
    <template #header-extra>
      <n-space>
        <n-button size="small" @click="showAddModal = true">+ 添加录制</n-button>
        <n-button type="primary" size="small" @click="router.push(`/replay?case_id=${testCase.id}`)">
          发起回放
        </n-button>
        <n-popconfirm @positive-click="handleDeleteCase">
          <template #trigger>
            <n-button size="small" type="error">删除用例</n-button>
          </template>
          确认删除该用例？
        </n-popconfirm>
      </n-space>
    </template>

    <n-descriptions bordered :column="3" size="small">
      <n-descriptions-item label="状态">{{ { ACTIVE: '启用中', DELETED: '已删除' }[testCase.status] || testCase.status }}</n-descriptions-item>
      <n-descriptions-item label="录制数">{{ recordings.length }}</n-descriptions-item>
      <n-descriptions-item label="标签">
        <n-space>
          <n-tag v-for="t in testCase.tags" :key="t" size="small">{{ t }}</n-tag>
          <span v-if="!testCase.tags?.length">-</span>
        </n-space>
      </n-descriptions-item>
      <n-descriptions-item label="描述" :span="3">{{ testCase.description || '-' }}</n-descriptions-item>
    </n-descriptions>

    <n-divider>关联录制（{{ recordings.length }} 条）</n-divider>
    <n-space v-if="selectedRecordingIds.length > 0" align="center" style="margin-bottom:8px">
      <span style="font-size:13px;color:#666">已选 {{ selectedRecordingIds.length }} 条</span>
      <n-popconfirm @positive-click="batchRemove">
        <template #trigger>
          <n-button size="small" type="error" :loading="batchRemoving">批量移除</n-button>
        </template>
        确认从用例中移除选中的 {{ selectedRecordingIds.length }} 条录制？
      </n-popconfirm>
      <n-button size="small" @click="selectedRecordingIds = []">取消选择</n-button>
    </n-space>
    <n-data-table
      :columns="columns"
      :data="recordings"
      :loading="loading"
      size="small"
      :pagination="recordingsPagination"
      :row-key="(r: any) => r.id"
      :checked-row-keys="selectedRecordingIds"
      @update:checked-row-keys="selectedRecordingIds = $event as string[]"
    />
  </n-card>

  <!-- 编辑请求参数弹窗 -->
  <n-modal v-model:show="showEditRequest" preset="card" title="编辑请求参数" style="width:680px">
    <n-space vertical :size="12">
      <!-- 只读信息行 -->
      <n-space align="center" :size="8">
        <n-tag type="info" size="small">{{ editMeta.method }}</n-tag>
        <span style="font-family:monospace;font-size:13px;color:#333">{{ editMeta.uri }}</span>
      </n-space>

      <!-- Content-Type 编辑 -->
      <n-space align="center" :size="8">
        <span style="font-size:13px;color:#666;white-space:nowrap">Content-Type</span>
        <n-auto-complete
          v-model:value="editContentType"
          :options="contentTypeOptions"
          style="width:320px"
          placeholder="application/xml"
        />
      </n-space>

      <!-- 请求体编辑 -->
      <n-space vertical :size="4">
        <n-space justify="space-between" align="center">
          <span style="font-size:13px;color:#666">请求体内容（留空则不修改）</span>
          <n-space :size="6">
            <n-button size="small" @click="formatBodyAsJson" v-if="isJsonContentType">格式化 JSON</n-button>
            <n-button size="small" @click="editRequestBody = ''">清空</n-button>
          </n-space>
        </n-space>
        <n-input
          v-model:value="editRequestBody"
          type="textarea"
          :rows="14"
          :placeholder="bodyPlaceholder"
          style="font-family:monospace;font-size:13px"
        />
      </n-space>

      <span v-if="editRequestError" style="color:#d03050;font-size:12px">{{ editRequestError }}</span>
    </n-space>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showEditRequest = false">取消</n-button>
        <n-button type="primary" :loading="editRequestSaving" @click="saveEditRequest">保存</n-button>
      </n-space>
    </template>
  </n-modal>

  <!-- 添加录制弹窗 -->
  <n-modal v-model:show="showAddModal" title="选择录制" style="width: 960px" preset="card">
    <n-space vertical>
      <n-space align="center" wrap>
        <n-select
          v-model:value="pickAppId"
          :options="appOptions"
          placeholder="按应用筛选"
          clearable
          style="width: 150px"
          @update:value="onPickAppChange"
        />
        <n-select
          v-model:value="pickSessionId"
          :options="pickSessionOptions"
          placeholder="按会话筛选"
          clearable
          style="width: 190px"
        />
        <n-input v-model:value="pickFilter" placeholder="按路径关键字筛选" clearable style="width: 160px" />
        <n-select
          v-model:value="pickQuality"
          :options="pickQualityOptions"
          placeholder="响应质量"
          clearable
          style="width: 120px"
        />
        <n-date-picker
          v-model:value="pickDateRange"
          type="datetimerange"
          clearable
          :shortcuts="dateShortcuts"
          style="width: 340px"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
        />
      </n-space>
      <n-space align="center">
        <span style="color:#999;font-size:12px">共 {{ filteredPickList.length }} 条</span>
        <n-button type="primary" :disabled="pickedIds.length === 0" :loading="adding" @click="handleAdd">
          添加所选 ({{ pickedIds.length }})
        </n-button>
      </n-space>
      <n-data-table
        :columns="pickColumns"
        :data="filteredPickList"
        :loading="pickLoading"
        :row-key="(r: Recording) => r.id"
        v-model:checked-row-keys="pickedIds"
        size="small"
        max-height="400"
      />
    </n-space>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NCard, NDescriptions, NDescriptionsItem, NDivider, NDataTable,
  NButton, NSpace, NTag, NPopconfirm, NModal, NInput, NSelect, NAutoComplete, NDatePicker, useMessage,
} from 'naive-ui'
import { testCaseApi, type TestCase } from '@/api/testCases'
import { recordingApi, sessionApi, type Recording, type Session } from '@/api/recordings'
import { applicationApi } from '@/api/applications'
import { fmtTime } from '@/utils/time'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const caseId = route.params.id as string

const testCase = ref<TestCase | null>(null)
const recordings = ref<Recording[]>([])
const loading = ref(false)
const selectedRecordingIds = ref<string[]>([])
const batchRemoving = ref(false)

const recordingsPagination = reactive({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [20, 50, 100],
  onChange: (page: number) => { recordingsPagination.page = page },
  onUpdatePageSize: (size: number) => { recordingsPagination.pageSize = size; recordingsPagination.page = 1 },
})

// Request edit state
const showEditRequest = ref(false)
const editingRecordingId = ref<string | null>(null)
const editingEnvelope = ref<Record<string, any>>({})  // 完整的 request_body 对象
const editMeta = ref({ method: 'GET', uri: '' })
const editContentType = ref('')
const editRequestBody = ref('')
const editRequestError = ref('')
const editRequestSaving = ref(false)

const contentTypeOptions = [
  'application/xml',
  'application/json',
  'text/xml',
  'application/x-www-form-urlencoded',
  'multipart/form-data',
  'text/plain',
].map(v => ({ label: v, value: v }))

const isJsonContentType = computed(() =>
  editContentType.value.includes('json')
)

const bodyPlaceholder = computed(() => {
  const ct = editContentType.value
  if (ct.includes('xml')) return '<Root>\n  <field>value</field>\n</Root>'
  if (ct.includes('json')) return '{\n  "key": "value"\n}'
  if (ct.includes('form')) return 'key1=value1&key2=value2'
  return '请求体内容'
})

function formatBodyAsJson() {
  try {
    editRequestBody.value = JSON.stringify(JSON.parse(editRequestBody.value), null, 2)
    editRequestError.value = ''
  } catch {
    editRequestError.value = '不是合法的 JSON，无法格式化'
  }
}

function openEditRequest(r: Recording) {
  editingRecordingId.value = r.id
  editRequestError.value = ''

  // 解析外层 JSON 信封
  let envelope: Record<string, any> = {}
  try {
    envelope = r.request_body ? JSON.parse(r.request_body) : {}
  } catch {
    envelope = {}
  }
  editingEnvelope.value = envelope
  editMeta.value = {
    method: (envelope.method || 'GET').toUpperCase(),
    uri: envelope.uri || r.path || '',
  }
  editContentType.value = envelope.contentType || ''

  // 内层 body 字段
  const innerBody = envelope.body || ''
  // 如果是 JSON 字符串，美化展示
  if (innerBody && (editContentType.value.includes('json') || innerBody.trimStart().startsWith('{'))) {
    try {
      editRequestBody.value = JSON.stringify(JSON.parse(innerBody), null, 2)
    } catch {
      editRequestBody.value = innerBody
    }
  } else {
    editRequestBody.value = innerBody
  }

  showEditRequest.value = true
}

async function saveEditRequest() {
  editRequestError.value = ''
  // 重新构造信封 JSON，只更新 body 和 contentType
  const envelope = {
    ...editingEnvelope.value,
    contentType: editContentType.value || editingEnvelope.value.contentType,
    body: editRequestBody.value,
  }
  const newRb = JSON.stringify(envelope, null, 0)

  editRequestSaving.value = true
  try {
    await recordingApi.updateRequest(editingRecordingId.value!, newRb)
    message.success('请求参数已更新')
    showEditRequest.value = false
    await loadRecordings()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    editRequestSaving.value = false
  }
}

// Add recordings modal state
const showAddModal = ref(false)
const pickLoading = ref(false)
const pickList = ref<Recording[]>([])
const pickedIds = ref<string[]>([])
const pickFilter = ref('')
const pickAppId = ref<string | null>(null)
const pickSessionId = ref<string | null>(null)
const pickQuality = ref<string | null>(null)
const pickDateRange = ref<[number, number] | null>(null)
const adding = ref(false)

const appOptions = ref<{ label: string; value: string }[]>([])
const appMap = ref<Record<string, string>>({})
const allSessions = ref<Session[]>([])
const pickSessionOptions = ref<{ label: string; value: string }[]>([])

const pickQualityOptions = [
  { label: '✅ 成功 (2xx)', value: '2xx' },
  { label: '❌ 失败 (4xx)', value: '4xx' },
  { label: '❌ 服务错误 (5xx)', value: '5xx' },
  { label: '⚠️ 空响应', value: 'empty' },
]

const now = Date.now()
const dateShortcuts = {
  '今天': () => [new Date().setHours(0, 0, 0, 0), now] as [number, number],
  '最近3天': () => [now - 3 * 86400000, now] as [number, number],
  '最近7天': () => [now - 7 * 86400000, now] as [number, number],
  '最近30天': () => [now - 30 * 86400000, now] as [number, number],
}

function onPickAppChange(appId: string | null) {
  pickSessionId.value = null
  if (appId) {
    pickSessionOptions.value = allSessions.value
      .filter(s => s.app_id === appId)
      .map(s => ({ label: `${s.name || s.id.slice(0, 8)} (${s.status})`, value: s.id }))
  } else {
    pickSessionOptions.value = allSessions.value.map(s => ({
      label: `${s.name || s.id.slice(0, 8)} (${s.status})`,
      value: s.id,
    }))
  }
}

function getPickQuality(r: Recording): '2xx' | '4xx' | '5xx' | 'empty' | 'unknown' {
  const body = r.response_body
  if (!body || !body.trim()) return 'empty'
  try {
    const obj = JSON.parse(body)
    const code = obj.status ?? obj.code ?? obj.statusCode ?? obj.httpStatus
    const n = typeof code === 'number' ? code : (typeof code === 'string' ? parseInt(code) : NaN)
    if (!isNaN(n)) {
      if (n >= 200 && n < 300) return '2xx'
      if (n >= 400 && n < 500) return '4xx'
      if (n >= 500) return '5xx'
    }
    return '2xx'
  } catch {}
  const xmlMatch = body.match(/<(?:code|status|httpStatus|errorCode)>(\d{3})<\//)
  if (xmlMatch) {
    const n = parseInt(xmlMatch[1])
    if (n >= 200 && n < 300) return '2xx'
    if (n >= 400 && n < 500) return '4xx'
    if (n >= 500) return '5xx'
  }
  if (body.trim().startsWith('<') || body.trim().length > 10) return '2xx'
  return 'unknown'
}

const pickQualityColorMap: Record<string, 'success' | 'error' | 'warning' | 'default'> = {
  '2xx': 'success', '4xx': 'error', '5xx': 'error', 'empty': 'warning', 'unknown': 'default',
}
const pickQualityLabelMap: Record<string, string> = {
  '2xx': '成功', '4xx': '失败4xx', '5xx': '服务错误', 'empty': '空响应', 'unknown': '未知',
}

const filteredPickList = computed(() => {
  let list = pickList.value
  if (pickAppId.value) list = list.filter(r => r.app_id === pickAppId.value)
  if (pickSessionId.value) list = list.filter(r => r.session_id === pickSessionId.value)
  const f = pickFilter.value.trim().toLowerCase()
  if (f) list = list.filter(r => (r.path || '').toLowerCase().includes(f))
  if (pickQuality.value) list = list.filter(r => getPickQuality(r) === pickQuality.value)
  if (pickDateRange.value) {
    const [start, end] = pickDateRange.value
    list = list.filter(r => {
      const t = r.timestamp || r.created_at
      if (!t) return true
      const ms = new Date(t).getTime()
      return ms >= start && ms <= end
    })
  }
  return list
})

const columns = [
  { type: 'selection' as const, width: 40 },
  { title: '类型', key: 'entry_type', width: 80 },
  { title: '路径', key: 'path', ellipsis: { tooltip: true } },
  { title: '耗时(ms)', key: 'duration_ms', width: 90 },
  {
    title: '录制时间',
    key: 'timestamp',
    width: 160,
    render: (r: Recording) => fmtTime(r.timestamp || r.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (r: Recording) =>
      h(NSpace, {}, () => [
        h(NButton, { size: 'small', onClick: () => router.push(`/recordings/${r.id}`) }, () => '查看'),
        h(NButton, { size: 'small', type: 'info', onClick: () => openEditRequest(r) }, () => '编辑请求'),
        h(NPopconfirm, { onPositiveClick: () => removeRecording(r.id) }, {
          trigger: () => h(NButton, { size: 'small', type: 'error' }, () => '移除'),
          default: () => '从用例中移除？',
        }),
      ]),
  },
]

const pickColumns = [
  { type: 'selection' as const },
  {
    title: '应用',
    key: 'app_id',
    width: 110,
    render: (r: Recording) => appMap.value[r.app_id || ''] || '-',
    ellipsis: { tooltip: true },
  },
  { title: '类型', key: 'entry_type', width: 70 },
  { title: '路径', key: 'path', ellipsis: { tooltip: true } },
  {
    title: '响应质量', key: 'resp_quality', width: 90,
    render: (r: Recording) => {
      const q = getPickQuality(r)
      return h(NTag, { size: 'small', type: pickQualityColorMap[q] }, () => pickQualityLabelMap[q])
    },
  },
  {
    title: '录制时间',
    key: 'timestamp',
    width: 145,
    render: (r: Recording) => fmtTime(r.timestamp || r.created_at),
  },
]

async function loadCase() {
  const res = await testCaseApi.get(caseId)
  testCase.value = res.data
}

async function loadRecordings() {
  loading.value = true
  try {
    const res = await testCaseApi.getRecordings(caseId)
    recordings.value = res.data
  } finally {
    loading.value = false
  }
}

async function removeRecording(recordingId: string) {
  await testCaseApi.removeRecording(caseId, recordingId)
  message.success('已移除')
  selectedRecordingIds.value = selectedRecordingIds.value.filter(id => id !== recordingId)
  await Promise.all([loadCase(), loadRecordings()])
}

async function batchRemove() {
  batchRemoving.value = true
  try {
    await Promise.all(selectedRecordingIds.value.map(id => testCaseApi.removeRecording(caseId, id)))
    message.success(`已移除 ${selectedRecordingIds.value.length} 条录制`)
    selectedRecordingIds.value = []
    await Promise.all([loadCase(), loadRecordings()])
  } finally {
    batchRemoving.value = false
  }
}

async function handleDeleteCase() {
  await testCaseApi.delete(caseId)
  message.success('用例已删除')
  router.push('/test-cases')
}

// When opening add modal: load all recordings, excluding already-added ones
const existingIds = computed(() => new Set(recordings.value.map(r => r.id)))

async function openAddModal() {
  showAddModal.value = true
  pickLoading.value = true
  pickedIds.value = []
  pickFilter.value = ''
  pickAppId.value = null
  pickSessionId.value = null
  pickQuality.value = null
  pickDateRange.value = null
  try {
    const [recsRes, appsRes, sessRes] = await Promise.all([
      recordingApi.listAll(),
      applicationApi.list(),
      sessionApi.listAll(),
    ])
    appOptions.value = appsRes.data.map((a: any) => ({ label: a.name, value: a.id }))
    appMap.value = Object.fromEntries(appsRes.data.map((a: any) => [a.id, a.name]))
    allSessions.value = sessRes
    pickSessionOptions.value = sessRes.map((s: Session) => ({
      label: `${s.name || s.id.slice(0, 8)} (${s.status})`,
      value: s.id,
    }))
    // Exclude recordings already in this case
    pickList.value = recsRes.filter((r: Recording) => !existingIds.value.has(r.id))
  } finally {
    pickLoading.value = false
  }
}

watch(showAddModal, (val) => {
  if (val) openAddModal()
})

async function handleAdd() {
  if (!pickedIds.value.length) return
  adding.value = true
  try {
    const res = await testCaseApi.addRecordings(caseId, pickedIds.value as string[])
    message.success(`已添加 ${res.data.added} 条录制`)
    showAddModal.value = false
    await Promise.all([loadCase(), loadRecordings()])
  } finally {
    adding.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadCase(), loadRecordings()])
})
</script>
