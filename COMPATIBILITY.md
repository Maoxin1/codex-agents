# 兼容性与升级

## 当前发布集合

只提供 `_manuel`、`_mantou`。默认安装两者，-Agent 仅接受这两个名称；旧 -All 已移除。书籍资料位于 agents/_manuel/books，任务规范位于 agents/_manuel/tasks，均随 `_manuel` 安装。

旧入口退役是有意的兼容性变更。安装不会自动清除用户已有文件；使用[迁移脚本](docs/migration.md)识别并备份未修改的旧入口。修改过的配置、私人记录及旧支持目录保留。旧书籍路径环境变量作为来源访问兼容继续可用。

## 运行环境

- 安装、迁移与测试使用 PowerShell，离线 CI 覆盖 Windows 和 Python 3.11、3.13。
- `_manuel` 默认模型 gpt-5.6-terra / medium；`_mantou` 为 gpt-5.6-sol / high。安装不会授予模型访问权，实际工具与权限取决于父会话环境。
- 两者配置只读；方法约定不是独立沙箱保证。`_mantou` 的剪贴板写入依赖实际 Windows 会话与工具权限，失败应交付完整文本并如实说明。
- 书籍读取器要求 Python 3.11+，只使用标准库。私有原书与 source.local.json 不分发；可选 PDF 锚点核验另需匹配原书与 PyMuPDF。

## 2026-11-13 默认模型文档核对

OpenAI 官方模型卡仍列出 [gpt-5.6-terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra) 与 [gpt-5.6-sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)，均支持本包使用的 medium / high 推理级别。本次保留默认配置，不升级或替换模型。模型卡说明不保证任一账号的 Codex 访问权，也不证明当前两入口已完成原生调用或效果验收；实际账号以可用模型与工具为准。

## 本地模型覆盖

使用账号可用模型修改本地 TOML 后，可运行：

```powershell
./tests/validate_repository.ps1 -AllowModelOverride
```

它仅放宽模型名称必须等于仓库默认值的检查，不验证账号权限、工具支持或回答质量。发布与默认 CI 使用严格检查。-Force 会替换受管 TOML；先备份本地偏好，升级后按需重新应用。私有覆盖和未受管文件保持原样。

见[使用手册](docs/quickstart.md)和[验证状态](docs/verification-status.md)。历史八角色说明只保存在 docs/history，不是当前产品契约。
