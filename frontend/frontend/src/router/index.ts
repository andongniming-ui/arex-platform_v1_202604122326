import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/applications',
    },
    {
      path: '/applications',
      component: () => import('@/views/applications/ApplicationList.vue'),
    },
    {
      path: '/applications/:id',
      component: () => import('@/views/applications/ApplicationDetail.vue'),
    },
    {
      path: '/recording',
      component: () => import('@/views/recording/RecordingCenter.vue'),
    },
    {
      path: '/recording/sessions/:id',
      component: () => import('@/views/recording/SessionDetail.vue'),
    },
    {
      path: '/recordings/:id',
      component: () => import('@/views/recording/RecordingDetail.vue'),
    },
    {
      path: '/test-cases',
      component: () => import('@/views/testcases/TestCaseLibrary.vue'),
    },
    {
      path: '/test-cases/:id',
      component: () => import('@/views/testcases/TestCaseDetail.vue'),
    },
    {
      path: '/replay',
      component: () => import('@/views/replay/ReplayCenter.vue'),
    },
    {
      path: '/replay-history',
      component: () => import('@/views/replay/ReplayHistory.vue'),
    },
    {
      path: '/replay/:jobId',
      component: () => import('@/views/replay/ReplayJobDetail.vue'),
    },
    {
      path: '/results/:jobId',
      component: () => import('@/views/results/ResultOverview.vue'),
    },
    {
      path: '/dashboard',
      component: () => import('@/views/dashboard/Dashboard.vue'),
    },
    {
      path: '/ci',
      component: () => import('@/views/dashboard/CIHub.vue'),
    },
    {
      path: '/settings',
      component: () => import('@/views/dashboard/SettingsCenter.vue'),
    },
    {
      path: '/schedules',
      component: () => import('@/views/schedule/ScheduleCenter.vue'),
    },
    {
      path: '/suites',
      component: () => import('@/views/suites/SuiteCenter.vue'),
    },
    {
      path: '/compare',
      component: () => import('@/views/compare/CompareCenter.vue'),
    },
  ],
})

export default router
