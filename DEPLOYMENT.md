# 部署指南

本文档介绍如何将项目部署到GitHub和Vercel。

## 📋 部署准备

### 1. 创建GitHub仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角的 "+" 号，选择 "New repository"
3. 填写仓库信息：
   - Repository name: `stock-screener` (或你喜欢的名称)
   - Description: A股尾盘主力埋伏策略系统
   - 选择 Public 或 Private（推荐Private，因为包含API密钥）
4. 不要勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

### 2. 配置Git

```bash
# 设置你的Git用户名和邮箱（如果还没设置）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交初始版本
git commit -m "Initial commit: A股尾盘主力埋伏策略系统"

# 添加远程仓库
git remote add origin https://github.com/yourusername/stock-screener.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 3. 部署到Vercel（可选）

Vercel主要用于部署Web应用。如果你的项目包含Web界面，可以按以下步骤部署：

#### 方案一：部署展示页面

1. 创建简单的Web展示页面：

```bash
# 创建vercel.json
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/",
      "dest": "/index.html"
    }
  ]
}
EOF

# 创建index.html（展示页面）
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A股尾盘主力埋伏策略系统</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #3b82f6;
            --primary-dark: #2563eb;
            --text: #1f2937;
            --text-light: #6b7280;
            --bg: #f9fafb;
            --card: #ffffff;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        .logo {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: var(--text-light);
            font-size: 1.2rem;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        .feature-card {
            background: var(--card);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            background: var(--card);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 3rem;
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }
        .stat-label {
            color: var(--text-light);
        }
        .cta {
            text-align: center;
            margin: 3rem 0;
        }
        .btn {
            display: inline-block;
            padding: 0.75rem 2rem;
            background: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            transition: background 0.2s;
        }
        .btn:hover {
            background: var(--primary-dark);
        }
        .footer {
            text-align: center;
            color: var(--text-light);
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e5e7eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🚀 A股尾盘主力埋伏策略系统</div>
            <div class="subtitle">基于量化分析的智能选股系统</div>
        </div>

        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>智能选股</h3>
                <p>基于多维度评分系统，每日精选TOP 10潜力股</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3>实时数据</h3>
                <p>集成Tushare和GuguData实时行情数据</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3>自动执行</h3>
                <p>支持定时自动执行和邮件通知</p>
            </div>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">14:50</div>
                <div class="stat-label">尾盘执行时间</div>
            </div>
            <div class="stat">
                <div class="stat-value">42%</div>
                <div class="stat-label">历史胜率</div>
            </div>
            <div class="stat">
                <div class="stat-value">+16.47%</div>
                <div class="stat-label">最佳表现</div>
            </div>
            <div class="stat">
                <div class="stat-value">120+</div>
                <div class="stat-label">回测样本</div>
            </div>
        </div>

        <div class="cta">
            <a href="https://github.com/yourusername/stock-screener" class="btn">查看源代码</a>
        </div>

        <div class="footer">
            <p>⚠️ 风险提示：本系统仅供量化研究，不构成投资建议。股市有风险，投资需谨慎。</p>
            <p>© 2025 Stock Screener. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
EOF
```

2. 安装Vercel CLI并部署：

```bash
# 安装Vercel CLI
npm i -g vercel

# 登录Vercel
vercel login

# 部署项目
vercel

# 按提示操作：
# - Set up and deploy "~/stock-screener"? [Y/n] y
# - Which scope do you want to deploy to? 选择你的账号
# - Link to an existing project? [N/y] n
# - What's your project's name? stock-screener
# - In which directory is your code located? ./
# - Want to override the settings? [N/y] n
```

#### 方案二：使用GitHub Actions（推荐）

1. 在GitHub仓库中创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'

    - name: Install Vercel CLI
      run: npm install --global vercel@latest

    - name: Pull Vercel Environment Information
      run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

    - name: Build Project Artifacts
      run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

    - name: Deploy Project Artifacts to Vercel
      run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

2. 配置Vercel项目：

- 访问 [Vercel](https://vercel.com)
- 导入GitHub仓库
- 配置环境变量（可选）
- 自动部署

## 🔐 安全注意事项

1. **API密钥保护**
   - 绝不要将真实的API密钥提交到Git
   - 使用环境变量存储敏感信息
   - 在GitHub仓库中使用Secrets存储密钥

2. **.gitignore检查**
   - 确保 `.env` 在 `.gitignore` 中
   - 不要提交日志文件和数据文件
   - 定期检查提交历史，确保没有敏感信息

## 📌 后续维护

### 1. 更新项目

```bash
# 查看修改
git status

# 添加修改
git add .

# 提交修改
git commit -m "Update: 描述你的修改"

# 推送到GitHub
git push
```

### 2. 版本管理

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

### 3. 自动化部署

- 使用GitHub Actions实现CI/CD
- 配置自动化测试
- 设置部署钩子

## 🚀 快速部署命令总结

```bash
# 1. 准备项目
git init
git add .
git commit -m "Initial commit"

# 2. 连接GitHub
git remote add origin https://github.com/yourusername/stock-screener.git
git push -u origin main

# 3. 部署到Vercel（可选）
npm i -g vercel
vercel

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入真实配置
```

## 📞 获取帮助

如果遇到问题，可以：

1. 查看 [GitHub文档](https://docs.github.com)
2. 查看 [Vercel文档](https://vercel.com/docs)
3. 提交Issue到项目仓库
4. 联系项目维护者

---

*最后更新：2025-12-18*