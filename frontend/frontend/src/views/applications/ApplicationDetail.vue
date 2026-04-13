<template>
  <n-space vertical :size="16">
    <n-card v-if="app">
      <template #header>
        <n-space align="center">
          <span>{{ app.name }}</span>
          <n-tag :type="statusColor[app.agent_status] || 'default'" size="small">
            {{ agentStatusLabel[app.agent_status] || app.agent_status }}
          </n-tag>
        </n-space>
      </template>
      <template #header-extra>
        <n-space>
          <n-button size="small" @click="openEdit">编辑应用</n-button>
          <n-button size="small" @click="testSsh" :loading="testing">测试 SSH</n-button>
          <n-button size="small" @click="discoverPid" :loading="discovering">发现 PID</n-button>
          <n-button
            v-if="app.agent_status !== 'ATTACHED'"
            size="small" type="primary"
            @click="attachAgent" :loading="attaching"
          >挂载 Agent</n-button>
          <n-button
            v-else
            size="small" type="warning"
            @click="detachAgent" :loading="detaching"
          >卸载 Agent</n-button>
        </n-space>
      </template>

      <n-descriptions bordered :column="2">
        <n-descriptions-item label="应用说明">{{ app.description || '-' }}</n-descriptions-item>
        <n-descriptions-item label="SSH Host">{{ app.ssh_host }}:{{ app.ssh_port }}</n-descriptions-item>
        <n-descriptions-item label="SSH User">{{ app.ssh_user }}</n-descriptions-item>
        <n-descriptions-item label="JAR 名称">{{ app.java_jar_name || '-' }}</n-descriptions-item>
        <n-descriptions-item label="JVM PID">{{ app.java_pid || '-' }}</n-descriptions-item>
        <n-descriptions-item label="应用端口">{{ app.repeater_port }}</n-descriptions-item>
        <n-descriptions-item label="Sandbox 端口">{{ app.sandbox_port }}</n-descriptions-item>
        <n-descriptions-item label="采样率">{{ Math.round((app.sample_rate ?? 1) * 100) }}%</n-descriptions-item>
        <n-descriptions-item label="接口识别字段">
          {{ app.operation_id_tags?.length ? app.operation_id_tags.join(', ') : '默认内置字段' }}
        </n-descriptions-item>
        <n-descriptions-item label="默认忽略字段">
          {{ app.default_ignore_fields?.length ? app.default_ignore_fields.join(', ') : '-' }}
        </n-descriptions-item>
        <n-descriptions-item label="Sandbox 路径" :span="2">{{ app.sandbox_home }}</n-descriptions-item>
        <n-descriptions-item label="录制数据目录" :span="2">{{ app.repeater_data_dir }}</n-descriptions-item>
        <n-descriptions-item label="最后心跳">{{ fmtTime(app.last_heartbeat) || '-' }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <!-- Recording Controls -->
    <n-card title="录制控制">
      <template #header-extra>
        <n-button size="small" type="primary" @click="saveRecordingControls" :loading="savingControls">保存</n-button>
      </template>
      <n-form label-placement="left" label-width="120px">
        <n-form-item label="采样率">
          <n-space align="center">
            <n-slider
              v-model:value="sampleRatePercent"
              :min="1" :max="100" :step="1"
              style="width: 200px"
            />
            <span style="min-width:40px">{{ sampleRatePercent }}%</span>
          </n-space>
          <template #feedback>
            <span style="color:#999;font-size:12px">录制时按比例随机采样，100% 表示全量录制</span>
          </template>
        </n-form-item>
        <n-form-item label="脱敏规则">
          <n-space vertical style="width:100%">
            <n-space v-for="(rule, i) in desensitizeRules" :key="i" align="center" wrap>
              <n-input v-model:value="rule.field" placeholder="字段名" style="width:130px" />
              <n-select
                v-model:value="rule.action"
                :options="desensitizeActionOptions"
                style="width:140px"
              />
              <template v-if="rule.action === 'partial'">
                <n-input-number v-model:value="rule.keep_start" :min="0" placeholder="保留前N位" style="width:100px" />
                <n-input-number v-model:value="rule.keep_end" :min="0" placeholder="保留后N位" style="width:100px" />
              </template>
              <n-button size="small" type="error" circle @click="removeDesensitizeRule(i)">×</n-button>
            </n-space>
            <n-button size="small" dashed @click="addDesensitizeRule">+ 添加脱敏规则</n-button>
            <span style="color:#999;font-size:12px">
              remove=删除字段 &nbsp; mask=替换为*** &nbsp; partial=部分遮盖 &nbsp; hash=哈希摘要
            </span>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- Replay Defaults -->
    <n-card title="回放默认配置">
      <template #header-extra>
        <n-button size="small" type="primary" @click="saveReplayDefaults" :loading="savingDefaults">保存</n-button>
      </template>
      <n-form label-placement="left" label-width="130px">
        <n-form-item label="默认忽略字段">
          <n-dynamic-tags v-model:value="defaultIgnoreFields" />
        </n-form-item>
        <n-form-item label="默认性能阈值(ms)">
          <n-input-number v-model:value="defaultPerfThreshold" :min="0" clearable placeholder="留空不限制" />
        </n-form-item>
      </n-form>
      <n-alert type="info" style="margin-top:8px;font-size:12px">
        在回放中心点击「加载应用默认配置」时，会自动填入以上配置。
      </n-alert>
    </n-card>

    <!-- XML Request Templates -->
    <n-card title="XML 默认请求模板">
      <template #header-extra>
        <n-button size="small" type="primary" @click="saveXmlTemplate" :loading="savingXmlTemplate">保存</n-button>
      </template>
      <n-space vertical>
        <div v-for="(tpl, idx) in xmlTemplates" :key="idx" style="width:100%;border:1px solid #e8e8e8;border-radius:6px;padding:12px">
          <n-space align="center" style="margin-bottom:8px">
            <n-input
              v-model:value="tpl.serviceId"
              placeholder="service_id，如 OPEN_ACCOUNT"
              style="width: 220px; font-family: monospace"
            />
            <n-button size="small" type="error" circle @click="xmlTemplates.splice(idx, 1)">×</n-button>
          </n-space>
          <n-input
            v-model:value="tpl.xml"
            type="textarea"
            :rows="6"
            placeholder="<request>&#10;  <service_id>OPEN_ACCOUNT</service_id>&#10;  <customer_no>C001</customer_no>&#10;</request>"
            style="font-family: monospace; font-size: 13px"
          />
        </div>
        <n-button size="small" dashed @click="xmlTemplates.push({ serviceId: '', xml: '' })">+ 添加模板</n-button>
      </n-space>
      <n-alert type="warning" style="margin-top:8px;font-size:12px">
        回放时如果请求体为空（XML 接口常见），会根据录制响应中的 service_id 自动匹配对应模板。<br/>
        适用于 Repeater Agent 不录制 XML 请求体的场景。留空则不启用。
      </n-alert>
    </n-card>

    <!-- Repeater Config -->
    <n-card title="Repeater 配置">
      <template #header-extra>
        <n-space>
          <n-button size="small" @click="loadDefaultConfig">加载默认</n-button>
          <n-button size="small" type="primary" @click="saveConfig" :loading="savingConfig">保存</n-button>
          <n-button size="small" @click="pushConfig" :loading="pushing">推送到主机</n-button>
        </n-space>
      </template>
      <n-input
        v-model:value="configJson"
        type="textarea"
        :rows="14"
        style="font-family: monospace; font-size: 13px"
        placeholder="repeater-config.json 内容"
      />
    </n-card>

  <!-- Edit Modal -->
  <n-modal v-model:show="showEdit" preset="dialog" title="编辑应用" style="width: 760px">
    <application-editor-form
      v-model="editForm"
      v-model:show-advanced="showAdvancedEditFields"
      :show-name="false"
      :show-advanced-guide="false"
    />
    <template #action>
      <n-button @click="showEdit = false">取消</n-button>
      <n-button type="primary" :loading="savingEdit" @click="handleSaveEdit">保存</n-button>
    </template>
  </n-modal>

    <!-- Recent Sessions -->
    <n-card title="录制会话">
      <template #header-extra>
        <n-button size="small" type="primary" @click="createSession">+ 开始录制</n-button>
      </template>
      <n-data-table
        :columns="sessionColumns"
        :data="sessions"
        :loading="sessionsLoading"
        :row-key="(r: Session) => r.id"
        :checked-row-keys="selectedSessionIds"
        @update:checked-row-keys="selectedSessionIds = $event as string[]"
      />
      <n-space v-if="selectedSessionIds.length > 0" align="center" style="margin-top:10px">
        <span>已选 {{ selectedSessionIds.length }} 条</span>
        <n-button size="small" type="error" :loading="batchDeletingSessions" @click="deleteSelectedSessions">批量删除</n-button>
      </n-space>
      <n-space justify="end" align="center" style="margin-top: 12px">
        <span style="font-size:13px;color:#666">共 {{ sessionTotal }} 条</span>
        <n-pagination
          v-model:page="sessionPagination.page"
          v-model:page-size="sessionPagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :item-count="sessionPagination.itemCount"
          show-size-picker
          :show-quick-jumper="true"
          :disabled="sessionsLoading"
          @update:page="loadSessions"
          @update:page-size="handleSessionPageSizeChange"
        />
      </n-space>
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, h, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NCard, NSpace, NTag, NButton, NDescriptions, NDescriptionsItem,
  NInput, NInputNumber, NSelect, NDataTable, NModal, NForm, NFormItem, NPagination,
  NSlider, NDynamicTags, NAlert, NTooltip, useMessage, useDialog,
} from 'naive-ui'
import { applicationApi, type Application, type DesensitizeRule } from '@/api/applications'
import ApplicationEditorForm from '@/components/applications/ApplicationEditorForm.vue'
import { useOffsetPagination } from '@/composables/useOffsetPagination'
import { usePageSummary } from '@/composables/usePageSummary'
import { sessionApi, configApi, type Session } from '@/api/recordings'
import { fmtTime } from '@/utils/time'
import {
  buildApplicationPayload,
  createApplicationEditorModel,
  createEmptyApplicationEditorModel,
  type ApplicationEditorModel,
} from '@/utils/applicationEditor'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const { setPageSummary, clearPageSummary } = usePageSummary()

// 收集所有活跃的轮询，组件销毁时统一清理
const activePolls = new Set<ReturnType<typeof setInterval>>()
onBeforeUnmount(() => { activePolls.forEach(clearInterval); activePolls.clear() })

const appId = route.params.id as string
const app = ref<Application | null>(null)
const configJson = ref('')
const sessions = ref<Session[]>([])
const sessionsLoading = ref(false)
const sessionTotal = ref(0)
const {
  pagination: sessionPagination,
  offset: sessionOffset,
  resetPage: resetSessionPage,
  setTotal: setSessionTotal,
  updatePageSize: updateSessionPageSize,
} = useOffsetPagination({ pageSize: 20, pageSizes: [10, 20, 50] })
const selectedSessionIds = ref<string[]>([])
const batchDeletingSessions = ref(false)

const testing = ref(false)
const discovering = ref(false)
const attaching = ref(false)
const detaching = ref(false)
const savingConfig = ref(false)
const savingControls = ref(false)
const pushing = ref(false)
const showEdit = ref(false)
const savingEdit = ref(false)
const showAdvancedEditFields = ref(false)

// Recording controls
const sampleRatePercent = ref(100)
const desensitizeRules = ref<DesensitizeRule[]>([])

// Replay defaults
const defaultIgnoreFields = ref<string[]>([])
const defaultPerfThreshold = ref<number | undefined>(undefined)
const savingDefaults = ref(false)

// XML request templates
const xmlTemplates = ref<{ serviceId: string; xml: string }[]>([])
const savingXmlTemplate = ref(false)

const desensitizeActionOptions = [
  { label: '删除字段 (remove)', value: 'remove' },
  { label: '替换为*** (mask)', value: 'mask' },
  { label: '部分遮盖 (partial)', value: 'partial' },
  { label: '哈希摘要 (hash)', value: 'hash' },
]

function addDesensitizeRule() {
  desensitizeRules.value.push({ field: '', action: 'mask' })
}

function removeDesensitizeRule(i: number) {
  desensitizeRules.value.splice(i, 1)
}

async function saveReplayDefaults() {
  savingDefaults.value = true
  try {
    const res = await applicationApi.update(appId, {
      default_ignore_fields: defaultIgnoreFields.value.length ? defaultIgnoreFields.value : undefined,
      default_perf_threshold_ms: defaultPerfThreshold.value || undefined,
    })
    app.value = res.data
    message.success('回放默认配置已保存')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    savingDefaults.value = false
  }
}

async function saveXmlTemplate() {
  savingXmlTemplate.value = true
  try {
    // Build JSON map from templates array
    const validTemplates = xmlTemplates.value.filter(t => t.serviceId.trim() && t.xml.trim())
    let templateValue: string | undefined
    if (validTemplates.length > 0) {
      const map: Record<string, string> = {}
      for (const t of validTemplates) {
        map[t.serviceId.trim()] = t.xml.trim()
      }
      templateValue = JSON.stringify(map)
    }
    const res = await applicationApi.update(appId, {
      xml_request_template: templateValue,
    })
    app.value = res.data
    message.success('XML 默认请求模板已保存')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    savingXmlTemplate.value = false
  }
}

async function saveRecordingControls() {
  savingControls.value = true
  try {
    const res = await applicationApi.update(appId, {
      sample_rate: sampleRatePercent.value / 100,
      desensitize_rules: desensitizeRules.value.filter(r => r.field),
    })
    app.value = res.data
    message.success('录制控制配置已保存')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    savingControls.value = false
  }
}

const editForm = ref<ApplicationEditorModel>(createEmptyApplicationEditorModel())

function openEdit() {
  if (!app.value) return
  editForm.value = createApplicationEditorModel(app.value)
  showAdvancedEditFields.value = true
  showEdit.value = true
}

async function handleSaveEdit() {
  savingEdit.value = true
  try {
    const payload = buildApplicationPayload(editForm.value)
    const res = await applicationApi.update(appId, payload)
    app.value = res.data
    message.success('应用更新成功')
    showEdit.value = false
  } catch (e: any) {
    message.error(e.response?.data?.detail || '更新失败')
  } finally {
    savingEdit.value = false
  }
}

const statusColor: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
  ATTACHED: 'success', DETACHED: 'warning', ERROR: 'error', UNKNOWN: 'default',
}

const agentStatusLabel: Record<string, string> = {
  ATTACHED: '已挂载', DETACHED: '已卸载', ERROR: '错误', UNKNOWN: '未知',
}

const sessionStatusLabel: Record<string, string> = {
  ACTIVE: '录制中', DONE: '已完成', COLLECTING: '采集中', STOPPED: '已停止', ERROR: '错误',
}

const sessionStatusColor: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  ACTIVE: 'success', DONE: 'info', COLLECTING: 'warning', STOPPED: 'default', ERROR: 'error',
}

const sessionColumns = [
  { type: 'selection' as const, width: 40 },
  { title: '名称', key: 'name', render: (r: Session) => r.name || fmtTime(r.started_at) },
  {
    title: '状态', key: 'status',
    render: (r: Session) => {
      const tag = h(NTag, {
        type: sessionStatusColor[r.status] || 'default',
        size: 'small',
      }, () => sessionStatusLabel[r.status] || r.status)
      if (r.status === 'ERROR' && r.error_message) {
        return h(NTooltip, { trigger: 'hover' }, {
          trigger: () => tag,
          default: () => r.error_message,
        })
      }
      return tag
    },
  },
  { title: '录制数', key: 'record_count' },
  { title: '开始时间', key: 'started_at', render: (r: Session) => fmtTime(r.started_at) },
  {
    title: '操作',
    key: 'actions',
    render: (r: Session) =>
      h(NSpace, { size: 'small' }, () => [
        r.status === 'ACTIVE'
          ? h(NButton, {
              size: 'small', type: 'warning',
              onClick: () => stopSession(r),
            }, () => '停止')
          : null,
        h(NButton, {
          size: 'small',
          onClick: () => router.push(`/recording?session_id=${r.id}&app_id=${appId}`),
        }, () => '查看录制'),
        h(NButton, {
          size: 'small', type: 'error',
          onClick: () => deleteSession(r),
        }, () => '删除'),
      ]),
  },
]

async function stopSession(session: Session) {
  try {
    await sessionApi.stop(session.id)
    message.success('录制已停止，正在收集数据...')
    // 轮询等待状态变为 DONE，最多等待 150 次（5 分钟）
    let pollCount = 0
    const MAX_POLLS = 150
    const poll = setInterval(async () => {
      pollCount++
      const res = await sessionApi.get(session.id)
      const idx = sessions.value.findIndex(s => s.id === session.id)
      if (idx !== -1) sessions.value[idx] = res.data
      if (res.data.status === 'DONE' || res.data.status === 'ERROR' || pollCount >= MAX_POLLS) {
        clearInterval(poll)
        activePolls.delete(poll)
        if (res.data.status === 'DONE') {
          message.success(`数据收集完成，共 ${res.data.record_count} 条录制`)
        } else if (pollCount >= MAX_POLLS) {
          message.warning('数据收集超时，请手动刷新页面查看结果')
        } else {
          const errDetail = res.data.error_message || '请检查 SSH 连接和录制目录配置'
          message.error(`数据收集失败（已收集 ${res.data.record_count} 条）：${errDetail}`, { duration: 8000 })
        }
      }
    }, 2000)
    activePolls.add(poll)
  } catch (e: any) {
    message.error(e.response?.data?.detail || '停止失败')
  }
}

async function deleteSession(session: Session) {
  if (session.status === 'ACTIVE') {
    message.warning('请先停止录制再删除')
    return
  }
  try {
    await sessionApi.delete(session.id)
    selectedSessionIds.value = selectedSessionIds.value.filter(i => i !== session.id)
    if (sessions.value.length === 1 && sessionPagination.page > 1) {
      sessionPagination.page -= 1
    }
    await loadSessions()
    message.success('会话已删除')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '删除失败')
  }
}

async function deleteSelectedSessions() {
  const active = sessions.value.filter(s => selectedSessionIds.value.includes(s.id) && s.status === 'ACTIVE')
  if (active.length) {
    message.warning('选中的会话中有正在录制的会话，请先停止录制再删除')
    return
  }
  dialog.warning({
    title: '确认批量删除',
    content: `将删除选中的 ${selectedSessionIds.value.length} 个录制会话及其所有录制数据，确认吗？`,
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      batchDeletingSessions.value = true
      try {
        const deletedCount = selectedSessionIds.value.length
        const shouldMovePrevPage =
          sessions.value.length === deletedCount && sessionPagination.page > 1
        await sessionApi.batchDelete(selectedSessionIds.value)
        message.success(`已删除 ${deletedCount} 个会话`)
        selectedSessionIds.value = []
        if (shouldMovePrevPage) {
          sessionPagination.page -= 1
        }
        await loadSessions()
      } finally {
        batchDeletingSessions.value = false
      }
    },
  })
}

async function load() {
  const res = await applicationApi.get(appId)
  app.value = res.data

  // Sync recording controls from app data
  sampleRatePercent.value = Math.round((res.data.sample_rate ?? 1.0) * 100)
  desensitizeRules.value = (res.data.desensitize_rules ?? []).map(r => ({ ...r }))

  // Sync replay defaults
  defaultIgnoreFields.value = [...(res.data.default_ignore_fields ?? [])]
  defaultPerfThreshold.value = res.data.default_perf_threshold_ms ?? undefined

  // Sync XML request templates
  const rawTpl = res.data.xml_request_template
  if (rawTpl) {
    try {
      const parsed = JSON.parse(rawTpl)
      if (typeof parsed === 'object' && !Array.isArray(parsed)) {
        // JSON map format: {"OPEN_ACCOUNT": "...", "QUERY_BALANCE": "..."}
        xmlTemplates.value = Object.entries(parsed).map(([serviceId, xml]) => ({
          serviceId,
          xml: xml as string,
        }))
      } else {
        // Backward compatible: plain XML string
        xmlTemplates.value = [{ serviceId: '', xml: rawTpl }]
      }
    } catch {
      xmlTemplates.value = [{ serviceId: '', xml: rawTpl }]
    }
  } else {
    xmlTemplates.value = []
  }

  // Load config
  try {
    const cfgRes = await configApi.get(appId)
    configJson.value = cfgRes.data.config_json
  } catch {
    // No config yet, will load default
  }

  await loadSessions()
}

async function loadSessions() {
  sessionsLoading.value = true
  try {
    const sRes = await sessionApi.list(appId, sessionPagination.pageSize, sessionOffset.value)
    sessions.value = sRes.data.items
    sessionTotal.value = sRes.data.total
    setSessionTotal(sRes.data.total)
  } finally {
    sessionsLoading.value = false
  }
}

function handleSessionPageSizeChange(size: number) {
  updateSessionPageSize(size)
  loadSessions()
}

watch(sessionTotal, (count) => {
  setPageSummary(`共 ${count} 条录制会话`)
}, { immediate: true })

onBeforeUnmount(clearPageSummary)

async function loadDefaultConfig() {
  const res = await configApi.getDefault(appId)
  configJson.value = JSON.stringify(res.data.config, null, 2)
}

async function testSsh() {
  testing.value = true
  try {
    const res = await applicationApi.sshTest(appId)
    if (res.data.success) {
      message.success(`SSH 连通: ${res.data.message}`)
    } else {
      message.error(`SSH 失败: ${res.data.message}`)
    }
  } finally {
    testing.value = false
  }
}

async function discoverPid() {
  discovering.value = true
  try {
    const res = await applicationApi.discoverPid(appId)
    if (res.data.pid) {
      message.success(`PID: ${res.data.pid}`)
      app.value!.java_pid = res.data.pid
    } else {
      message.warning('未找到 JVM 进程，请确认 java_jar_name 配置')
    }
  } finally {
    discovering.value = false
  }
}

async function attachAgent() {
  attaching.value = true
  try {
    const res = await applicationApi.attachAgent(appId)
    message.success(`Agent 已挂载`)
    app.value!.agent_status = res.data.agent_status
  } catch (e: any) {
    message.error(e.response?.data?.detail || '挂载失败')
  } finally {
    attaching.value = false
  }
}

async function detachAgent() {
  detaching.value = true
  try {
    await applicationApi.detachAgent(appId)
    message.success('Agent 已卸载')
    app.value!.agent_status = 'DETACHED'
  } finally {
    detaching.value = false
  }
}

async function saveConfig() {
  if (!configJson.value.trim()) {
    message.warning('配置内容为空，请先点击「加载默认」')
    return
  }
  try {
    JSON.parse(configJson.value)
  } catch {
    message.error('配置内容不是合法的 JSON，请检查格式')
    return
  }
  savingConfig.value = true
  try {
    await configApi.upsert(appId, { config_json: configJson.value })
    message.success('配置已保存')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败，请检查后端日志')
  } finally {
    savingConfig.value = false
  }
}

async function pushConfig() {
  pushing.value = true
  try {
    await configApi.push(appId)
    message.success('配置已推送到目标主机')
  } catch (e: any) {
    const detail = e.response?.data?.detail || ''
    if (detail.includes('No config')) {
      message.error('请先点击「保存」将配置存入数据库，再推送')
    } else {
      message.error(detail || '推送失败，请检查后端日志')
    }
  } finally {
    pushing.value = false
  }
}

async function createSession() {
  const res = await sessionApi.create({
    app_id: appId,
    name: `${app.value?.name ?? '录制'}_${new Date().toLocaleTimeString()}`,
  })
  message.success(`录制会话已创建: ${res.data.name || fmtTime(res.data.started_at)}`)
  resetSessionPage()
  await loadSessions()
}

onMounted(load)
</script>
