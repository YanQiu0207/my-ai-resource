# RTK 在 Codex 中的安装、使用与卸载

## 结论

RTK（Rust Token Killer）通过过滤和压缩 Shell 命令输出，减少写入 Codex 上下文的 Token。它适合处理 Git、文件搜索、测试、构建和 Lint 等高输出命令，但不能减少 System Prompt、Tool Schema、Skill、Agent 或历史对话占用。

Codex 当前通过 `AGENTS.md` 指令引导模型使用 RTK，不是透明 Hook，因此无法保证每条命令都自动经过 RTK。

项目地址：[rtk-ai/rtk](https://github.com/rtk-ai/rtk)

## 一、安装 RTK

以下步骤适用于 Windows PowerShell。

### 1. 下载 Windows 版本

打开 [RTK Releases](https://github.com/rtk-ai/rtk/releases)，下载：

```text
rtk-x86_64-pc-windows-msvc.zip
```

解压后得到 `rtk.exe`。

### 2. 放入固定目录

```powershell
New-Item -ItemType Directory -Force "$HOME\.local\bin"
Copy-Item ".\rtk.exe" "$HOME\.local\bin\rtk.exe"
```

### 3. 加入用户 PATH

```powershell
$rtkBin = "$HOME\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

if (($userPath -split ";") -notcontains $rtkBin) {
    [Environment]::SetEnvironmentVariable(
        "Path",
        "$userPath;$rtkBin",
        "User"
    )
}
```

关闭并重新打开 PowerShell，然后验证：

```powershell
rtk --version
rtk gain
```

如果 `rtk gain` 不存在，可能安装了 crates.io 上同名的 Rust Type Kit。应改用 RTK Releases 提供的二进制文件。

### 4. 可选：安装 ripgrep

部分过滤器依赖 `rg`：

```powershell
winget install BurntSushi.ripgrep.MSVC
rg --version
```

## 二、接入 Codex

### 全局接入

先备份现有全局规则：

```powershell
Copy-Item "$HOME\.codex\AGENTS.md" "$HOME\.codex\AGENTS.md.bak" -ErrorAction SilentlyContinue
```

初始化 Codex 集成：

```powershell
rtk init -g --codex
rtk init --show
```

该命令会向 `~/.codex/AGENTS.md` 写入 RTK 使用说明。完成后重启 Codex。

### 仅在当前项目接入

进入目标项目目录后执行：

```powershell
rtk init --codex
```

该命令会修改当前项目的 `AGENTS.md`。不建议同时进行全局和项目级接入，以免重复注入规则。

## 三、日常使用

### Git

```powershell
rtk git status
rtk git log -n 10
rtk git diff
rtk git push
```

### 文件与搜索

```powershell
rtk ls .
rtk find "*.py" .
rtk grep "TODO" .
rtk read ".\src\main.py"
```

激进压缩代码，只保留签名等概要：

```powershell
rtk read ".\src\main.py" -l aggressive
```

该模式会丢失实现细节，不适合定位具体 Bug。

### 测试与构建

```powershell
rtk pytest
rtk npm test
rtk cargo test
rtk go test ./...
```

具体支持范围以当前版本帮助为准：

```powershell
rtk --help
rtk discover
```

## 四、查看节省效果

```powershell
rtk gain
rtk gain --graph
rtk gain --history
rtk gain --daily
rtk discover
rtk session
```

这些数据是 RTK 的估算值，不等于 OpenAI 账单中的精确 Token 数。

## 五、需要原始输出时

RTK 可能裁掉诊断细节。排查复杂问题时，可以直接执行原始命令：

```powershell
git diff
pytest -vv
```

建议保留失败命令的完整输出：

```toml
[tee]
enabled = true
mode = "failures"
```

配置文件位置以以下命令的实际输出为准：

```powershell
rtk --help
rtk init --show
```

## 六、卸载

### 1. 移除 Codex 集成

全局接入：

```powershell
rtk init -g --codex --uninstall
```

项目级接入需要在对应项目目录执行：

```powershell
rtk init --codex --uninstall
```

执行后检查 `~/.codex/AGENTS.md` 或项目的 `AGENTS.md`，确认 RTK 管理的规则块已移除，且原有规则未被删除。

### 2. 删除可执行文件

```powershell
Remove-Item "$HOME\.local\bin\rtk.exe"
```

### 3. 从用户 PATH 删除目录

只有 `~/.local/bin` 不再存放其他程序时才执行：

```powershell
$rtkBin = "$HOME\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

$newPath = (($userPath -split ";") |
    Where-Object { $_ -and $_ -ne $rtkBin }) -join ";"

[Environment]::SetEnvironmentVariable("Path", $newPath, "User")
```

重新打开 PowerShell，验证：

```powershell
Get-Command rtk -ErrorAction SilentlyContinue
```

没有输出表示 RTK 已不在 PATH 中。

## 参考来源

- [RTK 官方仓库](https://github.com/rtk-ai/rtk)
- [RTK 支持的 Agent](https://github.com/rtk-ai/rtk/blob/master/docs/guide/getting-started/supported-agents.md)
- [Codex 原生 RTK 集成建议](https://github.com/openai/codex/issues/19001)
