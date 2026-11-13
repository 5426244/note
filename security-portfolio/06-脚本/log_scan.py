# -*- coding: utf-8 -*-
"""
log_scan.py —— 日志关键词检测脚本

用法：
    python3 log_scan.py                      # 默认扫 /var/log/apache2/access.log
    sudo python3 log_scan.py                # 同上，需要 sudo（该文件普通用户读不了）
    python3 log_scan.py /tmp/fake.log       # 扫指定的日志文件

面试可以这么说：
    对 access.log 逐行读取，统一转小写后用关键词规则表匹配，
    命中即记录。这是最粗的一层特征匹配，真实场景还要正则、上下文判断和降噪。
    写过它的目的是理解检测引擎的骨架：归一化 → 规则匹配 → 告警。
"""

import sys
import os

# ---------------- 配置 ----------------

# 默认日志文件路径
DEFAULT_LOG = "/var/log/apache2/access.log"

# 规则表：键 = 关键词（小写），值 = 命中后的告警名称
# 注意：字典是有顺序的（Python 3.7+），先写的先试
RULES = {
    "union select": "SQL 注入",
    "cmd=": "命令执行",
    "/shell.php": "疑似 webshell",
    "password=": "疑似口令泄露",
    "../": "疑似目录穿越",
    ".git/config": "版本库泄露探测",
}

# ---------------- 主逻辑 ----------------


def scan(log_path):
    """
    读日志文件，返回告警列表。
    每条告警是一个字典：{"type": 攻击类型, "keyword": 命中的词, "line": 原始行}
    """
    alerts = []

    # open() 用 with 包住：代码块结束时文件自动关闭
    # encoding="utf-8"  按 UTF-8 解码
    # errors="ignore"   遇到乱码字符直接跳过，否则会崩溃
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # 第 1 步：跳过空行
            line = line.strip()
            if not line:
                continue

            # 第 2 步：统一转小写，防大小写混淆（UnIoN SeLeCt）
            low = line.lower()

            # 第 3 步：拿每条规则挨个试
            for keyword in RULES:
                if keyword in low:
                    alerts.append({
                        "type": RULES[keyword],
                        "keyword": keyword,
                        "line": line,
                    })
                    break  # 一行只报一次，避免同一行刷屏

    return alerts


def print_report(alerts, log_path):
    """把告警按类型归组后打印"""
    print(f"扫描文件：{log_path}")
    print(f"共发现 {len(alerts)} 条告警\n")

    if not alerts:
        print("（无告警）")
        return

    # 按类型统计
    counts = {}
    for a in alerts:
        counts[a["type"]] = counts.get(a["type"], 0) + 1

    print("按类型统计：")
    for t, n in counts.items():
        print(f"  {t}: {n} 条")
    print()

    # 逐条打印
    for a in alerts:
        print(f"[!] {a['type']}  ← 关键词 {a['keyword']}")
        print(f"    {a['line']}")
        print()


def main():
    # 命令行参数 > 默认路径
    log_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG

    if not os.path.exists(log_path):
        print(f"文件不存在：{log_path}")
        print("提示：/var/log/apache2/access.log 需要 sudo 才能读")
        sys.exit(1)

    try:
        alerts = scan(log_path)
    except PermissionError:
        print(f"没有权限读：{log_path}")
        print("试试：sudo python3 log_scan.py")
        sys.exit(1)

    print_report(alerts, log_path)


if __name__ == "__main__":
    main()
