#!/bin/bash
# disk_alert.sh —— 磁盘使用率告警
# 用法：chmod +x disk_alert.sh && ./disk_alert.sh

THRESHOLD=80

df -h | grep -v tmpfs | while read -r line; do
    usage=$(echo "$line" | awk '{print $5}' | tr -d '%')
    mount=$(echo "$line" | awk '{print $6}')

    if [ "$usage" -ge "$THRESHOLD" ] 2>/dev/null; then
        echo "[ALERT] $mount 使用率 ${usage}%，超过 ${THRESHOLD}%"
    fi
done
