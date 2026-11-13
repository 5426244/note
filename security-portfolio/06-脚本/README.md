# 06-脚本：运维与检测小工具

三个脚本，都是在 Kali 上实际跑过的，不是抄的模板。

| 脚本 | 语言 | 干什么 | 关键点 |
|---|---|---|---|
| [log_scan.py](./log_scan.py) | Python | 逐行读 apache 访问日志，用关键词规则表匹配出可疑请求 | `with open()` + `errors="ignore"` + 大小写归一 + 一行只报一次 |
| [disk_alert.sh](./disk_alert.sh) | Shell | 磁盘使用率超过 80% 时告警 | `df` + `awk` 取第 5 列 + `tr -d '%'` 去百分号 |
| [log_rotate.sh](./log_rotate.sh) | Shell | 删除 apache 日志目录下超过 7 天的 `.gz` | `find -mtime +7 -delete -print` + 先判目录存在 |

---

## log_scan.py

```bash
python3 log_scan.py                    # 默认扫 /var/log/apache2/access.log
sudo python3 log_scan.py               # 该文件普通用户读不了，要 sudo
python3 log_scan.py /tmp/fake.log      # 扫指定文件
```

**规则表**（`RULES` 字典）：`union select` / `cmd=` / `/shell.php` / `password=` / `../` / `.git/config`

**核心逻辑**：

```
逐行读取 → strip() 去换行 → 跳过空行 → lower() 转小写 → 逐条规则匹配 → 命中即记录并 break
```

**为什么 `break`**：一行只报一次，否则 `/shell.php?cmd=whoami` 会同时命中 `cmd=` 和 `/shell.php`，刷两条。

**为什么要 `errors="ignore"`**：真实访问日志里有大量攻击者发来的乱码（`%e3%80%...`），不加这句程序遇到坏字符就崩。

---

## disk_alert.sh

```bash
chmod +x disk_alert.sh
./disk_alert.sh
```

**来源链**：`df -h` 的输出 → `grep -v tmpfs` 排除临时文件系统 → `while read` 逐行 → `awk '{print $5}'` 取使用率 → `tr -d '%'` 去掉百分号变成纯数字 → 数字比较。

**`2>/dev/null` 在 `[ "$usage" -ge "$THRESHOLD" ]` 后面**：`df` 第一行标题行的 `$5` 是文字 `Use%`，不是数字，比较会报错，这句把错误吞掉。

---

## log_rotate.sh

```bash
chmod +x log_rotate.sh
sudo ./log_rotate.sh
```

**实测输出**（2026-11-13）：

```
=== 清理前 ===
（列出 33 个 .gz 文件，日期从 Oct 29 到 Nov 16）
=== 删除 7 天前的 .gz 文件 ===
/var/log/apache2/error.log.9.gz
/var/log/apache2/access.log.6.gz
...
=== 清理后剩多少 ===
（剩余 9 个，日期都是 Nov 6 之后）
```

**踩过的坑**：最初写的是 `-delete -verbose`，Kali 的 find 报 `find: unknown predicate '-verbose'`。改成 `-delete -print` 后正常。

**注意**：`-mtime +7` 是"修改时间超过 7 天"，按 24 小时向上取整计算。实验环境设 7 天是为了看效果，生产环境按等保要求应至少保存 **六个月**。

---

## 三件面试会问的事

**1. 你写过什么脚本？**
磁盘使用率告警、日志轮转清理、访问日志关键词扫描。

**2. 日志扫描是怎么做的？**
逐行读，转小写做归一化，再拿规则表里的关键词逐个匹配。这是最粗的一层特征匹配，真实场景还要正则、上下文判断和降噪。写它的目的是理解检测引擎的骨架：**归一化 → 规则匹配 → 告警**。

**3. 为什么要 `-mtime +7` 而不是 `-mtime 7`？**
`-mtime 7` 只匹配"第 7 天那一天"，`-mtime +7` 才匹配"超过 7 天"。日志清理要的是"超过"，不是"正好那一天"。
