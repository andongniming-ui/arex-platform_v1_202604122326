<template>
  <n-card title="测试用例库">
    <template #header-extra>
      <n-space wrap>
        <n-select
          v-model:value="filterAppId"
          :options="appOptions"
          placeholder="按应用筛选"
          clearable
          style="width: 180px"
          @update:value="onFilter"
        />
        <n-input
          v-model:value="filterName"
          placeholder="搜索用例名称"
          clearable
          style="width: 160px"
          @keyup.enter="onFilter"
          @clear="onFilter"
        />
        <n-date-picker
          v-model:value="filterCreatedRange"
          type="datetimerange"
          clearable
          :shortcuts="dateShortcuts"
          style="width: 320px"
          start-placeholder="创建开始时间"
          end-placeholder="创建结束时间"
          @update:value="onFilter"
          @clear="onFilter"
        />
        <n-button @click="clearFilters">清空筛选</n-button>
        <n-button @click="onFilter">搜索</n-button>
        <n-button type="primary" @click="openCreate">+ 新建用例</n-button>
      </n-space>
    </template>

    <span style="color:#999;font-size:13px;margin-right:12px">共 {{ pagination.itemCount }} 条</span>
    <n-data-table
      :columns="columns"
      :data="filteredCases"
      :loading="loading"
      :pagination="pagination"
      :row-key="(r: any) => r.id"
      :checked-row-keys="selectedIds"
      @update:checked-row-keys="selectedIds = $event as string[]"
      @update:sorter="onSorterChange"
    />
    <n-space v-if="selectedIds.length > 0" align="center" style="margin-top:10px">
      <span>已选 {{ selectedIds.length }} 条</span>
      <n-button size="small" type="error" :loading="batchDeleting" @click="deleteSelected">批量删除</n-button>
    </n-space>
  </n-card>

  <n-modal v-model:show="showCreate" preset="dialog" title="新建测试用例" style="width: 480px">
    <n-form :model="form" label-placement="left" label-width="100px">
      <n-form-item label="所属应用" required>
        <n-select
          v-model:value="form.app_id"
          :options="appOptions"
          placeholder="选择被测应用"
        />
      </n-form-item>
      <n-form-item label="用例名称" required>
        <n-input v-model:value="form.name" placeholder="请输入用例名称" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="form.description" type="textarea" :rows="3" placeholder="可选" />
      </n-form-item>
      <n-form-item label="标签">
        <n-dynamic-tags v-model:value="form.tags" />
      </n-form-item>
    </n-form>
    <template #action>
      <n-button @click="showCreate = false">取消</n-button>
      <n-button
        type="primary"
        :loading="saving"
        :disabled="!form.name || !form.app_id"
        @click="handleCreate"
      >创建</n-button>
    </template>
  </n-modal>

  <n-modal v-model:show="showEdit" preset="dialog" title="编辑测试用例" style="width: 480px">
    <n-form :model="editForm" label-placement="left" label-width="100px">
      <n-form-item label="所属应用" required>
        <n-select
          v-model:value="editForm.app_id"
          :options="appOptions"
          placeholder="选择被测应用"
        />
      </n-form-item>
      <n-form-item label="用例名称" required>
        <n-input v-model:value="editForm.name" placeholder="请输入用例名称" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="editForm.description" type="textarea" :rows="3" placeholder="可选" />
      </n-form-item>
      <n-form-item label="标签">
        <n-dynamic-tags v-model:value="editForm.tags" />
      </n-form-item>
    </n-form>
    <template #action>
      <n-button @click="showEdit = false">取消</n-button>
      <n-button
        type="primary"
        :loading="saving"
        :disabled="!editForm.name || !editForm.app_id"
        @click="handleEdit"
      >保存</n-button>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, onBeforeUnmount, h, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NButton, NDataTable, NModal, NForm, NFormItem, NSelect,
  NInput, NDynamicTags, NTag, NSpace, NPopconfirm, NDatePicker, useMessage, useDialog,
} from 'naive-ui'
import { testCaseApi, type TestCase } from '@/api/testCases'
import { applicationApi } from '@/api/applications'
import { usePageSummary } from '@/composables/usePageSummary'
import { fmtTime } from '@/utils/time'
import { createDateShortcuts, type DateRangeValue } from '@/utils/dateRange'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const { setPageSummary, clearPageSummary } = usePageSummary()
const cases = ref<TestCase[]>([])
const loading = ref(false)
const showCreate = ref(false)
const showEdit = ref(false)
const saving = ref(false)
const editingId = ref('')
const editForm = ref({ app_id: '', name: '', description: '', tags: [] as string[] })
const filterAppId = ref<string | null>(null)
const filterName = ref('')
const filterCreatedRange = ref<DateRangeValue>(null)
const selectedIds = ref<string[]>([])
const batchDeleting = ref(false)
const sortOrder = ref<'ascend' | 'descend'>('descend')
const dateShortcuts = createDateShortcuts()

const filteredCases = computed(() => {
  const kw = filterName.value.trim().toLowerCase()
  let list = kw ? cases.value.filter(c => c.name.toLowerCase().includes(kw)) : cases.value
  list = [...list].sort((a, b) => {
    const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    return sortOrder.value === 'ascend' ? diff : -diff
  })
  return list
})

const pagination = reactive({
  itemCount: 0,
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => { pagination.page = page },
  onUpdatePageSize: (size: number) => { pagination.pageSize = size; pagination.page = 1 },
})

const appOptions = ref<{ label: string; value: string }[]>([])
const appMap = ref<Record<string, string>>({})

const emptyForm = () => ({ app_id: '', name: '', description: '', tags: [] as string[] })
const form = ref(emptyForm())

function openCreate() {
  form.value = emptyForm()
  // 如果当前有选中的应用，默认选中它
  if (filterAppId.value) form.value.app_id = filterAppId.value
  showCreate.value = true
}

const columns = computed(() => [
  { type: 'selection' as const, width: 40 },
  { title: '用例名称', key: 'name' },
  {
    title: '所属应用',
    key: 'app_id',
    width: 160,
    render: (r: TestCase) => appMap.value[r.app_id || ''] || r.app_id || '-',
  },
  {
    title: '标签',
    key: 'tags',
    render: (r: TestCase) =>
      h(NSpace, {}, () => (r.tags || []).map(t => h(NTag, { size: 'small' }, () => t))),
  },
  { title: '录制数', key: 'recording_count', width: 80 },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
    sorter: true,
    sortOrder: sortOrder.value,
    render: (r: TestCase) => fmtTime(r.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 290,
    render: (r: TestCase) =>
      h(NSpace, {}, () => [
        h(NButton, { size: 'small', onClick: () => router.push(`/test-cases/${r.id}`) }, () => '详情'),
        h(NButton, {
          size: 'small', type: 'primary',
          onClick: () => router.push(`/replay?case_id=${r.id}`),
        }, () => '回放'),
        h(NButton, { size: 'small', onClick: () => openEdit(r) }, () => '编辑'),
        h(NButton, { size: 'small', onClick: () => handleClone(r.id) }, () => '复制'),
        h(NPopconfirm, { onPositiveClick: () => handleDelete(r.id) }, {
          trigger: () => h(NButton, { size: 'small', type: 'error' }, () => '删除'),
          default: () => '确认删除该用例？',
        }),
      ]),
  },
])

async function load() {
  loading.value = true
  try {
    cases.value = await testCaseApi.listAll({
      app_id: filterAppId.value || undefined,
      created_after: filterCreatedRange.value ? new Date(filterCreatedRange.value[0]).toISOString() : undefined,
      created_before: filterCreatedRange.value ? new Date(filterCreatedRange.value[1]).toISOString() : undefined,
    })
  } finally {
    loading.value = false
  }
}

function onFilter() {
  pagination.page = 1
  load()
}

watch(filteredCases, (list) => {
  pagination.itemCount = list.length
  const maxPage = Math.max(1, Math.ceil(list.length / pagination.pageSize))
  if (pagination.page > maxPage) {
    pagination.page = maxPage
  }
}, { immediate: true })

function clearFilters() {
  filterAppId.value = null
  filterName.value = ''
  filterCreatedRange.value = null
  onFilter()
}

function onSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (sorter?.columnKey === 'created_at') {
    sortOrder.value = sorter.order || 'descend'
  }
}

async function handleCreate() {
  if (!form.value.name || !form.value.app_id) return
  saving.value = true
  try {
    await testCaseApi.create(form.value)
    message.success('用例创建成功')
    showCreate.value = false
    await load()
  } finally {
    saving.value = false
  }
}

function openEdit(r: TestCase) {
  editingId.value = r.id
  editForm.value = {
    app_id: r.app_id || '',
    name: r.name,
    description: r.description || '',
    tags: [...(r.tags || [])],
  }
  showEdit.value = true
}

async function handleEdit() {
  if (!editForm.value.name || !editForm.value.app_id) return
  saving.value = true
  try {
    await testCaseApi.update(editingId.value, {
      name: editForm.value.name,
      description: editForm.value.description,
      app_id: editForm.value.app_id,
      tags: editForm.value.tags,
    })
    message.success('用例已更新')
    showEdit.value = false
    await load()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '更新失败')
  } finally {
    saving.value = false
  }
}

async function handleClone(id: string) {
  try {
    const res = await testCaseApi.clone(id)
    message.success(`已复制为：${res.data.name}`)
    await load()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '复制失败')
  }
}

async function handleDelete(id: string) {
  await testCaseApi.delete(id)
  message.success('已删除')
  selectedIds.value = selectedIds.value.filter(i => i !== id)
  await load()
}

async function deleteSelected() {
  dialog.warning({
    title: '确认批量删除',
    content: `将删除选中的 ${selectedIds.value.length} 个测试用例，确认吗？`,
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      batchDeleting.value = true
      try {
        await testCaseApi.batchDelete(selectedIds.value)
        message.success(`已删除 ${selectedIds.value.length} 个用例`)
        selectedIds.value = []
        await load()
      } finally {
        batchDeleting.value = false
      }
    },
  })
}

onMounted(async () => {
  const res = await applicationApi.list()
  appOptions.value = res.data.map(a => ({ label: a.name, value: a.id }))
  appMap.value = Object.fromEntries(res.data.map(a => [a.id, a.name]))
  await load()
})

watch(() => pagination.itemCount, (count) => {
  setPageSummary(`共 ${count} 条用例`)
}, { immediate: true })

onBeforeUnmount(clearPageSummary)
</script>
