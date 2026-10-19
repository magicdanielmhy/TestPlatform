# Design

## Context

全新项目，无既有代码。目标是搭建一套"测试用例管理 + 接口测试执行"的 MVP，后端 Python、前端 Vue，采用前后端分离架构（REST API + 单页应用）。动机见 proposal.md - Why，行为契约见各 capability 的 spec.md。

## Goals / Non-Goals

**Goals:**

- 用最小成本打通核心闭环：登录 → 管理用例 → 组织案例集 → 执行接口测试 → 查看结果。
- 后端提供清晰、可扩展的 REST API；执行引擎与用例/案例集数据模型解耦，便于后续扩展更多测试类型。
- 数据层通过 ORM 抽象，MVP 用零配置存储，同时保留向更强数据库迁移的路径。

**Non-Goals:**

- 不做多用户/角色权限（MVP 仅单一管理员）。
- 不做 UI 自动化、定时任务、并发/分布式执行、通知告警。
- 不做测试报告统计分析看板（仅展示单次/历史执行结果）。

## Decisions

### 1. 后端框架：FastAPI

选择 FastAPI 而非 Flask/Django：自带 OpenAPI 文档、基于 Pydantic 的请求/响应校验、原生 async，适合 REST API；Django 对 MVP 偏重。校验层与执行引擎依赖 Pydantic 模型，减少样板代码。

### 2. 前端：Vue 3 + Vite + Element Plus + Pinia

选择 Vue 3（组合式 API）+ Vite 作为构建与开发服务器；Element Plus 提供表单、表格等后台组件，减少 UI 工作量；Pinia 管理登录态（令牌）。备选 React + Ant Design，最终选 Vue 以贴合用户指定技术栈。

### 3. 数据库：SQLite + SQLAlchemy（可迁移）

MVP 使用 SQLite（零配置、文件即库），通过 SQLAlchemy ORM 定义模型；切换 PostgreSQL/MySQL 仅需更换连接串，无需改业务代码。备选直接上 PostgreSQL 增加部署成本，MVP 阶段收益低。

### 4. 认证：JWT 访问令牌 + bcrypt 密码哈希

单一管理员账号在启动时按配置种子化（用户名/密码哈希），登录成功签发 JWT 访问令牌；受保护接口校验令牌。密码用 bcrypt（passlib）哈希，不存明文。备选 session-cookie 需要服务端会话状态，与无状态 API 目标不符。

### 5. 执行引擎：httpx 同步执行 + 简单断言

用例执行时按请求定义（method/url/headers/body）用 `httpx` 发送请求（设置超时），随后应用断言规则。断言 MVP 支持两类：期望状态码、响应体匹配（包含/相等）。执行结果为 pass/fail/error 三态。执行在请求内同步完成：单个用例一次请求返回结果；案例集顺序执行成员并汇总。备选 Celery 等异步队列对 MVP 过重，后续需要再引入。

### 6. 数据模型

- `users`：管理员账号（MVP 单行，含用户名、密码哈希）。
- `test_cases`：id、name、description、method、url、headers(JSON)、body(JSON)、assertions(JSON)、时间戳。
- `test_case_sets`：id、name、description、时间戳。
- `set_members`：set_id + case_id 多对多关联（一个用例可加入多个案例集）。
- `execution_results`：id、test_case_id、set_run_id(可空)、status、request 快照、response_status、response_body、断言结果(JSON)、error、时间戳。

### 7. 项目结构（monorepo）

```
backend/   # FastAPI 应用
frontend/  # Vue 3 应用
```

## Risks / Trade-offs

- **[SSRF 风险] 用例 URL 指向任意地址（含内网）** → MVP 仅单一管理员可触发，风险可控；后续再增加 URL 白名单/内网地址拦截。
- **[同步执行阻塞] 单个请求内同步发 HTTP，慢接口会阻塞 worker** → MVP 用例量小，顺序执行可接受；后续引入后台任务队列。
- **[SQLite 并发限制]** 多进程写库会受限 → MVP 单机开发/演示够用，ORM 已为迁移到 PostgreSQL 预留路径。
- **[断言能力有限]** MVP 仅状态码与响应体匹配 → 后续扩展 JSONPath、响应头、响应时间等断言类型。

## Migration Plan

全新系统，无迁移存量数据：按 tasks.md 顺序搭建后端、前端与执行引擎即可；无回滚策略需要。
