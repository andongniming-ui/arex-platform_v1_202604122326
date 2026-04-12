<template>
  <n-space vertical :size="16">
    <n-alert type="info" title="平台指引">
      这是给新人和首次接入同学准备的入口页。建议先看“菜单速览”和“新人推荐流程”，再去各功能菜单实际操作。
    </n-alert>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="平台定位" class="hero-card">
          <n-space vertical :size="12">
            <n-alert type="info">
              这是一个“真实流量录制 -> 回放验证 -> 差异分析 -> 回归固化”的平台，适合新人先从这里建立整体认知。
            </n-alert>
            <n-space wrap>
              <n-tag type="success">JDK8</n-tag>
              <n-tag type="success">XML / JSON</n-tag>
              <n-tag type="success">MySQL / MyBatis</n-tag>
              <n-tag type="success">回放 / 对比 / CI</n-tag>
            </n-space>
            <n-text depth="3">
              平台不替代业务测试，它的价值在于把真实样本沉淀下来，用来做版本回归、环境一致性检查和发布门禁。
            </n-text>
          </n-space>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="关键配置说明" class="hero-card">
          <n-descriptions bordered :column="1">
            <n-descriptions-item v-for="item in configItems" :key="item.label" :label="item.label">
              <n-text code>{{ item.key }}</n-text>
              <span class="config-desc">{{ item.desc }}</span>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="菜单速览" class="section-card">
      <div class="menu-grid">
        <div v-for="item in menuCards" :key="item.title" class="menu-card">
          <div class="menu-title-row">
            <div class="menu-title">{{ item.title }}</div>
            <n-button text type="primary" @click="router.push(item.path)">进入</n-button>
          </div>
          <div class="menu-scene">{{ item.scene }}</div>
          <div class="menu-desc">{{ item.desc }}</div>
        </div>
      </div>
    </n-card>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="新人推荐流程" class="section-card">
          <div class="workflow-list">
            <div v-for="item in workflows" :key="item.title" class="workflow-item">
              <span class="workflow-index">{{ item.index }}</span>
              <div>
                <div class="workflow-title">{{ item.title }}</div>
                <div class="workflow-desc">{{ item.desc }}</div>
              </div>
            </div>
          </div>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="发布前回归检查" class="section-card">
          <div class="checklist">
            <div v-for="item in releaseChecklist" :key="item" class="check-item">
              <span class="check-dot"></span>
              <span>{{ item }}</span>
            </div>
          </div>
          <n-alert type="warning" style="margin-top: 16px">
            详细步骤见仓库根目录文档：<n-text code>发布前回归SOP.md</n-text>
          </n-alert>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="常见建议" class="section-card">
          <div class="checklist">
            <div v-for="item in tips" :key="item" class="check-item">
              <span class="check-dot check-dot--green"></span>
              <span>{{ item }}</span>
            </div>
          </div>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="快捷入口" class="section-card">
          <n-space wrap>
            <n-button type="primary" @click="router.push('/applications')">应用管理</n-button>
            <n-button @click="router.push('/recording')">录制会话</n-button>
            <n-button @click="router.push('/test-cases')">测试用例</n-button>
            <n-button @click="router.push('/replay')">发起回放</n-button>
            <n-button @click="router.push('/replay-history')">回放历史</n-button>
            <n-button @click="router.push('/compare')">双环境对比</n-button>
            <n-button @click="router.push('/ci')">CI 集成</n-button>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-space>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  NAlert,
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NGrid,
  NGridItem,
  NSpace,
  NTag,
  NText,
} from 'naive-ui'

const router = useRouter()

const configItems = [
  { label: 'AREX Storage', key: 'AP_AREX_STORAGE_URL', desc: '后端访问 arex-storage 的地址，通常指向 8093。' },
  { label: '数据库类型', key: 'AP_DB_TYPE', desc: '可选 sqlite / mysql。小规模试用可先用 sqlite。' },
  { label: '数据库连接', key: 'AP_DB_URL', desc: '建议使用完整连接串，避免环境切换时产生歧义。' },
  { label: 'Agent JAR', key: 'AP_AREX_AGENT_JAR_PATH', desc: '应用自动挂载 agent 时使用的本地 JAR 路径。' },
  { label: 'Agent 回连地址', key: 'AP_AREX_AGENT_STORAGE_URL', desc: '目标 JVM 能访问到的 arex-storage 地址。' },
]

const menuCards = [
  { title: '数据总览', path: '/dashboard', scene: '先看平台是否稳定', desc: '查看最近回放趋势、通过率和失败波动，适合发布前先整体摸底。' },
  { title: '应用管理', path: '/applications', scene: '新系统首次接入', desc: '配置应用名称、SSH、端口、Agent、默认回放规则和 XML 模板。' },
  { title: '录制会话', path: '/recording', scene: '采集和筛选样本', desc: '查看录制会话、过滤录制条目、导入 HAR，并把关键录制沉淀到用例。' },
  { title: '测试用例库', path: '/test-cases', scene: '沉淀长期资产', desc: '管理测试用例，编辑请求体、克隆用例、推荐忽略字段。' },
  { title: '发起回放', path: '/replay', scene: '执行单次验证', desc: '配置目标应用、并发、差异规则、断言和 mock 方式，发起回放。' },
  { title: '回放历史', path: '/replay-history', scene: '追踪历史结果', desc: '查看历史任务、进入结果详情页、观察状态和通过率。' },
  { title: '定时回放', path: '/schedules', scene: '做巡检', desc: '创建 Cron 任务，按天或按小时做自动回归。' },
  { title: '回放套件', path: '/suites', scene: '发布前批量回归', desc: '把多条测试用例打成一批统一执行，适合核心路径打包验证。' },
  { title: '双环境对比', path: '/compare', scene: '比较两个环境', desc: '同一批录制同时打到两个环境，分析行为差异。' },
  { title: 'CI 集成', path: '/ci', scene: '接入流水线', desc: '把关键用例做成阻塞式回放门禁，用于 Jenkins 或 GitLab CI。' },
  { title: '平台指引', path: '/settings', scene: '新人入口页', desc: '集中看项目定位、推荐流程、配置说明和回归检查要点。' },
]

const workflows = [
  { index: '01', title: '接入应用', desc: '先在应用管理里配置 SSH、端口、JAR、Agent，再确认应用名与 Arex.service.name 一致。' },
  { index: '02', title: '开始录制', desc: '在录制会话页创建会话，在业务系统做真实操作，录完后回平台筛选有效样本。' },
  { index: '03', title: '沉淀用例', desc: '把关键录制加入测试用例，必要时编辑请求体、补 XML 模板、配置忽略字段。' },
  { index: '04', title: '执行回放', desc: '在发起回放页指定目标环境，设置并发、差异规则、断言和性能阈值。' },
  { index: '05', title: '查看结果', desc: '到回放历史和结果详情页看通过率、失败分类、Diff 明细和报告。' },
  { index: '06', title: '固化巡检', desc: '稳定后把关键用例接入定时回放、回放套件或 CI 流水线。' },
]

const releaseChecklist = [
  '先看数据总览，确认最近平台本身没有大面积异常。',
  '确认目标应用配置正确，必要时先做一次 SSH、Agent、PID 检查。',
  '选择核心测试用例或回放套件，不要把无效样本混进发布回归。',
  'XML 接口优先确认 request_body 是否完整，必要时补 xml_request_template。',
  '先看通过率，再逐条看失败分类，避免只盯着单个接口。',
  '关键失败要进入结果详情页看 Diff，不要只看状态颜色。',
  '发布门禁场景优先接 CI 集成，不要依赖人工口头确认。',
]

const tips = [
  '先把应用级默认忽略字段和差异规则配好，再做批量回放。',
  '录制会话尽量使用统一命名，方便后续定位问题和复盘。',
  'CI 阈值建议先从 0.9 起步，稳定后再逐步收紧到 1.0。',
  '双环境对比适合做上线前一致性检查，不建议替代常规回放。',
]
</script>

<style scoped>
.hero-card {
  min-height: 100%;
}

.section-card {
  border-radius: 20px;
}

.config-desc {
  margin-left: 8px;
  color: #52607a;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}

.menu-card {
  padding: 16px;
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.menu-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.menu-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.menu-scene {
  margin-top: 8px;
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 700;
}

.menu-desc {
  margin-top: 8px;
  color: #52607a;
  line-height: 1.7;
}

.workflow-list {
  display: grid;
  gap: 14px;
}

.workflow-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 14px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(31, 111, 235, 0.08), rgba(22, 163, 74, 0.05));
}

.workflow-index {
  min-width: 42px;
  height: 42px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.workflow-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 4px;
}

.workflow-desc {
  color: #52607a;
  line-height: 1.6;
}

.checklist {
  display: grid;
  gap: 12px;
}

.check-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: #334155;
  line-height: 1.7;
}

.check-dot {
  width: 8px;
  height: 8px;
  margin-top: 8px;
  border-radius: 999px;
  background: #f59e0b;
  flex: 0 0 auto;
}

.check-dot--green {
  background: #16a34a;
}
</style>
