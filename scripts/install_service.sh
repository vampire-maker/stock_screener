#!/bin/bash

echo "🔧 安装股票筛选自动服务"
echo "================================"

# 获取当前目录
CURRENT_DIR=$(pwd)
SERVICE_NAME="stock-screener"

# 创建systemd服务文件
cat > /tmp/${SERVICE_NAME}.service << EOF
[Unit]
Description=Stock Screener Auto Scheduler
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=SMTP_SERVER=smtp.qq.com
Environment=SMTP_PORT=587
Environment=SENDER_EMAIL=361612558@qq.com
Environment=SENDER_PASSWORD=eandpognegzacbda
Environment=RECEIVER_EMAIL=hf.zhang512@outlook.com,gxs0710@hotmail.com
ExecStart=/usr/bin/python3 $CURRENT_DIR/auto_scheduler.py
Restart=always
RestartSec=10
StandardOutput=append:$CURRENT_DIR/scheduler.log
StandardError=append:$CURRENT_DIR/scheduler_error.log

[Install]
WantedBy=multi-user.target
EOF

echo "📝 服务文件已创建: /tmp/${SERVICE_NAME}.service"
echo
echo "💡 安装说明:"
echo "  1. 复制服务文件到系统目录:"
echo "     sudo cp /tmp/${SERVICE_NAME}.service /etc/systemd/system/"
echo
echo "  2. 重新加载systemd:"
echo "     sudo systemctl daemon-reload"
echo
echo "  3. 启用服务 (开机自启):"
echo "     sudo systemctl enable ${SERVICE_NAME}"
echo
echo "  4. 启动服务:"
echo "     sudo systemctl start ${SERVICE_NAME}"
echo
echo "  5. 查看服务状态:"
echo "     sudo systemctl status ${SERVICE_NAME}"
echo
echo "  6. 查看日志:"
echo "     sudo journalctl -u ${SERVICE_NAME} -f"
echo
echo "⚠️  注意: 此服务适用于Linux系统，macOS用户请使用启动脚本"
echo "================================"