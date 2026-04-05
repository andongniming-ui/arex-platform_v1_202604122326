# AREX 回放平台 — 操作手册

> 适用版本：arex-platform（基于 AREX Agent v0.4.8）
> 最后更新：2026-04-05

---

## 目录

1. [系统概述](#1-系统概述)
2. [运行原理](#2-运行原理)
3. [快速启动](#3-快速启动)
4. [注册应用](#4-应用管理)
5. [录制流量](#5-录制中心)
6. [管理测试用例](#6-测试用例库)
7. [执行回放](#7-回放中心)
8. [查看结果](#8-回放结果)
9. [回放历史](#9-回放历史)
10. [定时回放](#10-定时回放)
11. [回放套件](#11-回放套件)
12. [双环境对比](#12-双环境对比)
13. [数据总览](#13-数据总览)
14. [注意事项与常见问题](#14-注意事项与常见问题)

---

## 1. 系统概述

AREX 回放平台是一套**流量录制 → 回放 → 对比**自动化测试系统，核心用途：

- **录制**：在被测 Java 服务上挂载 AREX Agent，自动抓取真实流量（请求 + 响应 + 数据库/RPC 子调用）
- **回放**：将录制的请求重新发送到目标服务，对比响应是否一致
- **对比**：字段级 Diff 分析，帮助快速定位接口回归问题

**典型场景**：
- Java 服务升级后，验证新版本与旧版本行为一致
- 两套环境（PL2 vs VT）行为比较
- 持续集成：定时回放 + Webhook 告警

---

## 2. 运行原理

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   arex-platform                      │
│  (FastAPI 后端 + Vue3 前端 + PostgreSQL)              │
│                                                     │
│  ① 管理应用注册 & 录制会话                             │
│  ② 从 arex-storage 拉取录制数据存入 PostgreSQL         │
│  ③ 执行回放（直接 HTTP 请求目标服务）                    │
│  ④ 字段对比 + 失败分析                                 │
└────────────────┬──────────────────────────────────┘
                 │ SSH / HTTP
       ┌─────────┴──────────┐
       ▼                    ▼
┌─────────────┐    ┌────────────────────────────┐
│  目标 Java  │    │       arex-storage          │
│  服务进程   │    │  (Spring Boot + MongoDB      │
│             │    │   + Redis，端口 8093)        │
│ ← arex-agent│    │                            │
│   .jar 挂载 │───→│  录制数据持久化存储           │
│  （-javaagent）  │  /api/storage/record/*      │
└─────────────┘    └────────────────────────────┘
```

### 2.2 录制流程

```
用户请求 → Java 服务
              │
          arex-agent 字节码拦截
              │
          AREXMocker JSON 组装
          （请求体 + 响应体 + 子调用）
              │
          HTTP POST 上报 → arex-storage → MongoDB 存储
              │
          平台调用 arex-storage API 拉取
              │
          解析存入 PostgreSQL (recording 表)
```

### 2.3 回放流程

```
平台读取 recording.request_body (JSON 格式)
    │
    ├── method: POST
    ├── uri: /api/bank/service
    ├── body: <xml 请求体>
    └── contentType: application/xml
         │
         ▼
HTTP 请求 → 目标服务（VT / PL2 / 任意环境）
         │
         ▼
收到响应 → 与 recording.response_body 做 Diff
         │
         ▼
存入 replay_result 表 → 前端展示
```

### 2.4 数据格式说明

| 字段 | 说明 |
|------|------|
| `recording.request_body` | JSON：`{"method":"POST","uri":"/api/bank/service","body":"<xml>...","contentType":"application/xml"}` |
| `recording.response_body` | 原始响应字符串（XML / JSON） |
| `recording.trace_id` | AREX 录制追踪 ID，用于 Mock 子调用 |
| `recording.sub_invocations` | 录制期间的数据库/RPC/Redis 子调用列表（JSON） |

### 2.5 sampleRate 说明

AREX Agent 使用 Guava `RateLimiter` 控制录制频率：

```
实际录制速率 = sampleRate / 60  条/秒
```

| sampleRate | 实际限速 |
|-----------|---------|
| 1（默认） | 1条/分钟 ⚠️ |
| 100 | 约 1.67 条/秒 |

**修改方式**：直接改 MongoDB 里的 `RecordServiceConfig` 集合：
```javascript
// 进入 arex-storage 容器的 mongo
db.RecordServiceConfig.updateMany(
  { appId: { $in: ['pl2', 'vt-bank-service'] } },
  { $set: { sampleRate: 100 } }
)
```
修改后需要**重启目标 Java 服务**（Rate Limiter 只能减速，不能加速）。

---

## 3. 快速启动

### 3.1 启动基础设施

```bash
cd /home/test/arex-platform
docker-compose up -d
```

包含的服务：
| 服务 | 端口 | 说明 |
|------|------|------|
| postgres | 5432 | 平台数据库 |
| backend | 8001 | FastAPI 后端（外部访问 8001） |
| frontend | 5174 | Vue3 前端 |
| mongodb | 27017 | arex-storage 数据库 |
| arex-redis | 6380 | arex-storage 缓存 |
| arex-storage | 8093 | AREX 录制数据存储服务 |

### 3.2 访问平台

浏览器打开：`http://172.25.109.28:5174`

### 3.3 启动被测服务（带 arex-agent）

```bash
# PL2 示例（port 9095）
cd /home/test/N-LSFT/PL2-bank-service/target
nohup java \
  -javaagent:/home/test/arex-agent/arex-agent.jar \
  -Darex.service.name=pl2 \
  -Darex.storage.service.host=172.25.109.28:8093 \
  -jar pl2-bank-service-1.0.0.jar --server.port=9095 \
  > /tmp/pl2.log 2>&1 &

# VT 示例（port 9096）
cd /home/test/N-LSFT/VT-bank-service/target
nohup java \
  -javaagent:/home/test/arex-agent/arex-agent.jar \
  -Darex.service.name=vt-bank-service \
  -Darex.storage.service.host=172.25.109.28:8093 \
  -jar vt-bank-service-1.0.0.jar --server.port=9096 \
  > /tmp/vt.log 2>&1 &
```

> **⚠️ 注意**：`-Darex.storage.service.host` 必须填 arex-storage 的 IP:端口，不能用 localhost，因为 Java 进程和 Docker 容器不在同一个网络命名空间。

### 3.4 确认服务正常

```bash
# 检查 arex-storage 是否在线
curl http://172.25.109.28:8093/api/storage/record/saveTest/

# 检查 backend 是否在线
curl http://172.25.109.28:8001/api/v1/applications
```

---

## 4. 应用管理

**入口**：左侧菜单 → 应用管理

### 4.1 注册应用

点击右上角"新增应用"，填写：

| 字段 | 说明 | 示例 |
|------|------|------|
| 应用名称 | 必填，需与 `-Darex.service.name` 完全一致 | `pl2` |
| SSH Host | 目标服务器 IP | `172.25.109.28` |
| SSH 用户名 | SSH 登录用户 | `test` |
| 认证方式 | PASSWORD 或 KEY | PASSWORD |
| SSH 密码 | 密码认证时填写 | - |
| 服务端口 | Java 服务的 HTTP 端口 | `9095` |
| JAR 文件名 | 用于 PID 识别 | `pl2-bank-service-1.0.0.jar` |

> **⚠️ 注意**：应用名称（name）和 `-Darex.service.name` 必须严格一致，否则 arex-storage 里的录制数据无法关联到该应用。

### 4.2 应用详情页

点击列表中的应用名称进入详情页，包含以下功能区：

#### SSH 连接测试
- "测试连接"：验证 SSH 凭据是否正确
- "发现 PID"：通过 `jps` 命令找到 Java 进程 PID

#### 录制配置
- **采样率**：1%~100%，控制录制密度（实际控制 MongoDB 里的 sampleRate，见 2.5 节）
- **脱敏规则**：对录制数据中的敏感字段做脱敏处理
  - 策略：remove（删除）/ mask（替换为 ***）/ partial（部分隐藏）/ hash（哈希）

#### 回放默认配置
- **默认忽略字段**：回放时自动忽略的字段（如 timestamp、traceId）
- **性能阈值（ms）**：超过此时间的回放请求标记为 PERF_FAIL

#### XML 请求模板
当被测服务是 XML 接口时，若 arex-agent 未能录制到请求体（某些旧版本兼容性问题），可在此配置模板：
```json
{
  "QUERY_BALANCE": "<request><service_id>QUERY_BALANCE</service_id><account_no>{{account_no}}</account_no></request>",
  "OPEN_ACCOUNT": "<request>...</request>"
}
```
平台会根据 service_id 自动填充请求体进行回放。

#### 录制会话管理
在详情页底部可以管理该应用的所有录制会话。

---

## 5. 录制中心

**入口**：左侧菜单 → 录制中心

### 5.1 发起录制

方式一：在**应用管理 → 详情页**，找到"录制会话"区域，点击"新建会话"。

方式二：在录制中心页面顶部的会话筛选器中发起。

### 5.2 录制流程说明

```
1. 点击"新建会话" → 填写会话名称 → 确认
2. 向被测 Java 服务发送真实请求（Postman / 前端 / 自动化脚本）
3. arex-agent 自动抓取流量 → 上报到 arex-storage
4. 平台后台轮询 arex-storage → 拉取数据 → 存入 recording 表
5. 点击"停止会话" → 查看已采集的录制条数
```

### 5.3 录制列表功能

| 功能 | 说明 |
|------|------|
| 按应用筛选 | 只显示某个应用的录制 |
| 按会话筛选 | 只显示某次录制会话的流量 |
| 按入口类型筛选 | HTTP / SERVLET / DUBBO / MYBATIS |
| 响应质量筛选 | 2xx成功 / 4xx客户端错误 / 5xx服务端错误 / 响应为空 |
| 日期范围筛选 | 支持快捷选项（今天/最近3天/7天/30天） |
| HAR 文件导入 | 从浏览器导出的 HAR 文件导入录制数据 |
| 添加到测试用例 | 批量选中 → 加入已有或新建用例 |
| 批量打标签 | 给录制添加分类标签 |
| 批量删除 | 清理无用录制 |

### 5.4 录制详情

点击某条录制进入详情页：

- **请求体**：发送到服务的原始 XML/JSON 内容
- **响应体**：服务返回的原始内容（作为"黄金标准"存档）
- **子调用 Mock 数据**：服务内部的 DB 查询、RPC 调用、Redis 操作的录制快照

> **⚠️ 入口类型说明**：
> - `SERVLET`：AREX Agent 在 Servlet 层拦截，等同于旧版 Repeater 的 `HTTP` 类型
> - `HTTP`：部分版本区别标注，功能相同
> - 两者在功能上无本质区别，均为 HTTP 接口录制

---

## 6. 测试用例库

**入口**：左侧菜单 → 测试用例库

### 6.1 用例的作用

测试用例是**一组录制的集合**，是执行回放的基本单位。
通常按业务场景组织：
- `账户开户流程` → 包含 OPEN_ACCOUNT + QUERY_BALANCE + QUERY_ACCOUNT_DETAIL 三条录制
- `账户冻结解冻流程` → 包含 FREEZE_ACCOUNT + UNFREEZE_ACCOUNT 录制

### 6.2 创建用例

点击"新建用例"，填写：
- **用例名称**（必填）
- **关联应用**（选填，便于筛选）
- **描述和标签**（选填）

### 6.3 向用例添加录制

进入用例详情页 → 点击"添加录制" → 在弹窗中筛选并勾选录制 → 确认添加。

支持多维度筛选：应用、会话、路径关键字、响应质量、日期范围。

### 6.4 编辑录制请求参数

在用例详情页，点击某条录制的"编辑"按钮，可修改：
- **请求体**（Body）
- **Content-Type**

> **使用场景**：对录制的数据做参数化调整，例如将账号替换为另一个账号进行测试。

### 6.5 发起回放

在用例详情页右上角，点击"发起回放"按钮，直接跳转到回放中心并预填该用例。

---

## 7. 回放中心

**入口**：左侧菜单 → 回放中心

### 7.1 基础配置

| 配置项 | 说明 | 建议 |
|--------|------|------|
| 选择测试用例 | 必填，回放哪批录制 | - |
| 目标应用 | 必填，回放打到哪个服务 | - |
| 环境标签 | 选填，如 staging/test | 便于历史区分 |
| Host 覆盖 | 选填，覆盖应用注册的 IP:端口 | 空则用注册配置 |

### 7.2 执行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 并发数 | 1 | 同时发送几条请求，建议 1-5 |
| 请求间隔（ms） | 0 | 每条请求之间的延迟 |
| 重复次数 | 1 | 流量放大，同一录制发 N 次 |
| 失败重试次数 | 0 | 失败后自动重试（最多5次） |

### 7.3 Mock 与降噪

| 开关 | 说明 |
|------|------|
| Mock 子调用 | 开启后，回放请求头注入 `arex-record-id`，arex-agent 拦截 DB/RPC/Redis 调用并返回录制值，避免真实数据写入 |
| 智能降噪 | 自动忽略 30+ 个常见动态字段（timestamp、requestId、traceId 等） |

> **⚠️ Mock 子调用注意**：目标服务必须已挂载 arex-agent 且 arex-storage 正常运行，否则 Mock 不生效，服务会真实访问数据库。

### 7.4 忽略字段 & Diff 规则

**忽略字段**：回放时对比响应，忽略指定字段的差异。常用于：
- `timestamp`、`createTime`、`requestId`：每次请求都不同，无需对比
- 点击"推荐字段"可自动扫描录制中的常见动态字段

**Diff 规则**（高级）：

| 规则类型 | 说明 | 示例 |
|---------|------|------|
| ignore | 忽略某字段 | `body.timestamp` |
| numeric_tolerance | 数值允许误差 | balance 误差 ±0.01 |
| regex_match | 正则匹配即通过 | `\d{4}-\d{2}-\d{2}` |
| type_only | 只校验类型，不校验值 | 字符串 vs 字符串 |

### 7.5 性能阈值

设置回放响应时间上限（ms）。超过阈值的请求标记为 `PERF_FAIL`，在结果页单独展示。

### 7.6 Webhook 通知

回放完成后，平台向指定 URL 发送 POST 请求，携带回放结果摘要（通过率、成功/失败数）。

---

## 8. 回放结果

**入口**：回放历史 → 查看结果
**路由**：`/results/:jobId`

### 8.1 结果概览

顶部统计卡片：
- **总数 / 成功 / 失败 / 错误 / 通过率**
- 绿色（≥90%）/ 黄色（60-90%）/ 红色（<60%）

### 8.2 失败分析

失败原因自动分类：

| 类别 | 说明 |
|------|------|
| ENVIRONMENT | 网络不通、服务未启动、连接超时 |
| DATA_ISSUE | 账户不存在、数据状态不一致（测试数据问题） |
| BUG | 响应内容与录制不符（真正的逻辑差异） |
| PERFORMANCE | 响应时间超过阈值 |
| UNKNOWN | 无法自动分类 |

### 8.3 结果详情 & Diff 查看

点击某条结果的"查看"按钮，弹出对比弹窗：

- **请求体**：回放时实际发送的请求内容
- **原始响应**：录制时服务返回的内容（黄金标准）
- **回放响应**：本次回放目标服务返回的内容
- **Diff 高亮**：字段级差异标红

### 8.4 保存失败结果为测试用例

在结果页，勾选失败的条目 → 点击"保存为用例"，可将失败的请求单独提取为新用例，方便持续跟踪该问题。

### 8.5 导出 HTML 报告

点击"导出报告"，生成包含完整对比结果的 HTML 文件，可离线查看或发送给团队。

---

## 9. 回放历史

**入口**：左侧菜单 → 回放历史

所有已执行的回放任务列表，支持：
- 按用例名称搜索
- 按用例、应用、状态筛选
- 查看结果（跳转到结果详情）
- **重新回放**：一键用相同配置重新执行一次（复制全部参数）
- 批量删除

| 状态 | 含义 |
|------|------|
| PENDING | 排队等待中 |
| RUNNING | 正在回放 |
| DONE | 已完成 |
| FAILED | 执行失败（非业务失败，是平台级错误） |
| CANCELLED | 已取消 |

---

## 10. 定时回放

**入口**：左侧菜单 → 定时回放

### 10.1 创建定时任务

填写：
- 任务名称
- 测试用例 + 目标应用（必填）
- Cron 表达式（5位标准格式）
- 其他回放参数（并发、环境、忽略字段等）
- Webhook URL（任务执行完成后通知）

常用 Cron 表达式：

| 表达式 | 执行时间 |
|--------|---------|
| `0 9 * * 1-5` | 工作日早9点 |
| `0 */2 * * *` | 每2小时 |
| `30 18 * * *` | 每天下午6:30 |

### 10.2 启用/停用

任务列表中可随时切换启用/停用状态，停用的任务不会触发执行。

---

## 11. 回放套件

**入口**：左侧菜单 → 回放套件

### 11.1 套件的作用

将多个测试用例组合成一个套件，一键批量执行，适合：
- 冒烟测试（一键跑所有关键接口）
- 回归测试（按模块分组执行）

### 11.2 创建套件

填写套件名称 + 默认目标应用 + 默认回放参数，然后进入套件详情添加用例。

### 11.3 执行套件

在套件列表，点击"运行"：
- 可覆盖目标应用和环境
- 套件中的每个用例依次执行（非并发）
- 执行历史可在套件详情查看

---

## 12. 双环境对比

**入口**：左侧菜单 → 双环境对比

### 12.1 适用场景

将同一批录制**同时回放到两个不同环境**，对比两个环境的响应差异，而不是与录制进行对比。

例如：
- PL2（旧版本）vs VT（新版本）：验证行为一致性
- 生产环境 vs 测试环境：发现配置差异

### 12.2 创建对比

填写：
- 测试用例
- 应用 A（基准环境）
- 应用 B（对比环境）
- 忽略字段、并发等参数

### 12.3 查看对比结果

| 指标 | 说明 |
|------|------|
| Agreed（一致） | 应用 A 和 B 返回相同响应 |
| Diverged（差异） | 应用 A 和 B 返回不同响应 |

点击每条差异记录，可看到 A/B 两侧的响应内容和 Diff 高亮。

---

## 13. 数据总览

**入口**：左侧菜单 → 数据总览（或首页）

### 展示内容

- **汇总卡片**：总回放次数、总发送量、成功/失败/错误数、平均通过率
- **通过率趋势图**：折线 + 柱状组合图，时间范围可选 7/14/30/90 天
- **每日明细表**：按天列出各项指标
- **日任务列表**：点击某天的数据，右侧抽屉展示当天所有回放任务详情

支持按**应用**和**时间范围**筛选。

---

## 14. 注意事项与常见问题

### 14.1 测试数据同步问题（⚠️ 重要）

**问题**：回放时出现大量"账户不存在"、"数据不存在"类错误。

**原因**：录制数据来自 PL2，请求体中硬编码了 PL2 的账号/ID。回放打到 VT 时，VT 没有对应数据。

**解决方案**：
- **正确做法**：录制前确保两个环境数据一致。例如，同步做相同的开户操作，确保账号编号一致，再开始录制
- **判断方式**：在失败分析中，"DATA_ISSUE" 类型的失败是数据问题，"BUG" 类型才是真正的逻辑差异

### 14.2 sampleRate 只录了1条

**原因**：默认 sampleRate=1，Rate Limiter = 1条/分钟。

**解决**：
1. 连接 MongoDB，执行 `db.RecordServiceConfig.updateMany({appId: 'xxx'}, {$set:{sampleRate:100}})`
2. 重启目标 Java 服务（Rate Limiter 只能降速，必须重启才能提速）

### 14.3 回放返回 HTTP 405 Method Not Allowed

**原因**：旧录制的 `request_body` 字段是纯 XML，不含 method 信息，回放时默认用了 GET。

**解决**：检查录制的 `request_body` 是否为 JSON 格式（包含 method/uri/body/contentType）。如果是纯 XML，需要重新录制，或手动在用例详情页编辑该录制的请求参数。

### 14.4 录制入口类型是 SERVLET 还是 HTTP

无区别。AREX Agent 在 Servlet 层拦截即标注为 SERVLET，旧版 Repeater 标注为 HTTP。功能完全相同。

### 14.5 arex-storage 连接数 / Redis FLUSHALL

修改 sampleRate 后，若 Agent 没有立即生效，可以：
```bash
# 进入 arex-redis 容器
docker exec -it arex-platform_arex-redis_1 redis-cli
FLUSHALL
```
清空 Redis 缓存后 Agent 会重新拉取配置。

### 14.6 SQLite vs PostgreSQL

本项目已迁移到 PostgreSQL（不再使用 SQLite）：
- **连接信息**：Host `172.25.109.28:5432`，库名 `arex_platform`，用户 `arex`，密码 `arex123`
- PostgreSQL 支持多连接，DBeaver 等工具可以直接连接，不影响服务运行

### 14.7 PL2/VT 服务数据重置

PL2 和 VT 使用**内存存储**（`ConcurrentHashMap`），重启即清空：
```bash
# 找进程
jps | grep bank-service

# 杀进程（确保所有实例都杀掉）
kill -9 <PID1> <PID2>

# 重新启动
nohup java -javaagent:/home/test/arex-agent/arex-agent.jar \
  -Darex.service.name=pl2 \
  -Darex.storage.service.host=172.25.109.28:8093 \
  -jar pl2-bank-service-1.0.0.jar --server.port=9095 \
  > /tmp/pl2.log 2>&1 &
```

> ⚠️ 用 `jps` 确认只有一个实例在运行，避免多进程导致数据混乱（账号没有从1开始）。

### 14.8 Docker 容器名称问题

若执行 `docker rm -f arex-platform_backend_1` 报错，实际容器名可能带有前缀哈希：
```bash
# 查看实际容器名
docker ps --format "{{.Names}}" | grep arex
# 结果例如：007215df2fc6_arex-platform_backend_1
```

### 14.9 回放并发与顺序

回放默认**并发执行**（concurrency > 1 时），不保证顺序。
对于有依赖关系的场景（如先开户才能查余额），建议：
- 设置 `并发数 = 1`
- 或使用 `请求间隔` 控制节奏

### 14.10 Webhook 通知格式

回放完成后，平台发送 POST 请求到 Webhook URL，请求体：
```json
{
  "job_id": "xxx",
  "status": "DONE",
  "total_count": 7,
  "success_count": 6,
  "fail_count": 1,
  "pass_rate": 0.857
}
```

---

## 附录：关键 API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/v1/applications` | 应用列表 |
| `POST /api/v1/sessions` | 新建录制会话 |
| `PUT /api/v1/sessions/{id}/stop` | 停止录制并采集数据 |
| `GET /api/v1/recordings` | 录制列表 |
| `POST /api/v1/replays` | 创建回放任务 |
| `GET /api/v1/replays/{id}/results` | 回放结果列表 |
| `GET /api/v1/replays/{id}/analysis` | 失败分析 |
| `GET /api/v1/replays/{id}/report` | 导出 HTML 报告 |

---

*文档维护：arex-platform 项目组*
