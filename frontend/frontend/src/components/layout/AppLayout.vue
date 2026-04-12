<template>
  <n-layout class="app-shell" has-sider>
    <div class="shell-bg shell-bg--left"></div>
    <div class="shell-bg shell-bg--right"></div>

    <n-layout-sider
      class="app-sider"
      collapse-mode="width"
      :collapsed-width="72"
      :width="252"
      :collapsed="collapsed"
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="brand" @click="collapsed = !collapsed">
        <div class="brand-mark">AR</div>
        <div v-if="!collapsed" class="brand-copy">
          <div class="brand-title">AREX Platform V1</div>
          <div class="brand-subtitle">录制、回放、对比</div>
        </div>
      </div>

      <div v-if="!collapsed" class="brand-panel">
        <div class="brand-panel__label">当前页面</div>
        <div class="brand-panel__value">{{ pageTitle }}</div>
        <div class="brand-panel__meta">{{ todayLabel }}</div>
      </div>

      <n-menu
        class="side-menu"
        :collapsed="collapsed"
        :collapsed-width="72"
        :collapsed-icon-size="20"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleNav"
      />
    </n-layout-sider>

    <n-layout class="app-main">
      <div class="topbar">
        <div>
          <div class="topbar-title">{{ pageTitle }}</div>
          <div class="topbar-subtitle">面向录制回放验证、双环境差异检查和发布前回归</div>
        </div>
        <n-space align="center" size="small">
          <div class="topbar-date">{{ todayLabel }}</div>
          <n-button v-if="route.path !== '/dashboard'" quaternary size="small" @click="router.push('/dashboard')">总览</n-button>
          <n-button v-if="route.path !== '/settings'" quaternary size="small" @click="router.push('/settings')">指引</n-button>
        </n-space>
      </div>

      <n-layout-content content-style="padding: 0 24px 24px; min-height: 100vh">
        <div class="content-shell">
          <slot />
        </div>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, h, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NButton, NLayout, NLayoutContent, NLayoutSider, NMenu, NSpace } from 'naive-ui'
import type { MenuOption } from 'naive-ui'

const collapsed = ref(false)
const router = useRouter()
const route = useRoute()

const activeKey = computed(() => {
  const p = route.path
  if (p.startsWith('/dashboard')) return 'dashboard'
  if (p.startsWith('/applications')) return 'applications'
  if (p.startsWith('/recording')) return 'recording'
  if (p.startsWith('/test-cases')) return 'test-cases'
  if (p === '/replay') return 'replay'
  if (p.startsWith('/replay-history') || p.startsWith('/results') || p.startsWith('/replay/')) return 'replay-history'
  if (p.startsWith('/schedules')) return 'schedules'
  if (p.startsWith('/suites')) return 'suites'
  if (p.startsWith('/compare')) return 'compare'
  if (p.startsWith('/ci')) return 'ci'
  if (p.startsWith('/settings')) return 'settings'
  return 'applications'
})

const pageTitleMap: Record<string, string> = {
  dashboard: '数据总览',
  applications: '应用管理',
  recording: '录制会话',
  'test-cases': '测试用例库',
  replay: '发起回放',
  'replay-history': '回放历史',
  schedules: '定时回放',
  suites: '回放套件',
  compare: '双环境对比',
  ci: 'CI 集成',
  settings: '平台指引',
}

const pageTitle = computed(() => pageTitleMap[activeKey.value] || '录制回放平台')

const todayLabel = computed(() => {
  const now = new Date()
  const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const mm = String(now.getMonth() + 1).padStart(2, '0')
  const dd = String(now.getDate()).padStart(2, '0')
  return `${mm}/${dd} ${week[now.getDay()]}`
})

const menuOptions: MenuOption[] = [
  { label: '数据总览', key: 'dashboard', icon: () => h('span', '概') },
  { label: '应用管理', key: 'applications', icon: () => h('span', '应') },
  { label: '录制会话', key: 'recording', icon: () => h('span', '录') },
  { label: '测试用例库', key: 'test-cases', icon: () => h('span', '例') },
  { label: '发起回放', key: 'replay', icon: () => h('span', '回') },
  { label: '回放历史', key: 'replay-history', icon: () => h('span', '史') },
  { label: '定时回放', key: 'schedules', icon: () => h('span', '定') },
  { label: '回放套件', key: 'suites', icon: () => h('span', '套') },
  { label: '双环境对比', key: 'compare', icon: () => h('span', '比') },
  { label: 'CI 集成', key: 'ci', icon: () => h('span', 'CI') },
  { label: '平台指引', key: 'settings', icon: () => h('span', '指') },
]

function handleNav(key: string) {
  router.push('/' + key)
}
</script>

<style scoped>
.app-shell {
  position: relative;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(225, 109, 71, 0.16), transparent 28%),
    radial-gradient(circle at bottom right, rgba(26, 115, 232, 0.14), transparent 30%),
    linear-gradient(180deg, #f7f2ea 0%, #f4f7fb 52%, #eef3f8 100%);
}

.shell-bg {
  position: fixed;
  pointer-events: none;
  border-radius: 999px;
  filter: blur(12px);
  opacity: 0.6;
}

.shell-bg--left {
  top: -64px;
  left: -80px;
  width: 260px;
  height: 260px;
  background: rgba(225, 109, 71, 0.16);
}

.shell-bg--right {
  right: 40px;
  top: 120px;
  width: 220px;
  height: 220px;
  background: rgba(26, 115, 232, 0.12);
}

.app-sider {
  position: relative;
  z-index: 1;
  background: linear-gradient(180deg, #17324d 0%, #0f2437 100%);
  box-shadow: 18px 0 40px rgba(15, 36, 55, 0.12);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 76px;
  padding: 18px 18px 14px;
  cursor: pointer;
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f08a5d 0%, #f6bd60 100%);
  color: #0f2437;
  font-size: 14px;
  font-weight: 800;
}

.brand-copy {
  min-width: 0;
}

.brand-title {
  color: #f8fbff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.brand-subtitle {
  margin-top: 3px;
  color: rgba(226, 236, 247, 0.72);
  font-size: 12px;
}

.brand-panel {
  margin: 2px 16px 14px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.06);
}

.brand-panel__label {
  color: rgba(226, 236, 247, 0.66);
  font-size: 11px;
  letter-spacing: 0.08em;
}

.brand-panel__value {
  margin-top: 8px;
  color: #fff7ef;
  font-size: 18px;
  font-weight: 700;
}

.brand-panel__meta {
  margin-top: 8px;
  color: rgba(226, 236, 247, 0.72);
  font-size: 12px;
}

.side-menu {
  padding: 6px 12px 18px;
}

.app-main {
  position: relative;
  z-index: 1;
  background: transparent;
}

.topbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 18px;
}

.topbar-title {
  color: #102a43;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.topbar-subtitle {
  margin-top: 6px;
  color: #627d98;
  font-size: 13px;
}

.topbar-date {
  padding: 8px 12px;
  border: 1px solid rgba(16, 42, 67, 0.08);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.62);
  color: #243b53;
  font-size: 12px;
  font-weight: 700;
}

.content-shell {
  min-height: calc(100vh - 108px);
}

:deep(.n-menu) {
  background: transparent;
}

:deep(.n-menu .n-menu-item-content) {
  margin-bottom: 6px;
  border-radius: 14px;
  color: rgba(239, 244, 250, 0.92);
}

:deep(.n-menu .n-menu-item-content::before) {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.06);
}

:deep(.n-menu .n-menu-item-content--selected) {
  background: linear-gradient(90deg, rgba(240, 138, 93, 0.92), rgba(246, 189, 96, 0.92));
  color: #102a43;
  font-weight: 700;
}

:deep(.n-menu .n-menu-item-content-header),
:deep(.n-menu .n-menu-item-content__icon),
:deep(.n-menu .n-menu-item-content-arrow) {
  color: inherit;
}

:deep(.n-menu .n-menu-item-content:not(.n-menu-item-content--selected):hover) {
  color: #fffaf2;
}

:deep(.n-menu .n-menu-item-content:not(.n-menu-item-content--selected):hover::before) {
  background: rgba(255, 255, 255, 0.12);
}

:deep(.n-menu .n-menu-item-content--selected .n-menu-item-content-header),
:deep(.n-menu .n-menu-item-content--selected .n-menu-item-content__icon) {
  color: #102a43;
}

:deep(.n-menu .n-menu-item-content-header) {
  font-size: 14px;
  color: inherit;
  opacity: 1;
}

:deep(.n-menu .n-menu-item-content__icon) {
  opacity: 1;
}

:deep(.n-card) {
  border-radius: 20px;
  box-shadow: 0 18px 40px rgba(15, 36, 55, 0.08);
}

@media (max-width: 960px) {
  .topbar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
