<template>
  <n-space vertical :size="16">
    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="CI 集成中心">
          <n-space vertical :size="12">
            <n-alert type="info">
              这部分借用了 `arex-recorder` 的 CI 使用方式，但适配到了当前平台已有的阻塞式回放接口。
            </n-alert>
            <n-text depth="3">
              适合 Jenkins、GitLab CI 或本地脚本直接触发单用例回放，并在流水线内同步拿到通过/失败结果。
            </n-text>
            <n-space>
              <n-button @click="router.push('/test-cases')">查看测试用例</n-button>
              <n-button @click="router.push('/applications')">查看应用</n-button>
              <n-button @click="copyCurl">复制 cURL</n-button>
            </n-space>
          </n-space>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="接入步骤">
          <n-space vertical :size="10">
            <div class="step-item"><span class="step-index">1</span><span>选择一个已有测试用例和目标应用。</span></div>
            <div class="step-item"><span class="step-index">2</span><span>按需设置阈值、并发、延迟和超时。</span></div>
            <div class="step-item"><span class="step-index">3</span><span>在页面执行验证，确认参数符合预期。</span></div>
            <div class="step-item"><span class="step-index">4</span><span>复制下方 cURL 到流水线脚本中使用。</span></div>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="回放参数">
      <n-form :model="form" label-placement="top">
        <n-grid :cols="2" :x-gap="16" responsive="screen">
          <n-grid-item>
            <n-form-item label="测试用例">
              <n-select
                v-model:value="form.case_id"
                filterable
                :options="caseOptions"
                placeholder="选择测试用例"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="目标应用">
              <n-select
                v-model:value="form.target_app_id"
                filterable
                :options="appOptions"
                placeholder="选择目标应用"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="通过阈值">
              <n-input-number v-model:value="form.pass_threshold" :min="0" :max="1" :step="0.05" style="width: 100%" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="超时时间(秒)">
              <n-input-number v-model:value="form.timeout_seconds" :min="10" :max="1800" style="width: 100%" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="并发数">
              <n-input-number v-model:value="form.concurrency" :min="1" :max="20" style="width: 100%" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="请求间隔(ms)">
              <n-input-number v-model:value="form.delay_ms" :min="0" :max="10000" style="width: 100%" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="运行环境标识">
              <n-input v-model:value="form.environment" placeholder="默认 ci" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="覆盖目标 Host">
              <n-input v-model:value="form.override_host" placeholder="可选，例如 10.10.1.15:8080" />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-form-item label="忽略字段">
          <n-dynamic-tags v-model:value="ignoreFields" />
        </n-form-item>

        <n-grid :cols="2" :x-gap="16" responsive="screen">
          <n-grid-item>
            <n-form-item label="Diff 规则(JSON 数组，可选)">
              <n-input
                v-model:value="diffRulesText"
                type="textarea"
                :rows="6"
                placeholder='例如: [{"path":"$.data.amount","operator":"tolerance","value":0.01}]'
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="断言规则(JSON 数组，可选)">
              <n-input
                v-model:value="assertionsText"
                type="textarea"
                :rows="6"
                placeholder='例如: [{"path":"$.code","operator":"eq","expected":"200"}]'
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-space>
          <n-button type="primary" :loading="running" @click="runReplay">执行 CI 回放</n-button>
          <n-button @click="copyCurl">复制 cURL</n-button>
        </n-space>
      </n-form>
    </n-card>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="流水线命令示例">
          <pre class="code-block">{{ curlCommand }}</pre>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="响应结果">
          <n-empty v-if="!result && !running" description="执行一次 CI 回放后，这里会展示结果摘要。" />
          <n-spin :show="running">
            <n-space v-if="result" vertical :size="12">
              <n-space align="center">
                <n-tag :type="result.passed ? 'success' : 'error'" size="large">
                  {{ result.passed ? '通过' : '未通过' }}
                </n-tag>
                <n-tag size="large">{{ result.status }}</n-tag>
              </n-space>
              <n-descriptions bordered :column="2">
                <n-descriptions-item label="任务 ID">{{ result.job_id }}</n-descriptions-item>
                <n-descriptions-item label="耗时">{{ result.duration_seconds }}s</n-descriptions-item>
                <n-descriptions-item label="通过率">{{ toPercent(result.pass_rate) }}</n-descriptions-item>
                <n-descriptions-item label="阈值">{{ toPercent(result.pass_threshold) }}</n-descriptions-item>
                <n-descriptions-item label="通过 / 总数">{{ result.success_count }} / {{ result.total_count }}</n-descriptions-item>
                <n-descriptions-item label="失败 / 错误">{{ result.fail_count }} / {{ result.error_count }}</n-descriptions-item>
              </n-descriptions>
              <n-button
                v-if="result.report_url"
                @click="openReport(result.report_url)"
              >打开 HTML 报告</n-button>
            </n-space>
          </n-spin>
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-space>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NAlert,
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NDynamicTags,
  NEmpty,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NInputNumber,
  NSelect,
  NSpace,
  NSpin,
  NTag,
  NText,
  useMessage,
} from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { ciApi, type CIReplayResponse } from '@/api/ci'
import { testCaseApi } from '@/api/testCases'

type ReplayForm = {
  case_id: string | null
  target_app_id: string | null
  pass_threshold: number
  timeout_seconds: number
  concurrency: number
  delay_ms: number
  override_host: string
  environment: string
}

const router = useRouter()
const message = useMessage()
const running = ref(false)
const result = ref<CIReplayResponse | null>(null)
const appOptions = ref<{ label: string; value: string }[]>([])
const caseOptions = ref<{ label: string; value: string }[]>([])
const ignoreFields = ref<string[]>([])
const diffRulesText = ref('')
const assertionsText = ref('')

const form = ref<ReplayForm>({
  case_id: null,
  target_app_id: null,
  pass_threshold: 1,
  timeout_seconds: 300,
  concurrency: 1,
  delay_ms: 0,
  override_host: '',
  environment: 'ci',
})

const requestPayload = computed(() => ({
  case_id: form.value.case_id,
  target_app_id: form.value.target_app_id,
  ignore_fields: ignoreFields.value.length ? ignoreFields.value : undefined,
  diff_rules: parseJsonArray(diffRulesText.value),
  assertions: parseJsonArray(assertionsText.value),
  pass_threshold: form.value.pass_threshold,
  timeout_seconds: form.value.timeout_seconds,
  concurrency: form.value.concurrency,
  delay_ms: form.value.delay_ms,
  override_host: form.value.override_host.trim() || undefined,
  environment: form.value.environment.trim() || undefined,
}))

const curlCommand = computed(() => {
  const payload = JSON.stringify(requestPayload.value, null, 2)
  return [
    `curl -X POST ${window.location.origin}/api/v1/ci/replay \\`,
    '  -H "Content-Type: application/json" \\',
    `  -d '${payload}'`,
  ].join('\n')
})

function parseJsonArray(text: string) {
  if (!text.trim()) return undefined
  try {
    const parsed = JSON.parse(text)
    return Array.isArray(parsed) ? parsed : undefined
  } catch {
    return undefined
  }
}

function toPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`
}

async function copyCurl() {
  try {
    await navigator.clipboard.writeText(curlCommand.value)
    message.success('cURL 已复制')
  } catch {
    message.error('复制失败，请手动复制')
  }
}

function openReport(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer')
}

function validatePayload() {
  if (!form.value.case_id) {
    message.warning('请选择测试用例')
    return false
  }
  if (!form.value.target_app_id) {
    message.warning('请选择目标应用')
    return false
  }
  if (diffRulesText.value.trim() && parseJsonArray(diffRulesText.value) === undefined) {
    message.warning('Diff 规则必须是合法的 JSON 数组')
    return false
  }
  if (assertionsText.value.trim() && parseJsonArray(assertionsText.value) === undefined) {
    message.warning('断言规则必须是合法的 JSON 数组')
    return false
  }
  return true
}

async function runReplay() {
  if (!validatePayload()) return
  running.value = true
  try {
    const res = await ciApi.replay(requestPayload.value as any)
    result.value = res.data
    message.success(res.data.passed ? 'CI 回放通过' : 'CI 回放未通过')
  } catch (error: any) {
    result.value = null
    const detail = error.response?.data?.detail
    if (typeof detail === 'object' && detail?.message) {
      message.error(`${detail.message}，job_id=${detail.job_id || '-'}`)
    } else {
      message.error(detail || 'CI 回放执行失败')
    }
  } finally {
    running.value = false
  }
}

onMounted(async () => {
  const [appsRes, casesRes] = await Promise.all([
    applicationApi.list(),
    testCaseApi.listAll(),
  ])

  appOptions.value = appsRes.data.map(app => ({
    label: app.name,
    value: app.id,
  }))

  caseOptions.value = casesRes.map(item => ({
    label: `${item.name} (${item.recording_count} 条录制)`,
    value: item.id,
  }))
})
</script>

<style scoped>
.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-index {
  width: 24px;
  height: 24px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #1f6feb;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.code-block {
  margin: 0;
  padding: 16px;
  border-radius: 14px;
  background: #0f172a;
  color: #dbeafe;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
