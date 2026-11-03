# DVWA Web 漏洞实战（个人练习）

在 DVWA 靶场上手工复现三类典型 Web 漏洞，并理解对应的防御原理。

| 漏洞 | 文件 | 状态 |
|---|---|---|
| SQL 注入 | [SQL注入.md](./SQL注入.md) | ✅ 完成 |
| XSS（反射 / 存储 / DOM） | [XSS三种类型.md](./XSS三种类型.md) | ✅ 完成 |
| 文件上传（含 Burp 绕过） | [文件上传绕过.md](./文件上传绕过.md) | ✅ 完成 |

## 测试环境

- DVWA（Damn Vulnerable Web Application），本地 Apache + MariaDB
- 难度：Low（基础复现）/ Medium（绕过练习）
- 工具：浏览器开发者工具、Burp Suite、Python 简易 HTTP 服务器

## 相关文件

- [渗透测试报告_模板.docx](./渗透测试报告_模板.docx)——报告写作模板
- [screenshots/](./screenshots/)——截图存放目录

## 说明

DVWA 本身就是故意做的不安全的靶场，所有测试均在本地进行。
