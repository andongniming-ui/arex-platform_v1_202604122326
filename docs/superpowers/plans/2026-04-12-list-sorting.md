# 会话列表与接口列表排序功能 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为录制中心的会话列表和接口列表加入服务端排序支持，默认按时间倒序，支持用户点击列头切换升/降序。

**Architecture:** 后端两个 GET 接口各新增 `sort_by` + `sort_order` 查询参数，用白名单校验后动态构建 `ORDER BY`；前端 API 类型加对应字段，View 层保存排序状态，表格开启 `remote` 模式，点击列头触发重新请求。

**Tech Stack:** FastAPI (SQLAlchemy async)、Vue 3 + TypeScript、Naive UI `n-data-table`

---

## 涉及文件

| 文件 | 变更类型 | 职责 |
|------|---------|------|
| `backend/api/v1/sessions.py` | 修改 | `list_sessions` 和 `list_recordings` 加排序参数 |
| `frontend/frontend/src/api/recordings.ts` | 修改 | `sessionApi.search` / `recordingApi.list` 参数类型扩展 |
| `frontend/frontend/src/views/recording/RecordingCenter.vue` | 修改 | 排序状态、列定义、表格事件、请求参数 |

---

### Task 1：后端 `list_sessions` 支持排序

**Files:**
- Modify: `backend/api/v1/sessions.py:121-147`

- [ ] **Step 1：找到 `list_sessions` 函数签名，在参数列表末尾（`db` 之前）加排序参数**

  文件：`backend/api/v1/sessions.py`，找到：
  ```python
  async def list_sessions(
      app_id: str | None = None,
      name: str | None = None,
      status: str | None = None,
      started_after: str | None = None,
      started_before: str | None = None,
      limit: int = 20,
      offset: int = 0,
      db: AsyncSession = Depends(get_db),
  ):
  ```
  替换为：
  ```python
  async def list_sessions(
      app_id: str | None = None,
      name: str | None = None,
      status: str | None = None,
      started_after: str | None = None,
      started_before: str | None = None,
      limit: int = 20,
      offset: int = 0,
      sort_by: str = "started_at",
      sort_order: str = "desc",
      db: AsyncSession = Depends(get_db),
  ):
  ```

- [ ] **Step 2：在函数体内替换硬编码排序为动态排序**

  找到（函数体末尾两行）：
  ```python
      total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
      items = (await db.execute(base.order_by(RecordingSession.started_at.desc()).offset(offset).limit(limit))).scalars().all()
  ```
  替换为：
  ```python
      _SESSION_SORT_COLS = {"started_at"}
      if sort_by not in _SESSION_SORT_COLS:
          raise HTTPException(400, f"Invalid sort_by '{sort_by}'. Allowed: {_SESSION_SORT_COLS}")
      _sort_col = getattr(RecordingSession, sort_by)
      _order_expr = _sort_col.desc() if sort_order == "desc" else _sort_col.asc()
      total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
      items = (await db.execute(base.order_by(_order_expr).offset(offset).limit(limit))).scalars().all()
  ```

- [ ] **Step 3：手动验证接口**

  启动后端后（或在现有进程下）：
  ```bash
  curl -s "http://localhost:8000/api/v1/sessions?limit=2&sort_by=started_at&sort_order=asc" | python3 -m json.tool | head -30
  ```
  预期：返回 `{"items": [...], "total": N}`，items 按 `started_at` 升序。

  ```bash
  curl -s "http://localhost:8000/api/v1/sessions?limit=2&sort_by=bad_col" | python3 -m json.tool
  ```
  预期：返回 HTTP 400，body 含 `"Invalid sort_by"`。

- [ ] **Step 4：提交**

  ```bash
  git add backend/api/v1/sessions.py
  git commit -m "feat(backend): list_sessions 支持 sort_by / sort_order 参数"
  ```

---

### Task 2：后端 `list_recordings` 支持排序

**Files:**
- Modify: `backend/api/v1/sessions.py:697-728`

- [ ] **Step 1：找到 `list_recordings` 函数签名，加排序参数**

  找到：
  ```python
  async def list_recordings(
      session_id: str | None = None,
      app_id: str | None = None,
      entry_type: str | None = None,
      status: str | None = None,
      path_contains: str | None = None,
      created_after: str | None = None,
      created_before: str | None = None,
      limit: int = 50,
      offset: int = 0,
      db: AsyncSession = Depends(get_db),
  ):
  ```
  替换为：
  ```python
  async def list_recordings(
      session_id: str | None = None,
      app_id: str | None = None,
      entry_type: str | None = None,
      status: str | None = None,
      path_contains: str | None = None,
      created_after: str | None = None,
      created_before: str | None = None,
      limit: int = 50,
      offset: int = 0,
      sort_by: str = "created_at",
      sort_order: str = "desc",
      db: AsyncSession = Depends(get_db),
  ):
  ```

- [ ] **Step 2：替换硬编码排序**

  找到：
  ```python
      total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
      items = (await db.execute(base.order_by(Recording.created_at.desc()).offset(offset).limit(limit))).scalars().all()
  ```
  替换为：
  ```python
      _RECORDING_SORT_COLS = {"created_at", "duration_ms"}
      if sort_by not in _RECORDING_SORT_COLS:
          raise HTTPException(400, f"Invalid sort_by '{sort_by}'. Allowed: {_RECORDING_SORT_COLS}")
      _sort_col = getattr(Recording, sort_by)
      _order_expr = _sort_col.desc() if sort_order == "desc" else _sort_col.asc()
      total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
      items = (await db.execute(base.order_by(_order_expr).offset(offset).limit(limit))).scalars().all()
  ```

- [ ] **Step 3：手动验证接口**

  ```bash
  curl -s "http://localhost:8000/api/v1/recordings?limit=2&sort_by=duration_ms&sort_order=asc" | python3 -m json.tool | head -30
  ```
  预期：items 按 `duration_ms` 升序排列。

  ```bash
  curl -s "http://localhost:8000/api/v1/recordings?sort_by=path" | python3 -m json.tool
  ```
  预期：HTTP 400，含 `"Invalid sort_by"`。

- [ ] **Step 4：提交**

  ```bash
  git add backend/api/v1/sessions.py
  git commit -m "feat(backend): list_recordings 支持 sort_by / sort_order 参数"
  ```

---

### Task 3：前端 API 类型扩展

**Files:**
- Modify: `frontend/frontend/src/api/recordings.ts`

- [ ] **Step 1：扩展 `sessionApi.search` 参数类型**

  找到：
  ```ts
  search: (params?: {
    app_id?: string
    name?: string
    status?: string
    started_after?: string
    started_before?: string
    limit?: number
    offset?: number
  }) => client.get<PagedResult<Session>>('/sessions', { params }),
  ```
  替换为：
  ```ts
  search: (params?: {
    app_id?: string
    name?: string
    status?: string
    started_after?: string
    started_before?: string
    limit?: number
    offset?: number
    sort_by?: string
    sort_order?: string
  }) => client.get<PagedResult<Session>>('/sessions', { params }),
  ```

- [ ] **Step 2：扩展 `recordingApi.list` 参数类型**

  找到：
  ```ts
  list: (params?: {
    session_id?: string
    app_id?: string
    entry_type?: string
    status?: string
    path_contains?: string
    created_after?: string
    created_before?: string
    limit?: number
    offset?: number
  }) => client.get<PagedResult<Recording>>('/recordings', { params }),
  ```
  替换为：
  ```ts
  list: (params?: {
    session_id?: string
    app_id?: string
    entry_type?: string
    status?: string
    path_contains?: string
    created_after?: string
    created_before?: string
    limit?: number
    offset?: number
    sort_by?: string
    sort_order?: string
  }) => client.get<PagedResult<Recording>>('/recordings', { params }),
  ```

- [ ] **Step 3：提交**

  ```bash
  git add frontend/frontend/src/api/recordings.ts
  git commit -m "feat(api): sessionApi / recordingApi 参数加 sort_by / sort_order"
  ```

---

### Task 4：前端 View — 会话列表排序

**Files:**
- Modify: `frontend/frontend/src/views/recording/RecordingCenter.vue`

- [ ] **Step 1：在 script setup 区域加会话排序状态**

  在文件 script 区里找到 `sessionPagination` 声明处（约 line 375）附近，加入：
  ```ts
  const sessionSortState = ref<{ columnKey: string; order: 'ascend' | 'descend' } | null>({
    columnKey: 'started_at',
    order: 'descend',
  })
  ```

- [ ] **Step 2：为 `sessionColumns` 的 `started_at` 列加 `sorter` 和受控排序**

  找到 `sessionColumns` 中的 `started_at` 列定义：
  ```ts
  {
    title: '开始时间',
    key: 'started_at',
    width: 170,
    render: (r: Session) => fmtTime(r.started_at),
  },
  ```
  替换为：
  ```ts
  {
    title: '开始时间',
    key: 'started_at',
    width: 170,
    sorter: true,
    sortOrder: computed(() =>
      sessionSortState.value?.columnKey === 'started_at' ? sessionSortState.value.order : false
    ),
    render: (r: Session) => fmtTime(r.started_at),
  },
  ```

- [ ] **Step 3：添加会话排序处理函数**

  在 `onSessionFilterChange` 函数附近加入：
  ```ts
  function onSessionSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
    if (!sorter || sorter.order === false) {
      sessionSortState.value = { columnKey: 'started_at', order: 'descend' }
    } else {
      sessionSortState.value = { columnKey: sorter.columnKey, order: sorter.order }
    }
    sessionPagination.page = 1
    loadSessionsPage()
  }
  ```

- [ ] **Step 4：会话 `n-data-table` 加 `remote` 和 `@update:sorter`**

  找到会话表格：
  ```html
  <n-data-table
    :columns="sessionColumns"
    :data="sessionRows"
    :loading="sessionsLoading"
    :row-key="(r: any) => r.id"
    :checked-row-keys="selectedSessionIds"
    @update:checked-row-keys="selectedSessionIds = $event as string[]"
  />
  ```
  替换为：
  ```html
  <n-data-table
    remote
    :columns="sessionColumns"
    :data="sessionRows"
    :loading="sessionsLoading"
    :row-key="(r: any) => r.id"
    :checked-row-keys="selectedSessionIds"
    @update:checked-row-keys="selectedSessionIds = $event as string[]"
    @update:sorter="onSessionSorterChange"
  />
  ```

- [ ] **Step 5：`loadSessionsPage` 传递排序参数**

  找到 `loadSessionsPage` 中调用 `sessionApi.search` 的参数对象，末尾加两行：
  ```ts
  sort_by: sessionSortState.value?.columnKey ?? 'started_at',
  sort_order: sessionSortState.value?.order === 'ascend' ? 'asc' : 'desc',
  ```
  完整参数对象变为：
  ```ts
  const sessionsRes = await sessionApi.search({
    app_id: filterAppId.value || undefined,
    name: sessionKeyword.value || undefined,
    status: sessionStatus.value || undefined,
    started_after: sessionStartedRange.value ? new Date(sessionStartedRange.value[0]).toISOString() : undefined,
    started_before: sessionStartedRange.value ? new Date(sessionStartedRange.value[1]).toISOString() : undefined,
    limit: sessionPagination.pageSize,
    offset: (sessionPagination.page - 1) * sessionPagination.pageSize,
    sort_by: sessionSortState.value?.columnKey ?? 'started_at',
    sort_order: sessionSortState.value?.order === 'ascend' ? 'asc' : 'desc',
  })
  ```

- [ ] **Step 6：提交**

  ```bash
  git add frontend/frontend/src/views/recording/RecordingCenter.vue
  git commit -m "feat(ui): 会话列表支持按开始时间排序"
  ```

---

### Task 5：前端 View — 接口列表排序

**Files:**
- Modify: `frontend/frontend/src/views/recording/RecordingCenter.vue`

- [ ] **Step 1：加接口列表排序状态**

  在 `sessionSortState` 下方加：
  ```ts
  const recordingSortState = ref<{ columnKey: string; order: 'ascend' | 'descend' } | null>({
    columnKey: 'created_at',
    order: 'descend',
  })
  ```

- [ ] **Step 2：为 `columns` 中 `created_at` 和 `duration_ms` 列加 `sorter`**

  找到 `columns` 中的 `耗时(ms)` 列：
  ```ts
  { title: '耗时(ms)', key: 'duration_ms', width: 80 },
  ```
  替换为：
  ```ts
  {
    title: '耗时(ms)',
    key: 'duration_ms',
    width: 80,
    sorter: true,
    sortOrder: computed(() =>
      recordingSortState.value?.columnKey === 'duration_ms' ? recordingSortState.value.order : false
    ),
  },
  ```

  找到 `columns` 中的 `时间` 列：
  ```ts
  {
    title: '时间', key: 'created_at', width: 155,
    render: (r: Recording) => fmtTime(r.created_at),
  },
  ```
  替换为：
  ```ts
  {
    title: '时间',
    key: 'created_at',
    width: 155,
    sorter: true,
    sortOrder: computed(() =>
      recordingSortState.value?.columnKey === 'created_at' ? recordingSortState.value.order : false
    ),
    render: (r: Recording) => fmtTime(r.created_at),
  },
  ```

- [ ] **Step 3：添加接口排序处理函数**

  在 `onSessionSorterChange` 下方加：
  ```ts
  function onRecordingSorterChange(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
    if (!sorter || sorter.order === false) {
      recordingSortState.value = { columnKey: 'created_at', order: 'descend' }
    } else {
      recordingSortState.value = { columnKey: sorter.columnKey, order: sorter.order }
    }
    pagination.page = 1
    loadPage()
  }
  ```

- [ ] **Step 4：接口 `n-data-table` 加 `remote` 和 `@update:sorter`**

  找到接口表格（约 line 171）：
  ```html
  <n-data-table
    :columns="columns"
    :data="filteredRecordings"
    :loading="loading"
    :row-key="(r: any) => r.id"
    :checked-row-keys="selectedIds"
    :scroll-x="1050"
    @update:checked-row-keys="selectedIds = $event as string[]"
  />
  ```
  替换为：
  ```html
  <n-data-table
    remote
    :columns="columns"
    :data="filteredRecordings"
    :loading="loading"
    :row-key="(r: any) => r.id"
    :checked-row-keys="selectedIds"
    :scroll-x="1050"
    @update:checked-row-keys="selectedIds = $event as string[]"
    @update:sorter="onRecordingSorterChange"
  />
  ```

- [ ] **Step 5：`loadPage` 传递排序参数**

  找到 `loadPage` 内调用 `recordingApi.list` 的参数对象，末尾加：
  ```ts
  sort_by: recordingSortState.value?.columnKey ?? 'created_at',
  sort_order: recordingSortState.value?.order === 'ascend' ? 'asc' : 'desc',
  ```
  完整参数对象：
  ```ts
  const res = await recordingApi.list({
    app_id: filterAppId.value || undefined,
    session_id: filterSessionId.value || undefined,
    entry_type: filterType.value || undefined,
    status: filterRecordStatus.value || undefined,
    path_contains: filterPathKeyword.value || undefined,
    created_after: filterDateRange.value ? new Date(filterDateRange.value[0]).toISOString() : undefined,
    created_before: filterDateRange.value ? new Date(filterDateRange.value[1]).toISOString() : undefined,
    limit: pagination.pageSize,
    offset: (pagination.page - 1) * pagination.pageSize,
    sort_by: recordingSortState.value?.columnKey ?? 'created_at',
    sort_order: recordingSortState.value?.order === 'ascend' ? 'asc' : 'desc',
  })
  ```

- [ ] **Step 6：提交**

  ```bash
  git add frontend/frontend/src/views/recording/RecordingCenter.vue
  git commit -m "feat(ui): 接口列表支持按时间和耗时排序"
  ```

---

### Task 6：前端构建验证

**Files:**
- `frontend/frontend/` (build)

- [ ] **Step 1：TypeScript 类型检查**

  ```bash
  cd frontend/frontend && npx vue-tsc --noEmit
  ```
  预期：无类型错误输出，退出码 0。

- [ ] **Step 2：构建**

  ```bash
  cd frontend/frontend && npm run build
  ```
  预期：`dist/` 目录生成，无报错。

- [ ] **Step 3：提交构建产物（如项目规范要求）**

  ```bash
  cd /home/test/arex-platform_v1
  git add frontend/frontend/dist
  git commit -m "build: 重新构建前端（排序功能）"
  ```
