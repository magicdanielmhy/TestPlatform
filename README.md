# 自动化测试平台（MVP）

基于 Python (FastAPI) 后端 + Vue 3 前端的自动化测试平台 MVP，打通「登录 → 管理测试用例 → 组织测试案例集 → 执行接口测试 → 查看结果」的核心闭环。

## 功能

- **登录认证**：单一管理员账号，JWT 令牌保护业务接口。
- **测试用例管理**：用例的增删改查，包含请求方法、URL、请求头、请求体与断言规则。
- **测试案例集**：把用例分组组织，管理案例集成员。
- **接口测试执行**：执行单个用例或整个案例集，记录并查看执行结果（通过/失败/错误）。

## 技术栈

- **后端**：FastAPI、SQLAlchemy、SQLite（可迁移 PostgreSQL/MySQL）、PyJWT、bcrypt、httpx
- **前端**：Vue 3、Vite、Element Plus、Pinia、vue-router、axios

## 目录结构

- `backend/`：FastAPI 应用（`app/`）与 pytest 测试（`tests/`）
- `frontend/`：Vue 3 单页应用
- `openspec/`：OpenSpec 变更与规格

## 环境要求

- Python 3.10+
- Node.js 18+

## 启动后端

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\activate
# Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
# 必填环境变量：SECRET_KEY、ADMIN_USERNAME、ADMIN_PASSWORD。
# 可复制 .env.example 为 .env 并用 --env-file .env 加载，或在 shell 中 export。
uvicorn app.main:app --reload --port 8000
```

接口文档：http://localhost:8000/docs

管理员账号由环境变量 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 提供（必填，无默认值），JWT 密钥由 `SECRET_KEY` 提供（必填）。

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173（已配置 `/api` 与 `/health` 代理到 http://localhost:8000）。

## 运行后端测试

```bash
cd backend
pytest
```

## 接口示例

登录：

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

创建含断言的用例：

```bash
curl -X POST http://localhost:8000/api/test-cases \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "健康检查",
    "method": "GET",
    "url": "http://localhost:8000/health",
    "assertions": [
      {"type": "status", "expected": 200},
      {"type": "body", "expected": "ok", "operator": "contains"}
    ]
  }'
```

执行单个用例 / 整个案例集：

```bash
curl -X POST http://localhost:8000/api/test-cases/<case_id>/execute \
  -H "Authorization: Bearer <token>"

curl -X POST http://localhost:8000/api/test-case-sets/<set_id>/execute \
  -H "Authorization: Bearer <token>"
```
