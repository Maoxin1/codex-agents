# Codex Agents

**不使用 Codex？** 可以直接使用[网页顾问室](https://mantou-agent-room.xmiao2343.chatgpt.site)，或[下载通用角色包](https://mantou-agent-room.xmiao2343.chatgpt.site/download)。网页使用访客自己的 OpenAI API Key；文本适配版不含联网与本地执行能力。自建与导出见[非 Codex 使用指南](docs/non-codex.md)。

两个日常入口：`_manuel` 帮你理解目标、检查判断并迈出下一步；`_mantou` 帮你把需求说清楚。

## 开始使用

```powershell
./install.ps1
```

默认安装两个入口以及 `_manuel` 使用的五本书方法资料，安装后重启 Codex。

> 请调用 _manuel：我想找到适合自己的副业。先根据我授权的资料核对真实目标，等我确认，再直接挑战我的假设，比较可尝试的方向，给出第一步。

> 请调用 _mantou：把这段需求改清楚，保持简短，不增加任务范围。

> 请调用 _manuel：调研［具体问题］，核验关键来源，说明前提和反证条件，并教我一个可迁移的分析方法。范围是［地区、时间或指定材料］。

调研与分析学习流程现可试用，仍使用 `_manuel` 入口；实际效果待使用检验，不承诺市场预测准确率。详见[调研流程](agents/_manuel/research.md)。

`_manuel` 也能只检查一段推理。资料不足时会提出必要问题；个人理解是可被纠正的判断，不是读心。五本书用于帮助分析，不要求用户选择作者或默认召集多个顾问。

## 个人记录和方法资料

知识库按用户指定路径、工作区 AGENTS.md 或 MANUEL_VAULT_PATH 解析。聊天历史需要用户提供导出文件或可用连接；没有自动导入、跨平台记忆或后台监控。私人入口可保存在安装目录的 `context.local.md`，不要提交个人笔记和聊天原文。

五本书分别提供批判性思维、研究设计、用户进展、改变过程和研究落地方法，按需读取并保留来源。未来新增书籍优先增加方法资料，不增加日常入口。详见 [_manuel 指南](agents/_manuel/README.md)及[方法路由](agents/_manuel/methods.md)。

## 可选角色与升级

```powershell
# 只安装一个入口及其资料
./install.ps1 -Agent _manuel
# 安装全部八个角色（含旧书籍顾问、事实核验、投资研究）
./install.ps1 -All
# 更新默认两个入口及依赖
./install.ps1 -Force
# 更新所有角色
./install.ps1 -All -Force
# 预览默认更新
./install.ps1 -Force -WhatIf
```

旧的 `_wayne`、`_clayton`、`_alan`、`_jim` 保留为按书点名的兼容入口；`_factbot` 和 `_invest` 为专项入口。安装器不会删除已经安装的旧角色，默认改为两个入口不等于自动卸载。需要隐藏旧入口时，先检查并备份相应 TOML，再由用户或获授权维护操作处理。

安装目录是 CODEX_HOME/agents，未配置时为用户主目录下的 .codex/agents。Force 会覆盖受管文件（包括模型配置），私有覆盖文件保留。相同依赖复用，不同依赖在无 Force 时提前报错。完整说明见[兼容性](COMPATIBILITY.md)和[使用手册](docs/quickstart.md)。

## 验证与维护

```powershell
./tests/validate_repository.ps1
```

离线检查覆盖安装、来源读取器、配置和用例资产，不证明个人理解或建议效果。新版统一伙伴与简化提示词行为尚待真实评估，旧版本结果不代表新版本。参见[验证状态](docs/verification-status.md)、[评估方案](docs/evaluation-plan.md)、[整合决定](docs/agent-consolidation-review.md)。模型评估需明确授权，不在默认 CI 中执行。

原书、完整提取文本和私人知识库不随仓库分发。精确引文或未覆盖内容需核验依法取得、版本匹配的原书。配置和原创支持材料采用 [MIT License](LICENSE)，第三方资料权利归原权利人。
