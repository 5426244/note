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
| 暴力破解（字典爆破 admin） | [screenshots/](./screenshots/) 28–29 | Low | ✅ 完成 |
| 渗透（Metasploitable2 两个后门） | [screenshots/](./screenshots/) 30–32 | Low（后门类） | ✅ 完成 |


## 三个我认为最重要的点

| 漏洞 | 关键点 | 说明|
|---|---|---|
| **CSRF Medium** | 源码用 `stripos($referer, $server_name)` 判断来源 | 只要 Referer **包含**服务器名就放行，攻击者注册 `192.168.59.128.evil.com` 即可绕过 |
| **命令执行 High** | 黑名单里写的是 `'\| '`（竖线**带空格**） | 攻击者用不带空格的 `127.0.0.1\|whoami` 直接绕过——黑名单永远补不完 |
| **文件包含 Low** | `php://filter/convert.base64-encode/resource=...` | include 会执行 PHP 文件，必须先用 filter 转 base64，才能看到 `db_password` 明文 |

## 相关文件

- [渗透测试报告_模板.docx](./渗透测试报告_模板.docx)——报告写作模板
- [screenshots/](./screenshots/)——截图存放目录

