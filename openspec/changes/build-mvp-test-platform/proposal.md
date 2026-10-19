# Proposal

## Why

团队需要一套统一的自动化测试平台，用来集中管理测试用例、按"测试案例集"组织用例，并直接执行 HTTP/API 接口自动化测试、查看执行结果。当前测试用例分散、接口测试依赖手工脚本，难以复用与沉淀。先以 MVP 验证核心闭环：登录 → 管理用例 → 组织案例集 → 执行接口测试 → 查看结果。

## What Changes

- 新增**登录认证**：单一管理员账号，基于 JWT 的会话与访问控制。
- 新增**测试用例管理**：测试用例的创建、查看、编辑、删除。
- 新增**测试案例集**：将测试用例分组组织（一个用例可归属到案例集）。
- 新增**接口测试执行**：用 Python 执行 HTTP/API 接口用例（请求、断言），记录并展示执行结果。
- 技术栈：后端 Python，前端 Vue。

## Capabilities

### New Capabilities

- `user-auth`: 登录认证与访问控制（单一管理员账号、JWT 会话）。
- `test-case-management`: 测试用例的定义与增删改查。
- `test-case-sets`: 测试案例集，把测试用例分组组织。
- `test-execution`: 执行 HTTP/API 接口测试并记录、查看结果。

### Modified Capabilities

（无，本项目为全新系统）

## Impact

- **后端**：Python 服务（REST API、认证、用例/案例集存储、接口测试执行引擎）。
- **前端**：Vue 单页应用（登录页、用例管理、案例集、执行与结果页）。
- **数据存储**：关系型数据库（SQLite/PostgreSQL/MySQL）。
- **依赖**：Python Web 框架、HTTP 客户端库、JWT 库；Vue 及其 UI 组件库。
