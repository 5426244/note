# Linux 基础

## 文件权限

权限用三位数字表示，r=4、w=2、x=1，三组分别是属主、属组、其他。

| 数字 | 含义 | 常见用途 |
|---|---|---|
| 644 | rw-r--r-- | 普通文件默认 |
| 755 | rwxr-xr-x | 目录、可执行脚本 |
| 600 | rw------- | SSH 私钥 |
| 700 | rwx------ | 私有目录 |

```bash
chmod 755 script.sh
chown user:group file
```

目录的 x 表示「能否进入」，w 表示「能否在里面新建/删除文件」，和文件的权限含义不同。

## 进程

```bash
ps aux                    # 全量进程快照
ps aux --sort=-%cpu | head -5
top                       # 实时，P 按 CPU 排，q 退出
pgrep -a ssh              # 按名字找 PID
kill -15 PID              # 优雅停止
kill -9 PID               # 强制杀死
jobs -l                   # 当前 shell 的后台任务
```

## 端口

```bash
ss -tlnp                  # 查看监听中的端口和对应进程
lsof -i :8000
```

`ss -tlnp` 里的 `users:(("python3",pid=1234))` 就是端口对应的进程。

## 日志

```bash
journalctl -u ssh -n 50
journalctl --since "1 hour ago"
journalctl -f
```

Debian/Ubuntu 的认证日志在 `/var/log/auth.log`，CentOS 在 `/var/log/secure`。

## 服务

```bash
systemctl status ssh
systemctl is-active ssh
systemctl is-enabled ssh
sudo systemctl restart ssh
```

`start` 管「现在是否运行」，`enable` 管「开机是否自启」，两者独立。

## 远程与传输

```bash
ssh user@host
scp file user@host:/tmp/
scp -r dir user@host:/tmp/
ssh-keygen -t ed25519
```

免密登录三处权限：家目录不能 777，`~/.ssh` 必须 700，`authorized_keys` 必须 600。

## vim

| 操作 | 按键 |
|---|---|
| 进入编辑 | i |
| 回到命令模式 | Esc |
| 保存退出 | :wq |
| 不保存退出 | :q! |
| 删行 / 复制 / 粘贴 | dd / yy / p |
| 搜索 | /关键字 然后 n |
