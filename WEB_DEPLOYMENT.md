# A股选股策略系统 - Web应用部署指南

## 部署选项对比

| 平台 | 推荐度 | 说明 | 费用 |
|------|--------|------|------|
| **Streamlit Community Cloud** | ⭐⭐⭐⭐⭐ | 官方托管，专为Streamlit设计 | 免费 |
| **Railway** | ⭐⭐⭐⭐ | 支持Streamlit，部署简单 | 免费额度 |
| **Render** | ⭐⭐⭐⭐ | 支持Streamlit，稳定 | 免费额度 |
| **Heroku** | ⭐⭐⭐ | 老牌平台，现已收费 | 付费 |

---

## 方案一：Streamlit Community Cloud（推荐）

这是Streamlit官方提供的免费托管服务，最适合部署Streamlit应用。

### 步骤1：准备代码仓库

```bash
# 确保所有文件已提交到GitHub
git add .
git commit -m "Add Streamlit web application"
git push origin main
```

### 步骤2：部署到Streamlit Cloud

1. 访问 [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. 点击 "Sign up" 或 "Log in"（使用GitHub账号登录）
3. 点击 "New app"
4. 填写部署信息：
   - **Repository**: vampire-maker/stock-screener
   - **Branch**: main
   - **Main file path**: web_app.py
5. 点击 "Deploy"

### 步骤3：配置环境变量

在Streamlit Cloud部署页面添加以下Secrets：

| 变量名 | 值 |
|--------|-----|
| `TUSHARE_TOKEN` | 你的Tushare Token |
| `GUGU_APPKEY` | `SQSM4ASGQT6UN363PWA9M6256764WYBS` |
| `EMAIL_ENABLED` | `true` |
| `SMTP_SERVER` | `smtp.qq.com` |
| `SMTP_PORT` | `587` |
| `SENDER_EMAIL` | 你的QQ邮箱 |
| `SENDER_PASSWORD` | 你的QQ邮箱授权码 |
| `RECIPIENTS` | 接收邮箱（逗号分隔） |

### 步骤4：访问应用

部署完成后，你会获得一个类似 `https://your-app-name.streamlit.app` 的URL。

---

## 方案二：使用FastAPI + Vercel

如果必须使用Vercel，需要将Streamlit转换为FastAPI应用。

### 当前状态

由于Streamlit需要持久进程，而Vercel是无服务器架构，我们推荐使用以下替代方案：

**选项A：使用Railway（类似Vercel体验）**

1. 访问 [https://railway.app](https://railway.app)
2. GitHub登录
3. "New Project" → "Deploy from GitHub repo"
4. 选择 `stock-screener` 仓库
5. 配置环境变量（同上）
6. Railway会自动检测Streamlit应用并部署

**选项B：使用Render**

1. 访问 [https://render.com](https://render.com)
2. GitHub登录
3. "New" → "Web Service"
4. 连接GitHub仓库
5. 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run web_app.py --server.port=$PORT`
6. 添加环境变量
7. 部署

---

## 本地运行

### 开发环境运行

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动Web应用
streamlit run web_app.py
```

访问：http://localhost:8501

### 后台运行（服务器部署）

```bash
# 使用nohup后台运行
nohup streamlit run web_app.py --server.port 8501 --server.headless true > streamlit.log 2>&1 &

# 或使用screen
screen -S stock_screener
streamlit run web_app.py --server.port 8501
# 按 Ctrl+A+D 退出screen
```

---

## 环境变量配置

创建 `.env` 文件（本地开发）：

```bash
# Tushare配置
TUSHARE_TOKEN=your_tushare_token_here

# GuguData配置
GUGU_APPKEY=SQSM4ASGQT6UN363PWA9M6256764WYBS

# 邮件配置
EMAIL_ENABLED=true
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SENDER_EMAIL=your_email@qq.com
SENDER_PASSWORD=your_qq_auth_code
RECIPIENTS=recipient1@qq.com,recipient2@qq.com
```

⚠️ **重要**：`.env` 文件包含敏感信息，已在 `.gitignore` 中排除，不要上传到Git！

---

## Web应用功能说明

### 页面导航

| 页面 | 功能描述 |
|------|----------|
| 🏠 首页 | 系统概览、今日推荐TOP5 |
| 📊 最新选股 | 查看最新一次选股结果 |
| 📜 历史记录 | 查看最多30次历史选股记录 |
| 🔍 股票分析 | 单只股票详细分析 |
| ⚙️ 策略配置 | 当前策略参数展示 |
| 🚀 手动选股 | 手动触发选股执行 |

### 核心功能

1. **实时选股**：点击"开始选股"按钮立即执行策略
2. **结果展示**：表格展示TOP 10推荐股票
3. **评分分析**：查看每只股票的详细评分组成
4. **历史追溯**：查看所有历史选股记录

---

## 故障排查

### 问题1：ModuleNotFoundError

```bash
# 确保在虚拟环境中安装了所有依赖
source venv/bin/activate
pip install -r requirements.txt
```

### 问题2：API调用失败

- 检查 `.env` 文件中的API Key是否正确
- GuguData需要等待订阅生效（通常5-10分钟）

### 问题3：邮件发送失败

- 检查SMTP端口号（587用于STARTTLS，465用于SSL）
- 确认QQ邮箱授权码已开启并正确配置

---

## 更新部署

```bash
# 修改代码后
git add .
git commit -m "Update web application"
git push origin main

# Streamlit Cloud会自动检测并重新部署
# Railway/Render需要手动触发 redeploy
```

---

## 费用说明

| 平台 | 免费额度 | 超出后 |
|------|----------|--------|
| Streamlit Cloud | 无限制 | - |
| Railway | $5/月免费额度 | 按使用量付费 |
| Render | 750小时/月 | 按使用量付费 |

⚠️ **风险提示**：本系统仅供量化研究，不构成投资建议。股市有风险，投资需谨慎。
