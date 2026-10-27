# 兼容性说明

本项目提供 Codex 自定义 agent 配置与支持文件。本地检查可以验证结构、语法和部分约定；模型访问权限、产品功能和实际工具权限由你的 Codex 环境决定。

## 运行要求

- Codex 需要支持自定义 agent，以及所用的模型、推理强度和权限配置字段。
- `_factbot`、`_manuel` 的仓库默认模型为 `gpt-5.6-terra`；`_invest`、`_mantou` 为 `gpt-5.6-sol`。安装配置不会自动授予这些模型的访问权限。
- `_wayne`、`_clayton`、`_alan`、`_jim` 不固定模型或推理强度，继承调用方设置。其原书读取工具需要 Python 3.11 或更新版本，只使用标准库。
- 安装和验证脚本需要 PowerShell。仓库检查接受 `python` 命令或 Windows 的 `py` 启动器。
- `_mantou` 的剪贴板复制功能需要 Windows 交互会话，以及可用的 `Set-Clipboard`、`Get-Clipboard`。剪贴板不可用时，仍返回完整提示词供手动复制。
- `_invest` 可在明确授权后维护 Obsidian；知识库路径和私人案例索引保存在公共仓库之外。

三位 JTBD 顾问依赖相邻的 `_book_sources` 目录，安装任意一位时会自动安装该公共读取库。各自的 `source.local.json` 会在更新时保留。`_alan` 读取本地已经解包的 EPUB，不直接读取 AZW3；解包属于维护配置步骤，不由运行中的顾问自动执行。

只读角色约定不等于系统已经完成权限隔离。父会话和本机权限策略仍然决定工具能读写什么、能否联网；遇到读取失败，应检查路径和环境，不应让顾问凭记忆补写原书观点。

## 模型不可用时怎样处理

先确认当前账号可以使用哪些模型。需要更换时，在相关 `agents/<name>.toml` 中只修改 `model`，保留该 agent 的工具、推理强度和行为边界，并显式检查本地覆盖：

```powershell
./tests/validate_repository.ps1 -AllowModelOverride
```

也可只检查对应 agent，例如：

```powershell
python agents/_factbot/tests/validate_factbot.py --allow-model-override
```

该选项只放宽“模型名称必须与仓库默认值完全一致”的检查；模型标识仍须是非空且不含空白的字符串。其他约束照常检查。它不验证账号权限、工具支持或回答质量。

检查通过后，安装本地版本、重启 Codex，再用不敏感的小问题确认实际调用。独立调用脚本若有 `-Model` 参数，也需要单独传入所选模型。

本地模型覆盖不要直接作为公共默认值提交。默认 CI 和发布前检查仍要求仓库模型默认值保持一致。带 `-Force` 的更新会替换受管 TOML，因此升级前应备份、之后按需重新应用本地模型偏好。

## 更新前后检查什么

1. 运行 `./install.ps1 -Force -WhatIf` 预览目标。
2. 阅读[更新记录](CHANGELOG.md)，备份自己修改过的受管文件。
3. 运行 `./tests/validate_repository.ps1`；仅在有意使用本地模型覆盖时加 `-AllowModelOverride`。
4. 安装更新并重启 Codex。
5. 用不敏感的问题确认所需 agent 的实际调用，再用于正式任务。

默认 CI 使用 Windows，覆盖 Python 3.11 和 3.13，不调用付费模型服务，也不执行真实行为评估。

需要批量评估时另行明确调用范围。独立 CLI 评估器在 Windows 上保留已有沙箱后端，并先做不消耗模型额度的只读预检；没有有效配置或读取失败时停止。修复与验证经过见[支持文件读取验证](docs/source-access-verification-2026-10-27.md)。
