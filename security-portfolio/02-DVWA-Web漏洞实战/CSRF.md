# CSRF · 跨站请求伪造

## 本质

攻击者**不需要拿到受害者的密码**，只要让受害者的浏览器「自愿」发出一个请求就行。

浏览器有两个天生的行为，正好被利用：

1. **发请求时自动带 Cookie** —— 只要目标域名匹配，浏览器一定会把 `PHPSESSID` 带上，不问你是不是本人点的。
2. **分不清"用户主动"和"被诱导"** —— 页面里一个 `<img src="...">`、一个自动提交的表单，浏览器都会照常发请求、照常带 Cookie。

> 一句话：攻击者借的是受害者的**身份**，不是受害者的**密码**。

## 成立条件（三个都要满足）

| 条件 | 说明 | 缺了会怎样 |
|---|---|---|
| 受害者已登录 | 浏览器里有有效 Cookie | 请求没有身份，改不了任何东西 |
| 参数可预测 | URL / 表单字段结构固定，没有随机值 | 攻击者构造不出可用的请求 |
| 关键操作只靠 Cookie 认证 | 服务端只看 Cookie 就执行 | 服务端会二次校验，攻击失效 |

**三条里任何一条不成立，CSRF 就打不成。** 所以防御也是从这三条里挑一条来断。

## DVWA 三档差异

### Low：零校验

改密码的接口是 GET：

```
/DVWA/vulnerabilities/csrf/?password_new=xxx&password_conf=xxx&Change=Change
```

只要受害者访问这个 URL，密码就被改了。攻击者的页面里放一行：

```html
<img src="http://192.168.59.128/DVWA/vulnerabilities/csrf/?password_new=csrf123&password_conf=csrf123&Change=Change" style="display:none">
```

受害者打开这个页面 → 图片加载 → 请求发出 → 密码变成 `csrf123`。
**页面上什么都看不见**，这就是 CSRF 最吓人的地方。

### Medium：检查 Referer

源码 `vulnerabilities/csrf/source/medium.php`：

```php
if( stripos( $_SERVER[ 'HTTP_REFERER' ], $_SERVER[ 'SERVER_NAME' ] ) !== false ) {
    // 允许改密码
}
```

`stripos` 是**"查找子串"**，不是"等于"。

所以只要 Referer 里**任意位置**出现服务器名就算通过：

| Referer | 结果 |
|---|---|
| `http://192.168.59.128/csrf.html` | 通过（正常来源） |
| `http://evil.com/` | 拦截 |
| `http://192.168.59.128.evil.com/` | **通过（绕过）** |

第三种就是绕过：`192.168.59.128.evil.com` 是攻击者自己注册的域名，**整串字符里确实"包含"服务器名**，但域名归属是攻击者。

### High：CSRF Token

源码 `vulnerabilities/csrf/source/high.php`：

```php
checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
```

页面表单里多了一个隐藏字段：

```html
<input type="hidden" name="user_token" value="d3b14462eebfef..." />
```

这个值有三个特点：

1. **随机** —— 每次刷新页面都不一样
2. **存在服务端 Session 里** —— 客户端只有一个副本
3. **一次性** —— 用过就作废

攻击者为什么拿不到：他的页面在 `evil.com`，**读不到** `192.168.59.128` 页面里的 HTML（同源策略）。拿不到这个随机值，就构造不出合法请求。

## 我的实测记录

测试环境：Kali 虚拟机，`192.168.59.128/DVWA/`，难度逐级切换。

### 1. Low：改 URL 直接改密码

浏览器直接访问改密码 URL，页面提示 `Password Changed.`，用新密码能登录。

### 2. Medium：三层对比（Burp 手动改 Referer）

| 测试 | Referer 值 | 返回 |
|---|---|---|
| 正常 | `http://192.168.59.128/csrf.html` | `Password Changed.` |
| 外部站点 | `http://evil.com/` | `That request didn't look correct.` |
| 子域名绕过 | `http://192.168.59.128.evil.com/` | `Password Changed.` ← **绕过成功** |

### 3. High：Token 被消耗后重放

- 请求里带 `user_token=d3b14462eebfef...`
- 第二次发送同一请求 → `HTTP/1.1 302 Found`，`Location: index.php`
- 跟随跳转后页面显示：**`CSRF token is incorrect`**

**结论：Token 用过即作废，重放必然失败。**

### 截图

| 文件 | 内容 |
|---|---|
| `screenshots/10-CSRF-Medium-Referer拦截.png` | Referer=evil.com，返回 "That request didn't look correct." |
| `screenshots/11-CSRF-Medium-绕过成功.png` | Referer=192.168.59.128.evil.com，返回 "Password Changed." |
| `screenshots/12-CSRF-High-Token参数.png` | 请求行里带 `user_token` |
| `screenshots/13-CSRF-High-重放失败.png` | 302 跳转 + "CSRF token is incorrect" |

## 为什么 Referer 不算防御

**Referer 是客户端提供的一个普通 HTTP 头。**

- 浏览器可以配置成不发 Referer
- Burp / curl 可以随意改写
- 攻击者可以注册含目标域名的子域名来构造

用 curl 就能伪造：

```bash
curl -H "Referer: http://192.168.59.128.evil.com/" \
  "http://192.168.59.128/DVWA/vulnerabilities/csrf/?password_new=x&password_conf=x&Change=Change"
```

**一个由客户端提供的值，不能用来证明客户端的身份。**

而且 Medium 的写法还有个结构性错误：判断用的是"包含"而不是"等于"。正确的写法至少应该是：

```php
$referer = parse_url( $_SERVER['HTTP_REFERER'], PHP_URL_HOST );
if( $referer === $_SERVER['SERVER_NAME'] ) { ... }
```

解析出 host 再**全等比较**——即使这样，也只能算辅助措施，不能当主防御。

## 正确防御

### 1. CSRF Token（根本）

- 服务端生成随机值，存 Session，同时输出到表单隐藏字段
- 提交时比对，**不等就拒绝**
- Token 绑定用户会话，一次一用

这是唯一能从根本上解决问题的方案，因为它依赖的是**攻击者拿不到的秘密**，而不是"看起来像不像自己人"。

### 2. SameSite Cookie（辅助）

```
Set-Cookie: PHPSESSID=xxx; SameSite=Lax
```

- `Lax`：跨站发起的 POST、`<img>`、`<iframe>` 请求**不带** Cookie
- `Strict`：更严，连从外部链接点进来都不带

DVWA 页面上就有这句提示：

> Browsers are starting to default to setting the SameSite cookie flag to Lax, and in doing so are killing off some types of CSRF attacks.

**注意**：这是"浏览器帮你挡"，不是"网站自己的防御"。面试时要说清这个区别——网站不能指望用户的浏览器版本。

### 3. 关键操作二次验证（兜底）

改密码要求输入**旧密码**，改邮箱要求**邮箱验证码**，转账要求**支付密码**。

即使 Token 被绕过，攻击者也不知道旧密码。

## 常见面试问题

**Q：CSRF 和 XSS 的区别？**

| | CSRF | XSS |
|---|---|---|
| 攻击目标 | 利用用户的**身份** | 利用用户对网站的**信任** |
| 攻击者能否读到响应 | 不能（同源策略挡着） | 能（脚本在目标域里跑） |
| 是否需要用户交互 | 需要（访问恶意页面） | 需要（点链接 / 页面被访问） |
| 防御 | Token + SameSite | 输出编码 + CSP |

**Q：为什么 CSRF 不需要知道用户密码？**

因为认证靠的是 Cookie，而浏览器会自动带 Cookie。攻击者不需要"登录"，他只需要"让受害者的浏览器发请求"。

**Q：GET 和 POST 在 CSRF 上的区别？**

低难度下没区别——`<img>` 只能发 GET，但攻击者可以用自动提交的表单发 POST：

```html
<form action="http://target/change" method="POST" id="f">
  <input name="password" value="hacked">
</form>
<script>document.getElementById('f').submit()</script>
```

**所以"改成 POST"不是防御**，只是提高了利用门槛。

**Q：Token 放在哪里？**

- 放在**表单隐藏字段**或**自定义请求头**（`X-CSRF-Token`）
- **不能放在 URL 参数里**——URL 会被记录到日志、Referer、浏览器历史里，容易泄露

**Q：Token 和 Session 的关系？**

Token 存在 Session 里，但**和 SessionID 是两个独立的值**。SessionID 证明"你是谁"，Token 证明"这个请求是从你的页面发出来的"。

## 一句话总结

> **Referer 是"我告诉你我从哪来"——可以撒谎。**
> **Token 是"我发给你的一串随机码"——你没拿到就是没有。**
