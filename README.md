# A股尾盘主力埋伏策略系统

一个基于量化分析的A股尾盘选股自动化系统，通过实时数据分析捕捉主力资金动向，提供次日交易机会。

## 🚀 项目特点

- **智能选股**：基于多维度评分系统筛选潜力股
- **实时数据**：集成Tushare和GuguData实时行情
- **自动调度**：支持定时自动执行和邮件通知
- **回测优化**：基于历史数据不断优化策略参数
- **风险控制**：多维度风控机制，保障资金安全

## 📊 核心策略

### 主力埋伏策略 v4.1 (优化评分版)

- **执行时间**：14:50（尾盘）
- **选股数量**：每日精选TOP 10只股票
- **核心逻辑**：捕捉尾盘主力资金介入信号
- **评分系统**：基于120只股票历史回测优化

#### 评分权重

| 因素 | 权重 | 说明 |
|------|------|------|
| 乖离率 | 25% | 避免追高风险 |
| 换手率 | 20% | 反映活跃度 |
| 成交额 | 20% | 确保流动性 |
| 价格位置 | 15% | 捕捉强势特征 |
| 涨幅 | 15% | 适中的涨幅表现 |
| 振幅 | 5% | 价格稳定性 |

#### 筛选条件

- 市值：20亿 - 200亿
- 涨幅：0.5% - 8.0%
- 成交额：≥1亿
- 乖离率：≤5%
- 换手率：1.5% - 8.0%

## 🛠️ 技术架构

```
stock_screener/
├── src/                       # 策略核心模块
│   ├── main_force_burial_strategy.py  # 主力埋伏策略
│   ├── config.py                   # 配置管理
│   └── realtime_data_fetcher.py     # 实时数据获取
├── core/                      # 核心功能模块
│   ├── auto_scheduler.py       # 自动调度器
│   ├── email_sender.py         # 邮件发送
│   └── notifier.py             # 通知系统
├── web_app.py                 # Web可视化界面
├── .streamlit/                # Streamlit配置
│   └── config.toml
├── scripts/                   # 辅助脚本
├── requirements.txt           # 依赖包
├── .env.example               # 环境变量模板
└── README.md                  # 项目说明
```

## 🌐 Web应用

本系统提供基于Streamlit的可视化Web界面，支持：

- 📊 **最新选股结果**：查看最新TOP 10推荐股票
- 📜 **历史记录**：追溯历史选股数据
- 🔍 **股票分析**：单只股票详细评分分析
- 🚀 **手动选股**：一键触发选股执行
- ⚙️ **策略配置**：查看当前策略参数

### 本地运行Web应用

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动Web应用
streamlit run web_app.py
```

访问：http://localhost:8501

### 在线部署

**推荐使用 Streamlit Community Cloud**（免费托管）：

1. 访问 [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. 使用GitHub登录
3. 点击 "New app" 部署你的仓库
4. 在Secrets中配置环境变量

详细部署指南请查看：[WEB_DEPLOYMENT.md](WEB_DEPLOYMENT.md)

## 📦 安装部署

### 1. 环境要求

- Python 3.8+
- pip 或 conda

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/stock_screener.git
cd stock_screener
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制环境变量模板并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# API配置
GUGU_APPKEY=your_gugudata_appkey
TUSHARE_TOKEN=your_tushare_token

# 邮件配置
EMAIL_ENABLED=true
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SENDER_EMAIL=your_email@qq.com
SENDER_PASSWORD=your_authorization_code
RECIPIENTS=recipient1@email.com,recipient2@email.com
```

## 🎯 使用方法

### 手动执行

```bash
python src/main_force_burial_strategy.py
```

### 自动调度

```bash
# 启动自动调度器（推荐）
nohup python core/auto_scheduler.py > scheduler.log 2>&1 &
```

调度器会自动在以下时间执行：
- 11:30 - 自适应策略
- 14:50 - 主力埋伏策略v4.1

## 📈 策略表现

基于2025年12月数据回测：

| 指标 | 数值 |
|------|------|
| 选股数量 | 120只 |
| 平均收益 | +0.22% |
| 胜率 | 42% |
| 最佳表现 | 中国高科 +16.47% |

## ⚠️ 风险提示

1. 本系统仅为量化研究工具，不构成投资建议
2. 股市有风险，投资需谨慎
3. 单股仓位建议不超过总资金的10%
4. 设置止损线，建议-3%
5. 请结合个人风险承受能力操作

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 邮件：your_email@example.com

---

*最后更新：2025-12-18*