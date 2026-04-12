# 会话列表与接口列表排序功能设计

**日期：** 2026-04-12  
**范围：** `backend/api/v1/sessions.py`、`frontend/frontend/src/api/recordings.ts`、`frontend/frontend/src/views/recording/RecordingCenter.vue`

---

## 目标

会话列表和接口列表默认按时间倒序展示，同时支持用户点击列头切换升/降序，方便快速定位历史数据。

---

## 架构

采用**服务端排序**：排序参数随分页请求一起发往后端，后端应用 `ORDER BY` 后返回结果。  
不采用客户端排序，原因：两个列表均为服务端分页，前端排序只能对当前页生效，跨页数据会产生误导。

---

## 后端（`backend/api/v1/sessions.py`）

### `GET /sessions` 新增参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sort_by` | `str` | `"started_at"` | 排序字段 |
| `sort_order` | `str` | `"desc"` | `"asc"` 或 `"desc"` |

**允许的 `sort_by` 白名单：** `{"started_at"}`

### `GET /recordings` 新增参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sort_by` | `str` | `"created_at"` | 排序字段 |
| `sort_order` | `str` | `"desc"` | `"asc"` 或 `"desc"` |

**允许的 `sort_by` 白名单：** `{"created_at", "duration_ms"}`

### 校验逻辑

```python
ALLOWED_SESSION_SORT = {"started_at"}
ALLOWED_RECORDING_SORT = {"created_at", "duration_ms"}

if sort_by not in ALLOWED_SESSION_SORT:
    raise HTTPException(400, f"Invalid sort_by: {sort_by}")
sort_col = getattr(RecordingSession, sort_by)
order_expr = sort_col.desc() if sort_order == "desc" else sort_col.asc()
base = base.order_by(order_expr)
```

白名单防止 SQL 注入，非法字段返回 HTTP 400。

---

## 前端 API（`frontend/frontend/src/api/recordings.ts`）

`sessionApi.search` 参数类型加：
```ts
sort_by?: string
sort_order?: string
```

`recordingApi.list` 参数类型加：
```ts
sort_by?: string
sort_order?: string
```

---

## 前端 View（`frontend/frontend/src/views/recording/RecordingCenter.vue`）

### 排序状态

```ts
const sessionSortState = ref<{ key: string; order: 'ascend' | 'descend' } | null>({
  key: 'started_at',
  order: 'descend',
})

const recordingSortState = ref<{ key: string; order: 'ascend' | 'descend' } | null>({
  key: 'created_at',
  order: 'descend',
})
```

### 会话列表列定义变更

`started_at` 列加 `sorter: true` 和 `sortOrder`（受控模式），绑定当前排序状态。

### 接口列表列定义变更

`created_at` 和 `duration_ms` 列各加 `sorter: true` 和 `sortOrder`。

### `n-data-table` 变更

两个表格加 `remote` prop 启用远程排序，监听 `@update:sorter`：

```ts
function onSessionSort(sorter: { columnKey: string; order: 'ascend' | 'descend' | false } | null) {
  if (!sorter || sorter.order === false) {
    sessionSortState.value = { key: 'started_at', order: 'descend' } // 回退默认
  } else {
    sessionSortState.value = { key: sorter.columnKey, order: sorter.order }
  }
  sessionPagination.page = 1
  loadSessionsPage()
}
```

接口列表同理。

### 请求携带排序参数

`loadSessionsPage()` 增加：
```ts
sort_by: sessionSortState.value?.key ?? 'started_at',
sort_order: sessionSortState.value?.order === 'ascend' ? 'asc' : 'desc',
```

`loadPage()` 增加：
```ts
sort_by: recordingSortState.value?.key ?? 'created_at',
sort_order: recordingSortState.value?.order === 'ascend' ? 'asc' : 'desc',
```

---

## 数据流

```
用户点击列头
  → @update:sorter 事件
  → 更新 sortState（key + order）
  → 重置 page = 1
  → loadXxxPage() 携带 sort_by + sort_order
  → 后端 ORDER BY 后返回
  → 表格渲染，列头显示当前排序方向
```

---

## 不在范围内

- 其他页面（回放、测试用例等）的列表排序
- 多列联合排序
- 排序状态持久化（刷新后重置为默认）
