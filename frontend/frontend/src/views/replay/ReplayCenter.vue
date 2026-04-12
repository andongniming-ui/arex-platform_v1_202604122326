<template>
  <n-space vertical :size="16">
    <n-card title="发起回放">
      <n-form :model="form" label-placement="left" label-width="120px">
        <n-form-item label="测试用例" required>
          <n-select
            v-model:value="form.case_id"
            :options="caseOptions"
            placeholder="选择测试用例"
            filterable
          />
        </n-form-item>
        <n-form-item label="回放目标应用" required>
          <n-select
            v-model:value="form.target_app_id"
            :options="appOptions"
            placeholder="选择目标应用"
            @update:value="onTargetAppChange"
          />
        </n-form-item>
        <n-form-item label="环境标签">
          <n-input v-model:value="form.environment" placeholder="staging / test" />
        </n-form-item>
        <n-form-item label="Host 覆盖">
          <n-input v-model:value="form.override_host" placeholder="留空使用应用配置的 ssh_host" />
        </n-form-item>
        <n-form-item label="Webhook URL">
          <n-input v-model:value="form.webhook_url" placeholder="回放完成后 POST 通知，留空不回调" />
          <template #feedback>
            <span style="color:#999;font-size:12px">POST {"job_id","pass_rate","success_count",...} 到该地址</span>
          </template>
        </n-form-item>
        <n-form-item label="通知类型">
          <n-select
            v-model:value="form.notify_type"
            :options="notifyOptions"
            clearable
            placeholder="选择通知格式（留空发通用 JSON）"
          />
        </n-form-item>
        <n-form-item label="并发数">
          <n-input-number v-model:value="form.concurrency" :min="1" :max="20" />
        </n-form-item>
        <n-form-item label="请求间隔(ms)">
          <n-input-number v-model:value="form.delay_ms" :min="0" />
        </n-form-item>
        <n-form-item label="性能阈值(ms)">
          <n-input-number v-model:value="form.perf_threshold_ms" :min="0" clearable placeholder="超过此耗时标记为性能失败，留空不启用" />
        </n-form-item>
        <n-form-item label="Mock 子调用">
          <n-space align="center">
            <n-switch v-model:value="form.use_sub_invocation_mocks" />
            <span style="color:#666;font-size:13px">
              开启后通过 Repeater Agent 回放，DB/RPC/Redis 子调用使用录制时的返回值（需 Agent 在线且录制文件存在）
            </span>
          </n-space>
        </n-form-item>
        <!-- P0: 智能降噪 -->
        <n-form-item label="智能降噪">
          <n-space align="center">
            <n-switch v-model:value="form.smart_noise_reduction" />
            <span style="color:#666;font-size:13px">
              启用后自动忽略 30+ 常见动态字段（时间戳、UUID、Token 等），大幅减少 diff 误报
            </span>
          </n-space>
        </n-form-item>
        <!-- P0: 流量放大 -->
        <n-form-item label="流量放大">
          <n-space align="center">
            <n-input-number v-model:value="form.repeat_count" :min="1" :max="100" />
            <span style="color:#666;font-size:13px">
              每条录制重复回放 N 次，用于压测场景
            </span>
          </n-space>
        </n-form-item>
        <!-- P1: 请求头转换 -->
        <n-form-item label="请求头转换">
          <n-space vertical style="width:100%">
            <!-- 常用预设 -->
            <div>
              <span style="font-size:12px;color:#999;margin-right:8px">快速添加：</span>
              <n-space size="small" style="display:inline-flex;flex-wrap:wrap;gap:6px">
                <n-tag
                  v-for="preset in headerPresets"
                  :key="preset.label"
                  size="small"
                  :type="preset.tagType"
                  style="cursor:pointer"
                  @click="addPresetTransform(preset)"
                >
                  {{ preset.label }}
                </n-tag>
              </n-space>
            </div>
            <!-- 已配置的转换列表 -->
            <n-space
              v-for="(t, i) in form.header_transforms"
              :key="i"
              align="center"
              wrap
              style="background:#fafafa;padding:6px 10px;border-radius:4px;border:1px solid #e8e8e8"
            >
              <n-select
                v-model:value="t.type"
                :options="headerTransformTypeOptions"
                style="width:110px"
              />
              <n-auto-complete
                v-model:value="t.key"
                :options="headerKeyOptions"
                placeholder="请求头名称"
                style="width:180px"
                :get-show="() => true"
              />
              <n-select
                v-if="t.type !== 'remove' && t.key === 'Content-Type'"
                v-model:value="t.value"
                :options="contentTypeOptions"
                tag
                placeholder="选择或输入 Content-Type"
                style="width:240px"
              />
              <n-input
                v-else-if="t.type !== 'remove'"
                v-model:value="t.value"
                placeholder="值"
                style="width:240px"
              />
              <n-button size="small" type="error" circle @click="removeHeaderTransform(i)">×</n-button>
            </n-space>
            <n-button size="small" dashed @click="addHeaderTransform">+ 自定义请求头</n-button>
          </n-space>
        </n-form-item>
        <!-- P1: 失败重试 -->
        <n-form-item label="失败重试">
          <n-space align="center">
            <n-input-number v-model:value="form.retry_count" :min="0" :max="5" />
            <span style="color:#666;font-size:13px">
              回放失败的请求自动重试 N 次，减少网络抖动导致的误报
            </span>
          </n-space>
        </n-form-item>
        <n-form-item label="忽略字段">
          <n-space vertical style="width:100%">
            <n-dynamic-tags v-model:value="form.ignore_fields" />
            <n-space>
              <n-button
                size="small"
                :loading="suggesting"
                :disabled="!form.case_id"
                @click="suggestFields"
              >
                推荐忽略字段
              </n-button>
              <span style="color:#999;font-size:12px">分析该用例的录制，推荐动态字段（需同一接口有 ≥2 条录制）</span>
            </n-space>
            <n-alert v-if="suggestResult" type="info" closable @close="suggestResult = null" style="font-size:12px">
              分析了 {{ suggestResult.analyzed_paths }}/{{ suggestResult.total_paths }} 个路径。
              <span v-if="suggestResult.suggested_fields.length">
                建议忽略：<b>{{ suggestResult.suggested_fields.join(', ') }}</b>
                <n-button size="tiny" style="margin-left:8px" @click="applyAll">全部添加</n-button>
              </span>
              <span v-else>未发现动态字段（录制数据可能已经足够稳定）。</span>
            </n-alert>
          </n-space>
        </n-form-item>

        <!-- Smart Diff Rules -->
        <n-form-item label="差异规则">
          <n-space vertical style="width:100%">
            <n-space v-for="(rule, i) in form.diff_rules" :key="i" align="center" wrap>
              <n-select
                v-model:value="rule.type"
                :options="diffRuleTypeOptions"
                style="width:160px"
              />
              <n-input v-model:value="rule.path" placeholder="字段路径，如 data.price" style="width:200px" />
              <n-input-number
                v-if="rule.type === 'numeric_tolerance'"
                v-model:value="rule.tolerance"
                :step="0.01" :min="0"
                placeholder="容差"
                style="width:110px"
              />
              <n-input
                v-if="rule.type === 'regex_match'"
                v-model:value="rule.pattern"
                placeholder="正则表达式"
                style="width:160px"
              />
              <n-button size="small" type="error" circle @click="removeDiffRule(i)">×</n-button>
            </n-space>
            <n-button size="small" dashed @click="addDiffRule">+ 添加差异规则</n-button>
            <span style="color:#999;font-size:12px">
              ignore=忽略字段 &nbsp; numeric_tolerance=数值容差 &nbsp; regex_match=正则匹配 &nbsp; type_only=仅比较类型
            </span>
          </n-space>
        </n-form-item>

        <!-- Assertion Rules -->
        <n-form-item label="断言规则">
          <n-space vertical style="width:100%">
            <n-space v-for="(rule, i) in form.assertions" :key="i" align="center" wrap>
              <n-select
                v-model:value="rule.type"
                :options="assertionTypeOptions"
                style="width:180px"
              />
              <n-input
                v-if="needsPath(rule.type)"
                v-model:value="rule.path"
                placeholder="JSON 路径，如 code"
                style="width:160px"
              />
              <n-input
                v-if="needsValue(rule.type)"
                v-model:value="(rule as any).value"
                :placeholder="rule.type === 'status_code_eq' ? '如 200' : '期望值'"
                style="width:140px"
              />
              <n-input
                v-if="rule.type === 'json_path_regex'"
                v-model:value="rule.pattern"
                placeholder="正则表达式"
                style="width:150px"
              />
              <n-button size="small" type="error" circle @click="removeAssertion(i)">×</n-button>
            </n-space>
            <n-button size="small" dashed @click="addAssertion">+ 添加断言规则</n-button>
            <span style="color:#999;font-size:12px">
              断言失败时结果标记为 FAIL（即使响应体与录制一致）
            </span>
          </n-space>
        </n-form-item>

        <n-form-item>
          <n-space>
            <n-button type="primary" :loading="submitting" @click="startReplay">
              开始回放
            </n-button>
            <n-button
              :disabled="!form.target_app_id"
              :loading="loadingDefaults"
              @click="loadAppDefaults"
            >
              加载应用默认配置
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>

    <n-space vertical :size="12" style="margin-top: 16px">
      <n-text depth="3" style="font-size: 13px">
        查看回放历史：
        <n-a @click="router.push('/replay-history')">回放历史页面</n-a>
      </n-text>
    </n-space>
  </n-space>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NCard, NSpace, NForm, NFormItem, NSelect, NInput, NInputNumber,
  NButton, NDynamicTags, NAlert, NSwitch, NText, NA, NTag, NAutoComplete, useMessage,
} from 'naive-ui'
import { replayApi, type DiffRule, type AssertionRule } from '@/api/replays'
import { fmtTime } from '@/utils/time'
import { testCaseApi } from '@/api/testCases'
import { applicationApi } from '@/api/applications'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const notifyOptions = [
  { label: '通用 JSON', value: 'generic' },
  { label: '钉钉 Webhook', value: 'dingtalk' },
  { label: '企业微信', value: 'wecom' },
]

const form = ref({
  case_id: (route.query.case_id as string) || '',
  target_app_id: '',
  environment: '',
  override_host: '',
  webhook_url: '',
  notify_type: undefined as string | undefined,
  concurrency: 1,
  delay_ms: 0,
  perf_threshold_ms: undefined as number | undefined,
  use_sub_invocation_mocks: false,
  // P0: 智能降噪
  smart_noise_reduction: false,
  // P0: 流量放大
  repeat_count: 1,
  // P1: 请求头转换
  header_transforms: [] as { type: 'replace' | 'remove' | 'add'; key: string; value?: string }[],
  // P1: 失败重试
  retry_count: 0,
  ignore_fields: [] as string[],
  diff_rules: [] as DiffRule[],
  assertions: [] as AssertionRule[],
})

const diffRuleTypeOptions = [
  { label: '忽略字段 (ignore)', value: 'ignore' },
  { label: '数值容差 (numeric_tolerance)', value: 'numeric_tolerance' },
  { label: '正则匹配 (regex_match)', value: 'regex_match' },
  { label: '仅比较类型 (type_only)', value: 'type_only' },
]

const assertionTypeOptions = [
  { label: 'HTTP状态码等于', value: 'status_code_eq' },
  { label: '响应体不为空', value: 'response_not_empty' },
  { label: 'JSON字段等于', value: 'json_path_eq' },
  { label: 'JSON字段包含', value: 'json_path_contains' },
  { label: 'JSON字段存在', value: 'json_path_exists' },
  { label: 'JSON字段匹配正则', value: 'json_path_regex' },
  { label: '差异分数不超过', value: 'diff_score_lte' },
]

const headerTransformTypeOptions = [
  { label: '替换', value: 'replace' },
  { label: '删除', value: 'remove' },
  { label: '添加', value: 'add' },
]

// 常用 Content-Type 下拉选项
const contentTypeOptions = [
  { label: 'application/xml', value: 'application/xml' },
  { label: 'application/json', value: 'application/json' },
  { label: 'text/xml; charset=UTF-8', value: 'text/xml; charset=UTF-8' },
  { label: 'application/x-www-form-urlencoded', value: 'application/x-www-form-urlencoded' },
  { label: 'multipart/form-data', value: 'multipart/form-data' },
  { label: 'text/plain', value: 'text/plain' },
]

// 请求头名称自动完成候选
const headerKeyOptions = [
  'Content-Type', 'Accept', 'Authorization', 'Host', 'X-Forwarded-For',
  'X-Real-IP', 'User-Agent', 'Referer', 'Origin', 'Cookie',
  'X-Request-ID', 'X-Trace-ID', 'X-App-ID', 'X-Token',
].map(k => ({ label: k, value: k }))

// 快速添加预设
const headerPresets: { label: string; type: 'replace' | 'remove' | 'add'; key: string; value: string; tagType: 'info' | 'success' | 'warning' }[] = [
  { label: 'Content-Type: application/xml',  type: 'replace', key: 'Content-Type', value: 'application/xml',  tagType: 'info' },
  { label: 'Content-Type: application/json', type: 'replace', key: 'Content-Type', value: 'application/json', tagType: 'info' },
  { label: 'Content-Type: text/xml',         type: 'replace', key: 'Content-Type', value: 'text/xml; charset=UTF-8', tagType: 'info' },
  { label: 'Accept: application/json',       type: 'replace', key: 'Accept',       value: 'application/json', tagType: 'success' },
  { label: 'Accept: application/xml',        type: 'replace', key: 'Accept',       value: 'application/xml',  tagType: 'success' },
  { label: '移除 Authorization',             type: 'remove',  key: 'Authorization', value: '',                tagType: 'warning' },
  { label: '移除 Cookie',                    type: 'remove',  key: 'Cookie',        value: '',                tagType: 'warning' },
]

function addPresetTransform(preset: typeof headerPresets[0]) {
  // 同 key + 同 type 的已存在则覆盖，避免重复添加
  const existing = form.value.header_transforms.find(
    t => t.key === preset.key && t.type === preset.type
  )
  if (existing) {
    existing.value = preset.value
  } else {
    form.value.header_transforms.push({ type: preset.type, key: preset.key, value: preset.value })
  }
}

function needsPath(type: string) {
  return ['json_path_eq', 'json_path_contains', 'json_path_exists', 'json_path_regex'].includes(type)
}

function needsValue(type: string) {
  return ['status_code_eq', 'json_path_eq', 'json_path_contains', 'diff_score_lte'].includes(type)
}

function addDiffRule() {
  form.value.diff_rules.push({ type: 'ignore', path: '' })
}

function removeDiffRule(i: number) {
  form.value.diff_rules.splice(i, 1)
}

function addAssertion() {
  form.value.assertions.push({ type: 'response_not_empty' } as AssertionRule)
}

function removeAssertion(i: number) {
  form.value.assertions.splice(i, 1)
}

function addHeaderTransform() {
  form.value.header_transforms.push({ type: 'replace', key: '', value: '' })
}

function removeHeaderTransform(i: number) {
  form.value.header_transforms.splice(i, 1)
}

const caseOptions = ref<{ label: string; value: string }[]>([])
const appOptions = ref<{ label: string; value: string }[]>([])
const appMap = ref<Record<string, any>>({})
const caseRecordingCount = ref<Record<string, number>>({})
const submitting = ref(false)

const loadingDefaults = ref(false)
const suggesting = ref(false)
const suggestResult = ref<{
  suggested_fields: string[]
  details: { field: string; paths_affected: number }[]
  analyzed_paths: number
  total_paths: number
} | null>(null)

async function loadAppDefaults() {
  if (!form.value.target_app_id) return
  loadingDefaults.value = true
  try {
    const app = appMap.value[form.value.target_app_id]
    if (!app) return
    form.value.ignore_fields = []
    form.value.diff_rules = []
    form.value.assertions = []
    form.value.perf_threshold_ms = undefined
    if (app.default_ignore_fields?.length) form.value.ignore_fields = [...app.default_ignore_fields]
    if (app.default_diff_rules?.length) form.value.diff_rules = app.default_diff_rules as DiffRule[]
    if (app.default_assertions?.length) form.value.assertions = app.default_assertions as AssertionRule[]
    if (app.default_perf_threshold_ms != null) form.value.perf_threshold_ms = app.default_perf_threshold_ms
    message.success('已加载应用默认配置')
  } finally {
    loadingDefaults.value = false
  }
}

function onTargetAppChange() {
  suggestResult.value = null
}

async function suggestFields() {
  if (!form.value.case_id) return
  suggesting.value = true
  suggestResult.value = null
  try {
    const res = await testCaseApi.suggestIgnore(form.value.case_id)
    suggestResult.value = res.data
    if (!res.data.suggested_fields.length) {
      message.info('未发现动态字段，当前录制数据较为稳定')
    }
  } catch (e: any) {
    message.error(e.response?.data?.detail || '分析失败')
  } finally {
    suggesting.value = false
  }
}

function applyAll() {
  if (!suggestResult.value) return
  const existing = new Set(form.value.ignore_fields)
  let added = 0
  for (const f of suggestResult.value.suggested_fields) {
    if (!existing.has(f)) {
      form.value.ignore_fields.push(f)
      added++
    }
  }
  message.success(added > 0 ? `已添加 ${added} 个字段` : '字段已全部存在，无需重复添加')
  suggestResult.value = null
}

async function startReplay() {
  if (!form.value.case_id || !form.value.target_app_id) {
    message.warning('请选择测试用例和目标应用')
    return
  }
  if ((caseRecordingCount.value[form.value.case_id] ?? 0) === 0) {
    message.warning('该测试用例还没有添加任何录制接口，请先在测试用例库中添加录制后再回放')
    return
  }
  submitting.value = true
  try {
    const payload = { ...form.value }
    if (!payload.override_host) delete (payload as any).override_host
    if (!payload.environment) delete (payload as any).environment
    if (!payload.webhook_url) delete (payload as any).webhook_url
    if (!payload.notify_type) delete (payload as any).notify_type
    if (!payload.ignore_fields?.length) delete (payload as any).ignore_fields
    if (!payload.diff_rules?.length) delete (payload as any).diff_rules
    if (!payload.assertions?.length) delete (payload as any).assertions
    if (!payload.perf_threshold_ms) delete (payload as any).perf_threshold_ms
    // P0-P1 新字段
    if (!payload.smart_noise_reduction) delete (payload as any).smart_noise_reduction
    if (payload.repeat_count === 1) delete (payload as any).repeat_count
    if (!payload.header_transforms?.length) delete (payload as any).header_transforms
    if (!payload.retry_count) delete (payload as any).retry_count
    const res = await replayApi.create(payload)
    message.success(`回放任务已创建: ${fmtTime(res.data.created_at)}，可前往「回放历史」查看进度`)
  } catch (e: any) {
    message.error(e.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    testCaseApi.listAll().then(items => {
      caseOptions.value = items.map(c => ({ label: c.name, value: c.id }))
      caseRecordingCount.value = Object.fromEntries(items.map(c => [c.id, c.recording_count]))
    }).catch(() => {}),
    applicationApi.list().then(appsRes => {
      appOptions.value = appsRes.data.map(a => ({ label: a.name, value: a.id }))
      appMap.value = Object.fromEntries(appsRes.data.map(a => [a.id, a]))
    }).catch(() => {}),
  ])
})
</script>
 
