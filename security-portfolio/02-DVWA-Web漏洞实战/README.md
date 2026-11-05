# DVWA Web 漏洞实战（个人练习）

在 DVWA 靶场上手工复现六类典型 Web 漏洞，并理解对应的防御原理。

| 漏洞 | 文件 | 难度覆盖 | 状态 |
|---|---|---|---|
| SQL 注入 | [SQL注入.md](./SQL注入.md) | Low | ✅ 完成 |
| XSS（反射 / 存储 / DOM） | [XSS三种类型.md](./XSS三种类型.md) | Low | ✅ 完成 |
| 文件上传（含 Burp 绕过） | [文件上传绕过.md](./文件上传绕过.md) | Low / Medium | ✅ 完成 |
| CSRF（含 Token 重放） | [CSRF.md](./CSRF.md) | Low / Medium / High | ✅ 完成 |
| 命令执行（含反弹 shell） | [命令执行.md](./命令执行.md) | Low / Medium / High | ✅ 完成 |
| 文件包含（LFI → 读配置 → 拿数据库凭据） | [文件包含.md](./文件包含.md) | Low | ✅ 完成 |

## 测试环境

- DVWA（Damn Vulnerable Web Application），本地 Apache + MariaDB
- 难度：Low（基础复现）/ Medium（绕过练习）/ High（黑名单与 Token 绕过）
- 工具：浏览器开发者工具、Burp Suite（Repeater / Follow redirects）、curl、netcat、mysql 客户端

## 三个我认为最值得讲的复现

| 漏洞 | 关键点 | 一句话 |
|---|---|---|
| **CSRF Medium** | 源码用 `stripos($referer, $server_name)` 判断来源 | 只要 Referer **包含**服务器名就放行，攻击者注册 `192.168.59.128.evil.com` 即可绕过 |
| **命令执行 High** | 黑名单里写的是 `'\| '`（竖线**带空格**） | 攻击者用不带空格的 `127.0.0.1\|whoami` 直接绕过——黑名单永远补不完 |
| **文件包含 Low** | `php://filter/convert.base64-encode/resource=...` | include 会执行 PHP 文件，必须先用 filter 转 base64，才能看到 `db_password` 明文 |

## 相关文件

- [渗透测试报告_模板.docx](./渗透测试报告_模板.docx)——报告写作模板
- [screenshots/](./screenshots/)——截图存放目录（含索引说明）

## 说明

DVWA 本身就是故意做的不安全的靶场，所有测试均在本地进行，未对任何未授权目标发起测试。
