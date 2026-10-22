# Antigravity Proxy Launcher（macOS）

让 Google Antigravity 启动时自动继承系统 HTTP/HTTPS 代理，用于后台 `language_server` 未使用系统代理、必须开启 TUN 的情况。这是独立启动工具，不是 IDE 扩展，也不修改原应用。

## 工作方式

每次启动读取 `scutil --proxy` 的 HTTPS 代理地址和端口，设置 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY` 及对应小写变量，再启动原应用。`localhost`、`127.0.0.1`、`::1` 保持直连。系统 HTTPS 代理未启用时会提示并停止。

代理客户端仍须运行并启用系统代理。此工具不提供代理节点、不改变账号地区，也不保证所有版本及网络环境均兼容。不支持只有 PAC、只有 SOCKS 或需要代理认证的配置。

## 安装

要求 macOS、Python 3、已安装的 Antigravity，以及已固定到 Dock 的原应用入口。关闭 Antigravity 后，解压并双击 `Install.command`。也可在终端运行：

```sh
python3 tool.py install --dock
```

默认生成 `~/Applications/Antigravity Proxy.app`，并把已有 Dock 入口替换成 `Antigravity Proxy`。图标从本机原应用复制，仓库和发行包不包含 Google 图标或应用二进制。

如果系统阻止运行，请先检查脚本源码，再通过 macOS 的打开/安全设置允许本工具运行；不要全局关闭 Gatekeeper。

原应用安装位置不同，可以指定：

```sh
python3 tool.py install --dock --app '/Applications/Antigravity IDE.app'
```

只创建启动器，不修改 Dock：

```sh
python3 tool.py build --output './Antigravity Proxy.app'
```

目标文件夹已存在时停止，不覆盖。启动器和原应用可能分别显示运行图标。只从新入口启动才会注入代理；原应用已在运行时，请先完全退出，再从新入口启动。原应用更新通常不会覆盖此启动器，但移动应用或更换代理实现后需重新验证。

## 验证

1. 关闭 TUN/虚拟网卡，保留代理客户端和系统代理。
2. 完全退出 Antigravity，从新入口打开。
3. 发送一条模型消息，确认收到回复。
4. 退出、重开，再次验证。

可用 `lsof -nP -a -p <language_server_PID> -iTCP` 检查后台是否连接本地代理端口。仅启动成功不代表模型请求成功。

本工具来源于一次 macOS Antigravity 2.23.1 实测：后台已观察到连接本地 HTTP 代理，使用者确认关闭 TUN 后可以使用。其他版本仍需验证。发行包验证覆盖 Python/Zsh 语法、构建结果与包内容；通用安装脚本不在发布时再次修改开发者当前 Dock。

## 回滚 Dock

```sh
python3 tool.py restore-dock
```

只恢复本工具替换的 Dock 项，保留其他当前 Dock 项和启动器文件。备份位于 `~/Library/Application Support/Antigravity Proxy Launcher/`。回滚不删除文件。安装脚本不会结束你的应用进程。

注：此前会话中生成的首版启动器由单独安装流程创建，其备份不属于本仓库安装脚本；本仓库的 `restore-dock` 仅适用于这里的 `install --dock`。

## 目录

- `src/launcher.zsh`：可审查的启动逻辑。
- `tool.py`：本机构建、安装、Dock 备份与恢复。
- `Install.command`：双击安装入口。

此项目为非官方工具，与 Google 无隶属关系。

## 开源许可

本仓库原创脚本与文档使用 [MIT License](LICENSE)。Google Antigravity 的名称、商标、图标和原应用不在此许可范围内。构建时从使用者本机复制的图标仅用于本机启动入口，不随发行包分发。
