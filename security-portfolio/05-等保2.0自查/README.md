# 等保 2.0 自查测评 · 本地实验环境

> 对照 GB/T 22239-2019 第三级「安全计算环境」，对本地 Kali 虚拟机做逐项配置核查。
> 测评日期：2026-11-07 20:19 — 11-08 16:20 ｜ 测评人：张野 ｜ 版本：v1.1（已补测）

## 一句话结论

**抽样 10 个控制点：符合 0、部分符合 2、不符合 8、待验证 0 —— 当前不具备第三级安全保护能力。**

最关键的发现是：**口令策略缺失（无失败锁定、密码永不过期）与 Burp 字典爆破能够成功，是同一条因果链的两端。** 而访问日志又把登录口令原样落盘——审计记录本身成了二次泄露源。

## 测评边界（先说清楚）

| 项 | 内容 |
|---|---|
| 被测对象 | Kali Linux 2023.3 虚拟机（192.168.59.128）及其上的 DVWA 靶场 |
| 测评方法 | 配置核查 + 命令验证，**不做渗透测试** |
| 为什么不做渗透 | 靶场本身即为不安全的演示环境，打靶结论没有测评意义。等保测的是「防护措施有没有做到」，不是「能不能打穿」 |

渗透测试结论见 [`01-Metasploitable2-渗透报告`](../01-Metasploitable2-渗透报告/) 与 [`02-DVWA-Web漏洞实战`](../02-DVWA-Web漏洞实战/)。

## 结果汇总

| 判定 | 数量 | 控制点 |
|---|---|---|
| 符合 | 0 | — |
| 部分符合 | 2 | 访问控制、个人信息保护 |
| 不符合 | 8 | 身份鉴别、安全审计、入侵防范、恶意代码防范、数据保密性、数据备份恢复、剩余信息保护（会话）、剩余信息保护（介质） |
| 待验证 | 0 | 原 3.8 会话项已补测 |

## 逐项记录

### 3.1 身份鉴别（8.1.4.1）— 不符合

```bash
sudo grep -E "PASS_MAX_DAYS|PASS_MIN_LEN" /etc/login.defs
sudo grep pam_faillock /etc/pam.d/common-auth
```

```
PASS_MAX_DAYS   99999
#PASS_MIN_LEN
（第二条无输出）
```

- `PASS_MAX_DAYS 99999` = 密码约 273 年才过期，等于永不过期
- `PASS_MIN_LEN` 被注释，没有最小长度限制
- 未加载 `pam_faillock`，**没有任何失败锁定**

**这直接解释了 Burp Intruder 能无限次尝试直到命中**（实测见 [`02-DVWA-Web漏洞实战`](../02-DVWA-Web漏洞实战/)）。

### 3.2 访问控制（8.1.4.2）— 部分符合

```bash
sudo cat /etc/passwd | grep -v nologin | grep -v false
```

可登录账号：`root`（UID 0）、`sync`、`postgres`、`kali`（UID 1000）、`devuser`（UID 1001）。

UID 0 账号只有 `root` 一个，这点是对的。但存在 `devuser` 这类用途不明的通用账号，无法证明账号独立与职责分离。

### 3.3 安全审计（8.1.4.3）— 不符合

```bash
sudo systemctl status systemd-journald
ls -la /var/log/journal/ 2>/dev/null || echo "无持久化日志"
sudo grep "password=" /var/log/apache2/access.log | head -5
```

**实测结果一：日志未持久化**

```
Active: active (running)
Collecting audit messages is disabled.
（ls 无输出，/var/log/journal 不存在）
```

**实测结果二：访问日志明文记录口令**

```
192.168.59.128 - - [08/Nov/2026:10:24:00 +0800] "GET /DVWA/vulnerabilities/brute/
?username=admin&password=password&Login=Login HTTP/1.1" 200 1821
```

两个问题叠加：
1. 日志只写在内存 `/run/log/journal`，重启即丢，无法满足「保存不少于六个月」
2. Apache 把完整 URL 原样落盘，**登录口令明文可见**，未做任何脱敏

**审计记录本身成了二次泄露源。**

> ⚠️ 排查提醒：用 `grep -i password /var/log/ -r` 会命中 `boot.log` 里的
> `systemd-ask-password-plymouth.path` —— 那是 **systemd 服务名，不是泄露的密码**。
> 必须用 `grep "password="` 精确定位。

### 3.4 入侵防范（8.1.4.4）— 不符合

```bash
sudo ss -tlnp
```

| 端口 | 服务 | 监听地址 | 判断 |
|---|---|---|---|
| 22 | OpenSSH 9.3p2 | 0.0.0.0 | 允许口令登录，存在爆破风险 |
| 80 | Apache 2.4.57 | `*:80` | **对外暴露，且承载两个漏洞靶场** |
| 3306 | MariaDB 10.11.4 | 127.0.0.1 | 配置正确 |

> ⚠️ 命令别打错：`sudo ss -ss -tlnp` 会报 `ss: invalid option -- '-'`，正确是 `sudo ss -tlnp`。

### 3.5 恶意代码防范（8.1.4.5）— 不符合

```bash
which clamav || echo "未安装防病毒"    # → clamav not found
```

### 3.6 数据保密性（8.1.4.8）— 不符合

```bash
sudo grep -i "ssl\|tls" /etc/apache2/sites-enabled/*
```

只匹配到一行注释 `#LogLevel info ssl:warn`，**没有任何 TLS 站点**。

**补充证据**：登录表单用 GET 提交，口令出现在 URL 查询串中并被写入访问日志。口令同时暴露在三处：浏览历史、代理日志、服务器访问日志。

### 3.7 数据备份恢复（8.1.4.9）— 不符合

```bash
crontab -l 2>/dev/null; ls -la /etc/cron.d/ /etc/cron.daily/
ls -la /var/backups/
```

```
no crontab for root
/etc/cron.daily: apache2  apt-compat  dpkg  dbus  man-db  sysstat
/var/backups:    仅 apt.extended_states.0（2023-08-22）
```

**有系统级备份，没有业务数据备份。**
- `apt-compat` 备份软件包索引
- `dpkg` 备份包数据库
- `e2scrub_all` 是文件系统检查

**没有一个针对 DVWA 数据库、靶场配置或测试报告的备份任务。**

### 3.8 剩余信息保护（会话）— 不符合

```bash
ls -la ~/.mozilla/firefox/*.default-esr/cookies.sqlite
```

```
-rw-r--r-- 1 root root 524288 Nov  8 16:13 .../cookies.sqlite
```

浏览器会话库以**未加密的明文 SQLite** 持久化在磁盘，权限 644（同机其他用户可读）。退出登录后文件不删除。且该文件归 root 所有，说明**浏览器曾以 root 运行**。

### 3.9 个人信息保护（8.1.4.11）— 部分符合

```bash
mysql -h 127.0.0.1 -u dvwa -p'p@ssw0rd' dvwa -e "select user,password from users;"
```

```sql
desc users;
user_id    int(6) PRI
user       varchar(15)
password   varchar(32)    ← 32 位，正好是 MD5 长度
first_name / last_name / avatar / last_login / failed_login / role / account_enabled
```

5 个账号口令均为 32 位十六进制串，如 `admin` = `5f4dcc3b5aa765d61d8327deb882cf99`。

这是**无盐 MD5**。本次已用公开彩虹表把它还原成 `password` —— 属于「加了哈希但没加盐」。

> 一个值得注意的细节：表里设计了 `failed_login` 和 `account_enabled` 两列，说明系统**原本设计了账号管理能力**，但失败计数只记数不锁定，等于字段设计到位、策略没落地。

### 3.10 剩余信息保护（测试产物）— 不符合

```bash
sudo find / -name "*.bak" -o -name "*.nmap" -o -name "wget-log*" 2>/dev/null | grep -v "/proc\|/sys"
ls -la ~/Desktop/
```

**实测结果一：全盘搜索**

```
/usr/bin/dbkgbackup  /usr/bin/wrbsp_st_backup  /usr/lib/...
/home/kali/.mozilla/firefox/.../sessionstore-backups/
/var/lib/dpkg/info/...
```

**全部是操作系统自带组件，初看容易被误判成数据残留。**

**实测结果二：桌面目录**

```
-rw-r--r-- 1 root root 183 Nov  8 18:47 hello.py
-rw-r--r-- 1 root root 145 Nov  8 09:37 test2.php
-rw-r--r-- 1 root root 290 Nov  8 09:09 test.php
```

前一轮残留的 `scan_result.nmap`、`scan.txt`、`pikachu-ready.zip` 已清理，但**命令执行对比实验的 `test.php` 与 `test2.php` 仍在桌面**。

这两个文件包含 `system("ping -c 1 " . $ip)` 形式的命令拼接代码，**一旦被 Web 服务引用即可执行系统命令，等同于一个现成后门。**

## 整改优先级

| 级别 | 问题 | 整改动作 |
|---|---|---|
| **P0** | 无失败锁定 + 密码永不过期 | `pam_faillock` 连错 5 次锁 10 分钟；`PASS_MAX_DAYS 90`；启用 `PASS_MIN_LEN 8` 与复杂度 |
| **P0** | 访问日志明文记录口令 | access_log 敏感参数脱敏；登录改 POST；日志目录收紧权限 |
| **P0** | 80 端口对外 + 承载靶场 | 改监听 `127.0.0.1`；实验结束立即停服；禁止接入办公网 |
| **P0** | 全站明文 HTTP | 启用 TLS，80 强制跳 443；表单改 POST |
| P1 | 日志只在内存 | 创建 `/var/log/journal` 启用持久化；开 auditd；配 `SystemMaxUse` 与远端转发 |
| P1 | 只有系统备份 | 为数据库与业务数据配置每日备份并**验证可恢复**；异地保存 |
| P1 | 无盐 MD5 | 改 bcrypt / Argon2；数据库账号最小权限 |
| P1 | 可执行代码残留桌面 | 建立测试产物清理清单；实验脚本集中存放并设最小权限 |
| P1 | 浏览器会话明文落盘 | 浏览器不以 root 运行；实验结束清理 profile |
| P2 | 无恶意代码防范 | 部署 ClamAV，每日更新 + 定期扫描 |
| P2 | 通用命名账号 | 一人一号；离职或实验结束即删 |

## 面试怎么讲这份报告

**问：你做过等保测评吗？**

> 做过自查，不是正式测评。我对照 GB/T 22239-2019 第三级，从安全计算环境里抽了 10 个控制点，在本地 Kali 上逐条核查配置，结果是 0 符合、2 部分符合、8 不符合、0 待验证。
>
> 最有意思的是能串起来的几条：身份鉴别不符合——没有 `pam_faillock`、密码永不过期；安全审计也不符合——访问日志把 `password=password` 原样落盘。**前者是我能用 Burp 字典爆破成功的根因，后者让爆破过程本身就写进了服务器日志。** 测评的价值就在这，它把「我打进去了」翻译成「你的哪几条防护没做到」。

**问：管理测评和技术测评的区别？**

> 技术测评是敲命令看配置，管理测评是看制度文件、看执行记录、访谈管理员。剩余信息保护、备份介质管理这些条款，命令查不出来，只能找证据。

**问：这次测评有什么你觉得做得对的地方？**

> 全盘 `find` 搜 `*.bak` 命中了一大堆文件，看起来很像数据残留。但我逐条核对发现**全是操作系统自带组件**——dpkg 的备份工具、Mozilla 的会话备份。真正的风险反而是桌面那两个最不起眼的 `test.php`，那是我自己做对比实验写的、带 `system()` 的脚本。**误报比漏报更容易让人下错结论**，测评不能看到命中就写。

## 一句话

**等保测评不是查漏洞，是查「防护措施有没有做到」——漏洞是结果，缺的条款是原因。**
