<template>
  <n-space vertical :size="16">
    <n-space justify="space-between" align="center">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/recording')">录制会话</n-breadcrumb-item>
        <n-breadcrumb-item>{{ session?.name || `会话 ${sessionId.slice(0, 8)}` }}</n-breadcrumb-item>
      </n-breadcrumb>
      <n-space>
        <n-button @click="loadPage">刷新</n-button>
        <n-button @click="router.push(`/recording?session_id=${sessionId}`)">回到列表</n-button>
        <n-button v-if="session?.app_id" @click="router.push(`/applications/${session.app_id}`)">查看应用</n-button>
      </n-space>
    </n-space>

    <n-grid :cols="4" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card>
          <n-statistic label="录制数量" :value="session?.record_count || 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="接口条目" :value="recordingTotal" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="平均耗时" :value="avgDuration">
            <template #suffix>ms</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="入口类型数" :value="entryTypeCount" />
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card v-if="session" title="会话详情">
      <template #header-extra>
        <n-tag :type="sessionStatusType[session.status] || 'default'">
          {{ session.status }}
        </n-tag>
      </template>
      <n-descriptions bordered :column="2">
        <n-descriptions-item label="会话名称">{{ session.name || '-' }}</n-descriptions-item>
        <n-descriptions-item label="所属应用">{{ appName }}</n-descriptions-item>
        <n-descriptions-item label="开始时间">{{ fmtTime(session.started_at) || '-' }}</n-descriptions-item>
        <n-descriptions-item label="结束时间">{{ fmtTime(session.stopped_at) || '-' }}</n-descriptions-item>
        <n-descriptions-item label="创建人">{{ session.created_by || '-' }}</n-descriptions-item>
        <n-descriptions-item label="错误信息">{{ session.error_message || '-' }}</n-descriptions-item>
        <n-descriptions-item label="说明" :span="2">{{ session.description || '-' }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card v-if="session?.status === 'ACTIVE'" title="代理录制（推荐）">
      <template #header-extra>
        <n-tooltip>
          <template #trigger>
            <n-tag type="success" size="small">银行 / XML 场景优先</n-tag>
          </template>
          当被测系统很多接口共用一个 URL，例如都走 /api/bank/service，而业务靠 service_id / trand_id 区分时，推荐让 Postman 或功能测试平台直接打平台代理地址。平台代理会逐条转发并逐条落库，不依赖 arex-agent 在 Servlet 入口的去重行为。
        </n-tooltip>
      </template>
      <n-space vertical :size="12">
        <n-alert type="info" :show-icon="false">
          录制方式：把原始请求地址从
          <strong>{{ originalServiceBase }}</strong>
          改成
          <strong>{{ proxyBase }}</strong>
          ，请求方法、Header、请求体保持不变。
        </n-alert>
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="原始路径" label-placement="left" :label-width="80">
              <n-input v-model:value="proxyPath" placeholder="/api/bank/service" clearable />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="代理 URL" label-placement="left" :label-width="80">
              <n-input :value="proxyTargetUrl" readonly />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="原始服务" label-placement="left" :label-width="80">
              <n-input :value="originalServiceBase" readonly />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="推荐 Header" label-placement="left" :label-width="100">
              <n-input :value="drContentType" readonly />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-space>
          <n-button @click="copyProxyUrl">复制代理 URL</n-button>
          <n-button @click="copyProxyCurl">复制示例 cURL</n-button>
        </n-space>
        <n-alert type="warning" :show-icon="false">
          如果你继续直接打 <strong>{{ originalServiceBase }}</strong>，同一路径多交易码请求可能只录到 1 条。银行项目默认应优先走平台代理录制。
        </n-alert>
      </n-space>
    </n-card>

    <!-- 直接录制面板：仅 ACTIVE 会话可用 -->
    <n-card v-if="session?.status === 'ACTIVE'" title="平台代发录制（高级）">
      <template #header-extra>
        <n-tooltip>
          <template #trigger>
            <n-tag type="info" size="small">单条调试</n-tag>
          </template>
          适合临时验证单个请求，或在你不方便改 Postman 目标地址时，由平台替你向被测服务发请求并保存录制。
        </n-tooltip>
      </template>
      <n-space vertical :size="12">
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="目标 URL" label-placement="left" :label-width="80">
              <n-input v-model:value="drUrl" placeholder="http://host:port/api/bank/service" clearable />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Content-Type" label-placement="left" :label-width="100">
              <n-input v-model:value="drContentType" placeholder="application/xml" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-form-item label="请求体" label-placement="top">
          <n-input
            v-model:value="drBody"
            type="textarea"
            :rows="6"
            placeholder="<request><service_id>OPEN_ACCOUNT</service_id>...</request>"
          />
        </n-form-item>
        <n-space align="center">
          <n-button type="primary" :loading="drLoading" :disabled="!drUrl" @click="doDirectRecord">发送并录制</n-button>
          <n-tag v-if="drLastResult" :type="drLastResult.ok ? 'success' : 'error'" size="small">
            上次: HTTP {{ drLastResult.status_code }} · {{ drLastResult.duration_ms }}ms · {{ drLastResult.operation }}
          </n-tag>
        </n-space>
      </n-space>
    </n-card>

    <n-card title="会话内录制">
      <template #header-extra>
        <n-space align="center" wrap>
          <n-input
            v-model:value="search"
            clearable
            placeholder="搜索路径 / 交易码"
            style="width: 220px"
            @keyup.enter="onFilterChange"
          />
          <n-select
            v-model:value="entryType"
            clearable
            :options="entryTypeOptions"
            placeholder="入口类型"
            style="width: 140px"
            @update:value="onFilterChange"
          />
          <n-select
            v-model:value="recordStatus"
            clearable
            :options="recordStatusOptions"
            placeholder="录制状态"
            style="width: 140px"
            @update:value="onFilterChange"
          />
          <n-date-picker
            v-model:value="createdRange"
            type="datetimerange"
            clearable
            :shortcuts="dateShortcuts"
            style="width: 320px"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            @update:value="onFilterChange"
            @clear="onFilterChange"
          />
          <n-button size="small" @click="clearFilters">清空筛选</n-button>
          <n-button @click="loadRecordings">查询</n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="columns"
        :data="recordings"
        :loading="loading"
        :pagination="pagination"
        :scroll-x="1120"
        remote
        @update:sorter="onSorterChange"
      />
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { computed, h, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NAlert,
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NDataTable,
  NDatePicker,
  NDescriptions,
  NDescriptionsItem,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NSelect,
  NSpace,
  NStatistic,
  NTag,
  NTooltip,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { usePageSummary } from '@/composables/usePageSummary'
import { recordingApi, sessionApi, type Recording, type Session } from '@/api/recordings'
import { createDateShortcuts, type DateRangeValue } from '@/utils/dateRange'
import { fmtTime } from '@/utils/time'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const { setPageSummary, clearPageSummary } = usePageSummary()
const sessionId = String(route.params.id)

const session = ref<Session | null>(null)
const appName = ref('-')
const appHost = ref('localhost')
const appPort = ref(8081)
const recordings = ref<Recording[]>([])
const recordingTotal = ref(0)
const loading = ref(false)
const search = ref('')
const entryType = ref<string | null>(null)
const recordStatus = ref<string | null>(null)
const createdRange = ref<DateRangeValue>(null)
const sortField = ref<'created_at' | 'duration_ms'>('created_at')
const sortOrder = ref<'ascend' | 'descend'>('descend')
const dateShortcuts = createDateShortcuts()

const entryTypeOptions = [
  { label: 'HTTP', value: 'HTTP' },
  { label: 'DUBBO', value: 'DUBBO' },
  { label: 'MYBATIS', value: 'MYBATIS' },
  { label: 'JAVA', value: 'JAVA' },
]

const recordStatusOptions = [
  { label: '原始', value: 'ORIGINAL' },
  { label: '回放', value: 'REPLAYED' },
  { label: '已处理', value: 'PROCESSED' },
]

const sessionStatusType: Record<string, 'default' | 'info' | 'success' | 'warning' | 'error'> = {
  ACTIVE: 'info',
  COLLECTING: 'warning',
  DONE: 'success',
  FAILED: 'error',
}

const avgDuration = computed(() => {
  const values = recordings.value.map(item => item.duration_ms || 0).filter(Boolean)
  if (values.length === 0) return 0
  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length)
})

const entryTypeCount = computed(() => new Set(recordings.value.map(item => item.entry_type).filter(Boolean)).size)

const pagination = reactive({
  page: 1,
  pageSize: 12,
  pageSizes: [12, 20, 50],
  itemCount: 0,
  showSizePicker: true,
  onChange: (page: number) => {
    pagination.page = page
    loadRecordings()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadRecordings()
  },
})

const columns = computed<DataTableColumns<Recording>>(() => [
  {
    title: '入口类型',
    key: 'entry_type',
    width: 90,
    render: (row) => h(NTag, { size: 'small', type: 'info' }, () => row.entry_type || '-'),
  },
  { title: 'Host', key: 'host', width: 170, ellipsis: { tooltip: true } },
  { title: '路径', key: 'path', width: 260, ellipsis: { tooltip: true } },
  {
    title: '标签',
    key: 'tags',
    width: 180,
    render: (row) => {
      if (!row.tags?.length) return '-'
      return h(NSpace, { size: 4 }, () => row.tags!.map(tag => h(NTag, { size: 'small', type: 'warning' }, () => tag)))
    },
  },
  {
    title: '耗时(ms)',
    key: 'duration_ms',
    width: 90,
    sorter: true,
    sortOrder: sortField.value === 'duration_ms' ? sortOrder.value : false,
    render: (row) => row.duration_ms ?? '-',
  },
  { title: '状态', key: 'status', width: 100 },
  {
    title: '时间',
    key: 'created_at',
    width: 170,
    sorter: true,
    sortOrder: sortField.value === 'created_at' ? sortOrder.value : false,
    render: (row) => fmtTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => h(NButton, { size: 'small', onClick: () => router.push(`/recordings/${row.id}`) }, () => '查看'),
  },
])

// ── Direct-record state ──────────────────────────────────────────────────────
const drUrl = ref('')
const drContentType = ref('application/xml')
const drBody = ref('')
const drLoading = ref(false)
const drLastResult = ref<{ ok: boolean; status_code: number; duration_ms: number; operation: string } | null>(null)
const proxyPath = ref('/api/bank/service')

const currentHost = computed(() => {
  if (typeof window === 'undefined') return 'localhost'
  return window.location.hostname || 'localhost'
})

const proxyBase = computed(() => `http://${currentHost.value}:8001/api/v1/proxy/${appName.value}`)
const originalServiceBase = computed(() => `http://${appHost.value}:${appPort.value}`)

const normalizedProxyPath = computed(() => {
  const raw = (proxyPath.value || '').trim()
  if (!raw) return '/api/bank/service'
  return raw.startsWith('/') ? raw : `/${raw}`
})

const proxyTargetUrl = computed(() => `${proxyBase.value}${normalizedProxyPath.value}`)

async function copyText(text: string, successMessage: string) {
  try {
    await navigator.clipboard.writeText(text)
    message.success(successMessage)
  } catch {
    message.error('复制失败，请手动复制')
  }
}

async function copyProxyUrl() {
  await copyText(proxyTargetUrl.value, '代理 URL 已复制')
}

async function copyProxyCurl() {
  const body = drBody.value || '<request><service_id>OPEN_ACCOUNT</service_id></request>'
  const curl = [
    `curl -X POST '${proxyTargetUrl.value}'`,
    `-H 'Content-Type: ${drContentType.value || 'application/xml'}'`,
    `-d '${body.replace(/'/g, `'\"'\"'`)}'`,
  ].join(' \\\n')
  await copyText(curl, '示例 cURL 已复制')
}

async function doDirectRecord() {
  if (!drUrl.value) return
  drLoading.value = true
  try {
    const res = await sessionApi.directRecord(sessionId, {
      method: 'POST',
      url: drUrl.value,
      headers: { 'Content-Type': drContentType.value },
      body: drBody.value || undefined,
    })
    const d = res.data
    // Extract auto-detected operation from recording path via service_id regex
    const opMatch = drBody.value.match(/<service_id>\s*([^<]+)\s*<\/service_id>/i)
    drLastResult.value = {
      ok: d.status_code >= 200 && d.status_code < 400,
      status_code: d.status_code,
      duration_ms: d.duration_ms,
      operation: opMatch ? opMatch[1].trim() : d.recording_id.slice(0, 8),
    }
    if (drLastResult.value.ok) {
      message.success(`录制成功: ${drLastResult.value.operation}`)
    } else {
      message.warning(`录制已保存，目标服务返回 HTTP ${d.status_code}`)
    }
    // Refresh recordings list and session (to update live count)
    await loadPage()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '直接录制失败')
  } finally {
    drLoading.value = false
  }
}

async function loadSession() {
  try {
    const res = await sessionApi.get(sessionId)
    session.value = res.data
    if (res.data.app_id) {
      const appRes = await applicationApi.get(res.data.app_id)
      appName.value = appRes.data.name
      appHost.value = appRes.data.ssh_host || 'localhost'
      appPort.value = appRes.data.repeater_port || 8081
      drUrl.value = `http://${appRes.data.ssh_host}:${appRes.data.repeater_port}/api/bank/service`
    } else {
      appName.value = '-'
      appHost.value = 'localhost'
      appPort.value = 8081
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载会话详情失败')
  }
}

async function loadRecordings() {
  loading.value = true
  try {
    const res = await recordingApi.list({
      session_id: sessionId,
      entry_type: entryType.value || undefined,
      status: recordStatus.value || undefined,
      path_contains: search.value.trim() || undefined,
      created_after: createdRange.value ? new Date(createdRange.value[0]).toISOString() : undefined,
      created_before: createdRange.value ? new Date(createdRange.value[1]).toISOString() : undefined,
      sort_by: sortField.value,
      sort_order: sortOrder.value === 'ascend' ? 'asc' : 'desc',
      limit: pagination.pageSize,
      offset: (pagination.page - 1) * pagination.pageSize,
    })
    recordings.value = res.data.items
    recordingTotal.value = res.data.total
    pagination.itemCount = res.data.total
  } catch (error: any) {
    recordings.value = []
    recordingTotal.value = 0
    pagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载会话录制失败')
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  search.value = ''
  entryType.value = null
  recordStatus.value = null
  createdRange.value = null
  sortField.value = 'created_at'
  sortOrder.value = 'descend'
  pagination.page = 1
  loadRecordings()
}

function onFilterChange() {
  pagination.page = 1
  loadRecordings()
}

function onSorterChange(sorter: { columnKey?: string; order?: 'ascend' | 'descend' | false } | null) {
  if (!sorter?.columnKey || !sorter.order) {
    sortField.value = 'created_at'
    sortOrder.value = 'descend'
  } else if (sorter.columnKey === 'duration_ms') {
    sortField.value = 'duration_ms'
    sortOrder.value = sorter.order
  } else {
    sortField.value = 'created_at'
    sortOrder.value = sorter.order
  }
  pagination.page = 1
  loadRecordings()
}

async function loadPage() {
  await Promise.all([loadSession(), loadRecordings()])
}

onMounted(loadPage)

watch(recordingTotal, (count) => {
  setPageSummary(`共 ${count} 条会话录制`)
}, { immediate: true })

onBeforeUnmount(clearPageSummary)
</script>
