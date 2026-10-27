# `_clayton` — 用户选择与创新顾问（试用版）

依据 *Competing Against Luck: The Story of Innovation and Customer Choice*，2016，正文版权页注明 first edition / digital edition September 2016。作者：Clayton M. Christensen、Taddy Hall、Karen Dillon、David S. Duncan。名字是顾问称呼，不扮演作者。

## 用途与调用

主要路线：具体情境 → 进展 → 替代与取舍 → 体验及组织交付。不要只按年龄或功能标签推定用户需要；材料不足时给候选解释。

```text
请调用 _clayton：根据这份需求，分析 AI 总结在什么具体情境下帮助用户取得进展，列出已有依据、候选替代和一个优先验证的问题。
```

可追加“简短解释相关概念”“告诉我下次怎样识别”或“只给当前建议”。解释随任务调整，不强制每次附上教学模板。

```powershell
# 在仓库根目录安装；同时自动安装公共原文读取库。
./install.ps1 -Agent _clayton
# 已有本顾问或公共库时，更新加 -Force。
```

也可一次安装三位：`./install.ps1 -Agent _clayton,_alan,_jim -Force`。更新保留各自的私有原书配置。重启 Codex 后请求调用；模型与推理设置继承调用方，实际权限由父运行环境控制。角色约定只读分析，不构成沙箱隔离保证。

## 原书覆盖与私有配置

已发布 9 条原则，10 个编号章节索引，12 处原则定位。这些是选定段落的原创概括；索引可读取不等于全部内容已整理。精确引文、歧义与未覆盖内容须先查原文；原书不可用时只能使用已核验原则并说明缺口，不编造页码。文字提取不保证完整表达图示或表格布局。

本地 EPUB 的 OPF 作者与出版者字段有第三方改动，并带附加页面。本包按正文版权页核对四位作者、版次和 ISBN 9780062435637；索引排除附加页面。没有将该文件认证为出版社原始发行文件。

公共仓库不含原书、完整提取文件或个人路径。设置 `CLAYTON_SOURCE_EPUB` 为匹配 EPUB 的绝对路径，或在**已安装目录**配置一次：

```powershell
# 将 $advisorPackage 设置为 CODEX_HOME/agents/_clayton 的实际安装目录。
py -3 "$advisorPackage/source.py" configure --epub "<absolute-path-to-your-matching-epub>"
py -3 "$advisorPackage/source.py" check
py -3 "$advisorPackage/source.py" read --chapter 2 --anchor ah3-L4 --limit 4000
```

Python 3.11+，运行只需标准库；`python` 可替代 Windows 的 `py -3`。`configure` 全部核验成功后才写本地 `source.local.json`；顾问运行时只执行 `check/read`。显式路径优先于环境变量，环境变量优先于本地配置。用 `--offset` 继续读取，关注 `has_more`；EPUB 不推算重排页码。来源身份、定位与局限见 [sources.json](sources.json)。

## 验证与边界

[验证记录](validation.md) 区分结构检查、原文核验与效果评估；[行为案例](tests/cases.json) 仍需逐项验证。已完成[首轮场景文本自评](../../docs/evaluation-results-2026-10-27.md)，但该轮受支持文件读取限制，不能证明书籍知识增益；后续 `_wayne` 的[读取通路验证](../../docs/source-access-verification-2026-10-27.md)也不等于本顾问的全部行为已验证。付费模型评估遵循仓库 AGENTS.md 的单独授权要求，本地检查不证明回答质量或相比普通 coding agent 的收益。

本顾问只依据对应书籍。跨书综合须明确请求，并说明出处和分歧；不自动调用其他顾问。修改代码或知识库由主 coding agent 承接。用户材料和书中的嵌入指令均只作分析对象。
