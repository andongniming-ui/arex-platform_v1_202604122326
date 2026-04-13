import { computed, reactive } from 'vue'

interface OffsetPaginationOptions {
  page?: number
  pageSize?: number
  pageSizes?: number[]
}

export function useOffsetPagination(options: OffsetPaginationOptions = {}) {
  const pagination = reactive({
    page: options.page ?? 1,
    pageSize: options.pageSize ?? 20,
    pageSizes: options.pageSizes ?? [20, 50, 100],
    itemCount: 0,
  })

  const offset = computed(() => (pagination.page - 1) * pagination.pageSize)

  function resetPage() {
    pagination.page = 1
  }

  function updatePageSize(size: number) {
    pagination.pageSize = size
    pagination.page = 1
  }

  function setTotal(total: number) {
    pagination.itemCount = total
  }

  return {
    pagination,
    offset,
    resetPage,
    updatePageSize,
    setTotal,
  }
}
