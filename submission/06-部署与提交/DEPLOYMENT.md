# 云部署指南（Railway / Render）

> 片语 RedNote — 经典电影小红书创作助手  
> 依赖：Docker 镜像（T13）、MySQL 8、OpenAI + TMDB API Key

## 架构

```text
[Browser] → Frontend (Next.js :3000)
                ↓ NEXT_PUBLIC_API_URL
            Backend (FastAPI :8000) → MySQL 8
```

- **Backend** 与 **Frontend** 各一个 Web 服务（Docker 部署）
- **MySQL** 建议用 **Railway MySQL** 插件（Render 免费层无 MySQL）

---

## 环境变量（必填）

| 变量 | 服务 | 说明 |
|------|------|------|
| `DATABASE_URL` | backend | `mysql+pymysql://user:pass@host:3306/rednote` |
| `OPENAI_API_KEY` | backend | LLM + gpt-image-2 |
| `TMDB_API_KEY` | backend | 影片元数据 |
| `API_SECRET_KEY` | backend | 单用户鉴权 |
| `CORS_ORIGINS` | backend | 前端公网 URL，逗号分隔 |
| `NEXT_PUBLIC_API_URL` | frontend（构建时） | 后端公网 URL，如 `https://rednote-api.onrender.com` |

复制模板：

```bash
cp .env.example .env
```

---

## 方案 A：Render（Frontend + Backend）

### 1. 准备 MySQL（Railway）

1. 登录 [Railway](https://railway.app/) → New Project → **Add MySQL**
2. 在 MySQL 服务 Variables 中复制连接串，转为 SQLAlchemy 格式：
   `mysql+pymysql://USER:PASS@HOST:PORT/railway`
3. 记下该 `DATABASE_URL`

### 2. 部署 Backend

1. [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**
2. 连接本仓库，Render 读取根目录 `render.yaml`
3. 服务 `rednote-api` 环境变量填入：
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `TMDB_API_KEY`
   - `CORS_ORIGINS=https://<your-frontend-host>`
4. 部署完成后记下 API URL，例如：  
   `https://rednote-api.onrender.com`

### 3. 部署 Frontend

1. 同一 Blueprint 中的 `rednote-web`
2. 设置构建参数 / 环境变量：  
   `NEXT_PUBLIC_API_URL=https://rednote-api.onrender.com`
3. 重新部署 frontend（Next.js 需在**构建时**注入 `NEXT_PUBLIC_*`）

### 4. 验证

```bash
curl https://rednote-api.onrender.com/health
# {"status":"ok"}

curl -X POST https://rednote-api.onrender.com/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"title":"肖申克的救赎","year":1994}'
```

浏览器打开 frontend URL → `/dashboard/create` 走完整流程。

---

## 方案 B：Railway（全栈）

### 1. MySQL

New Project → **Add MySQL** → 复制 `DATABASE_URL`（转为 `mysql+pymysql://...`）

### 2. Backend 服务

1. **New Service** → GitHub Repo → Root Directory: `backend`
2. Railway 自动检测 `backend/Dockerfile`
3. Variables：

```env
DATABASE_URL=mysql+pymysql://...
OPENAI_API_KEY=sk-...
TMDB_API_KEY=...
API_SECRET_KEY=...
CORS_ORIGINS=https://<frontend>.up.railway.app
```

4. Settings → Networking → **Generate Domain**  
   例：`https://rednote-api-production.up.railway.app`

### 3. Frontend 服务

1. **New Service** → 同一仓库 → Root Directory: `frontend`
2. Variables / Build Args：

```env
NEXT_PUBLIC_API_URL=https://rednote-api-production.up.railway.app
```

3. Generate Domain → 例：`https://rednote-web-production.up.railway.app`
4. 将 frontend URL 写回 backend 的 `CORS_ORIGINS`

### 4. 验证

同 Render 步骤 4。

---

## 公网 URL 登记（课程交付）

部署完成后，更新根目录 `README.md` 的 **Production URLs** 一节：

```markdown
## Production URLs

| 环境 | URL |
|------|-----|
| Frontend | https://YOUR-FRONTEND-URL |
| Backend API | https://YOUR-BACKEND-URL/health |
```

---

## 常见问题

| 问题 | 处理 |
|------|------|
| Frontend 调 API 跨域失败 | 检查 `CORS_ORIGINS` 是否包含前端完整 origin（无尾斜杠） |
| `NEXT_PUBLIC_API_URL` 不生效 | 修改后需**重新构建** frontend 镜像 |
| 数据库连接失败 | 确认 `DATABASE_URL` 使用 `mysql+pymysql://` 前缀 |
| Render 免费实例休眠 | 首次访问需等待 30–60s 冷启动 |

---

## GHCR 镜像（可选）

CI 在 `main` 分支 push 后发布：

- `ghcr.io/<owner>/<repo>/backend:latest`
- `ghcr.io/<owner>/<repo>/frontend:latest`

可在 Railway/Render 中选择「Deploy from container image」替代 Dockerfile 构建。
