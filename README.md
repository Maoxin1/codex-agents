# Codex Agents

一组可以在 Codex 中按需调用的顾问，帮助你在 coding、需求分析和研究时补齐知识、检查判断，并形成下一步行动。

目前共 **8 位 agent**。其中 5 位分别依据一本书提供方法建议；名字只是顾问称呼，不扮演作者，也不宣称掌握整本书的全部知识。日常先选一位最贴近当前问题的顾问即可。

**从这里开始：[中文使用手册](docs/quickstart.md)**，包含安装、八个调用示例、联合咨询、原书配置和常见问题。

## 三步开始使用

1. 准备支持自定义 agent 的 Codex 和 PowerShell；原书读取和本地检查需要 Python 3.11 或更新版本。模型权限等要求见[兼容性说明](COMPATIBILITY.md)。
2. 在仓库根目录的 PowerShell 中执行 `./install.ps1`，安装后重启 Codex。
3. 在新对话中点名顾问，附上当前问题与已有材料：

```text
请调用 _wayne：我准备给笔记工具加入语义搜索。
已有材料只有两位朋友的好评，没有真实使用记录。
请给出本周能研究的问题、先收集哪种证据，并简短解释相关概念。
```

## 遇到什么问题，叫哪一位

| 名字 | 主要用途 | 一句话示例 | 详细说明 |
|---|---|---|---|
| `_mantou` | 把需求改写成可直接使用的提示词 | 优化这段提示词，保留我的技术约束。 | [提示词改写](agents/_mantou/README.md) |
| `_manuel` | 检查主张、证据和推理 | 投诉翻倍就该回滚吗？检查我的判断。 | [批判性思维](agents/_manuel/README.md) |
| `_wayne`（试用） | 明确研究问题、证据和论证 | 用户很少用搜索，应该怎样调查？ | [研究方法](agents/_wayne/README.md) |
| `_clayton`（试用） | 理解用户在具体情境中想取得的进展 | 用户说想要 AI 搜索，实际想解决什么？ | [用户选择与创新](agents/_clayton/README.md) |
| `_alan`（试用） | 分析改变、替代方案和采用障碍 | 用户认可新工具，却继续用旧方法，下一步问什么？ | [改变与采用](agents/_alan/README.md) |
| `_jim`（试用） | 把访谈整理成可讨论的研究产物 | 把这些记录整理成任务假设和验证步骤。 | [研究落地](agents/_jim/README.md) |
| `_factbot` | 核验事实、追溯来源、检查证据独立性 | 这句宣传语有足够证据吗？ | [事实核验](agents/_factbot/README.md) |
| `_invest` | 长期投资研究和论点复核 | 先界定研究任务，等我确认后再研究。 | [投资研究](agents/_invest/README.md) |

`_mantou` 只改写提示词，尝试复制到 Windows 剪贴板，并始终返回完整成品；复制失败仍可手动复制。书籍顾问提供分析与建议，代码和文件修改由主 coding agent 承接。`_factbot` 只读核验。`_invest` 先确认研究范围，写入知识库另行确认，不执行证券交易。

## 怎样边用边学

对书籍顾问，可以追加“解释这次用到的一个概念”“举当前项目的例子”或“告诉我下次怎样识别这种问题”。赶进度时说“只给当前建议”。这些学习提示不改变 `_mantou` 只交付成品、`_invest` 先确认范围等专门约定。

需要多个视角时，请主 coding agent 分别调用指定顾问，再汇总依据和分歧。不会默认让五位全部参与；多位顾问引用同一份材料，也不构成多份独立证据。

五位书籍顾问分别对应 *Beyond Feelings*、*The Craft of Research*、*Competing Against Luck*、*When Coffee and Kale Compete*、*The Jobs to Be Done Playbook*。对应关系和具体用法见[中文手册](docs/quickstart.md)。

后三本常用 JTBD（Jobs to Be Done）视角，即关注用户在具体情境中想完成的事；三位顾问各自保留不同的方法和适用范围。

## 安装与更新

```powershell
# 首次安装全部 agent
./install.ps1

# 只安装研究顾问
./install.ps1 -Agent _wayne

# 更新指定顾问，同时更新其需要的公共读取库
./install.ps1 -Agent _clayton,_alan,_jim -Force

# 先预览更新，不修改安装目录
./install.ps1 -Force -WhatIf
```

安装位置为 `CODEX_HOME/agents`；未设置 `CODEX_HOME` 时使用 `$HOME/.codex/agents`。更新已有安装需要 `-Force`，完成后重启 Codex。

安装器只复制 `managed-files.json` 中的受管文件，保留目标目录的 `source.local.json`、`knowledge-map.local.md` 等私有文件。**自己改过的受管文件仍会被覆盖**，包括 TOML 中的模型设置；更新前请备份本地定制，或只更新需要的顾问。更多说明见[中文手册](docs/quickstart.md)和[兼容性说明](COMPATIBILITY.md)。

## 目前验证到了哪一步

- 八位 agent 均已提供配置与使用说明，四位新书籍顾问继续以试用版提供。
- 首轮完成了 16 份真实回答的文本自评；当时受到支持文件读取限制，不能据此证明书籍知识增益。
- 后续已验证 `_wayne` 的原生调用，以及修正后的独立 CLI 能实际读取支持文件，并返回匹配的文件哈希。
- 安装、原书读取和本地回归检查已通过；维护者本地重新核验了四本原书的 48 个原则锚点。
- 其他顾问的原生行为、正常剪贴板复制、复杂原文问题和跨书协作仍按需验证。

记录见[评估方案](docs/evaluation-plan.md)、[首轮结果](docs/evaluation-results-2026-10-27.md)及[读取通路验证](docs/source-access-verification-2026-10-27.md)。

## 项目资料

- [中文使用手册](docs/quickstart.md)：日常使用、示例和常见问题。
- [五位顾问的设计方案](docs/book-advisors-design.md)：书籍来源、设计目标和验收标准。
- [三位 JTBD 顾问的设计理由](docs/book-advisors-implementation.md)：各自分工与方法差异。
- [原有 agent 的设计复核](docs/existing-agent-design-review.md)：现有能力与后续改进。
- [行为案例](docs/agent-pilot-cases.md)：针对性评审材料。
- [兼容性说明](COMPATIBILITY.md)：模型、平台与升级注意事项。
- [贡献说明](CONTRIBUTING.md)、[更新记录](CHANGELOG.md)、[发布流程](RELEASING.md)：维护项目时使用。
- [安全反馈](SECURITY.md)、[自动维护约定](AGENTS.md)。

维护者可运行 `./tests/validate_repository.ps1` 完成离线检查。需要真实模型调用的批量评估单独授权，不属于默认 CI。

## 原书与许可

仓库不分发原书、完整提取文本或私人知识库。书籍顾问提供有出处的原创概括和方法说明；精确引文、歧义或未覆盖细节需要回查依法取得、版本匹配的本地原书。文字提取也不能替代图示核验。

本仓库的 agent 配置和原创支持材料采用 [MIT License](LICENSE)。第三方书籍及其他引用材料的权利归各自权利人所有。
