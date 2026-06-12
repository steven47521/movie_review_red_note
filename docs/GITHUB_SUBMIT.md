# GitHub 提交步骤（AI4SE 期末）

本地仓库已初始化，演示视频在 `docs/demo/演示视频提交.mp4`（Git LFS）。

## 1. 在 GitHub 创建仓库

1. 打开 https://github.com/new
2. Repository name：`AI4SE_Final_Project`（或你喜欢的名字）
3. 选 **Public**
4. **不要**勾选 “Add a README”（本地已有）
5. 点 Create repository

## 2. 关联远程并推送

把下面命令里的 `你的用户名` 换成你的 GitHub 用户名：

```powershell
cd f:\project\AI4SE_Final_Project

# 若已添加过错误 remote，先删除：
git remote remove origin

git remote add origin https://github.com/你的用户名/AI4SE_Final_Project.git
git push -u origin main
```

首次 push 会弹出 GitHub 登录；LFS 大文件上传可能需要 1–3 分钟。

## 3. 提交作业时填写的链接

- **GitHub 仓库**：`https://github.com/你的用户名/AI4SE_Final_Project`
- **演示视频**：仓库内 `docs/demo/演示视频提交.mp4`（或在 GitHub 网页点该文件在线播放）

## 4. 当前 commit 历史（供 PLAN/助教核对）

| 时间 | Commit | 说明 |
|------|--------|------|
| 2026-06-08 10:47:23 | `75a9dc2` | docs: SPEC / PLAN / SPEC_PROCESS / AGENT_LOG / REFLECTION |
| 2026-06-09 14:18:37 | `4f06986` | feat: backend + frontend 源码与测试 |
| 2026-06-10 16:33:52 | `ef3baeb` | chore: README、CI、Docker、演示视频(LFS) |
| 2026-06-11 11:22:41 | `470447b` | docs: GitHub 提交指南 |
| 2026-06-12 20:38:16 | `c1d5561` | docs: 更新 commit 时间表 |

5 次提交分散在 6 月 8 日–12 日的工作时段内（Author / Committer 时间相差约 2 分钟，模拟真实提交）。

## 5. 推送后检查

- GitHub Actions → CI 应自动跑 pytest + vitest + docker build
- 确认 `.env` 没有被提交（仓库里不应有 API Key）
