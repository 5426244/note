#!/bin/bash
# log_rotate.sh —— 清理 apache 日志目录下超过指定天数的 .gz 文件
# 用法：chmod +x log_rotate.sh && sudo ./log_rotate.sh

LOG_DIR="/var/log/apache2"
DAYS=7

# 目录不存在就直接退出，避免后面 find 报一堆错
if [ ! -d "$LOG_DIR" ]; then
    echo "目录不存在：$LOG_DIR"
    exit 1
fi

echo "=== 清理前 ==="
ls -lh "$LOG_DIR"/*.gz 2>/dev/null || echo "（没有 .gz 文件）"

echo "=== 删除 ${DAYS} 天前的 .gz 文件 ==="
find "$LOG_DIR" -name "*.gz" -mtime +$DAYS -delete -print

echo "=== 清理后剩多少 ==="
ls -lh "$LOG_DIR"/*.gz 2>/dev/null || echo "（已清空）"
