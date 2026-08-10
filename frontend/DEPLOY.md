# 部署指南 - Smart Suite Next.js Frontend

## 域名：geo-smartsuite.app (Vercel)

---

## 方式一：Vercel CLI（最快，一条命令）

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署到 Vercel（首次会引导登录和项目配置）
cd frontend
vercel

# 部署到生产环境
vercel --prod
```

部署后 Vercel 会给你一个 URL（如 `smartsuite-xxx.vercel.app`），然后在 Vercel Dashboard 绑定 `geo-smartsuite.app` 域名。

---

## 方式二：GitHub 自动部署（推荐长期方案）

1. **推送到 GitHub**
```bash
cd frontend
git init
git add .
git commit -m "feat: Smart Suite Next.js frontend"
git remote add origin https://github.com/YOUR_ORG/smartsuite-web.git
git push -u origin main
```

2. **Vercel 导入**
- 访问 https://vercel.com/new
- 导入 GitHub 仓库
- Framework: Next.js (自动检测)
- Root Directory: `./` (如果是 monorepo 则选 `frontend/`)

3. **设置环境变量**
- `NEXT_PUBLIC_API_URL` = 你的 FastAPI 后端地址
  - 如果后端在 EC2: `http://YOUR_EC2_IP:8000`
  - 如果后端在 Lambda: `https://xxx.execute-api.us-east-1.amazonaws.com`

4. **绑定域名**
- Project Settings → Domains → Add `geo-smartsuite.app`
- 按照 Vercel 提示在域名注册商添加 DNS 记录

---

## 方式三：AWS Amplify（如果偏好 AWS 生态）

```bash
# 安装 Amplify CLI
npm i -g @aws-amplify/cli

# 初始化
amplify init

# 部署
amplify push
```

---

## 后端 API 地址配置

Next.js 前端需要连接到 FastAPI 后端。确保：

1. **CORS 已配置**（已在 `api/main.py` 中设置 `geo-smartsuite.app`）
2. **环境变量正确**：
   - 本地开发: `.env.local` → `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - 生产环境: Vercel 环境变量 → 你的后端实际地址

### 后端部署选项：
- **当前**: EC2 直接部署 (uvicorn)
- **建议**: Lambda + API Gateway（已有 `lambda/` 目录配置）

---

## 快速验证

部署后访问 `https://geo-smartsuite.app`：
1. 应看到登录页面
2. 输入用户名（在 `output/users.json` 的 `allowed` 列表中）
3. 成功登录后进入智库页面

---

## 注意事项

- `node_modules/` 和 `.next/` 不需要上传到 S3（它们太大了！）
- 建议在 `.gitignore` 中排除这些目录
- Vercel 部署时会自动运行 `npm install` + `npm run build`
