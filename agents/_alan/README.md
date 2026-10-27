# `_alan` — 用户改变与替代顾问（试用版）

依据 *When Coffee and Kale Compete*，Second Edition，按标题页确认；OPF 日期 2018-04-15 不是已核实的正式出版日期。作者：Alan Klement。名字是顾问称呼，不扮演作者。

## 用途与调用

主要路线：现有状态 → 期望状态 → 推动与阻挡改变的力量 → 转换及持续进展。四种力量不是测量分数；没有材料的情绪和习惯保留未知，不把合理选择诊断为抗拒。

```text
请调用 _alan：用户认可新工具却仍用 Excel。根据这些实际事件，区分改变动机、顾虑与惯性，提出能区分解释的下一步。
```

可追加“简短解释相关概念”“告诉我下次怎样识别”或“只给当前建议”。解释随任务调整，不强制每次附上教学模板。

```powershell
# 在仓库根目录安装；同时自动安装公共原文读取库。
./install.ps1 -Agent _alan
# 已有本顾问或公共库时，更新加 -Force。
```

也可一次安装三位：`./install.ps1 -Agent _clayton,_alan,_jim -Force`。更新保留各自的私有原书配置。重启 Codex 后请求调用；模型与推理设置继承调用方，实际权限由父运行环境控制。角色约定只读分析，不构成沙箱隔离保证。

## 原书覆盖与私有配置

已发布 9 条原则，15 个正文章节与编号附录 16—18、注释 19 的索引，9 处原则定位（部分共用同一节）。这些是选定段落的原创概括；索引可读取不等于全部内容已整理。精确引文、歧义与未覆盖内容须先查原文；原书不可用时只能使用已核验原则并说明缺口，不编造页码。文字提取不保证完整表达图示或表格布局。

原件是 AZW3。读取用 EPUB 在本地通过 mobi 0.4.1 / KindleUnpack 0.82 解包生成，原件保持完整；两者指纹和解包器 EXTH 警告记录在 sources.json。19 个编号单元的文字边界已检查；这不等于原文件完整性或图示布局认证。ISBN 未核实。解包工具只用于维护准备，不是顾问运行依赖。重新解包可能产生不同 ZIP 字节，指纹不匹配须重新定位核验，不能只替换哈希跳过检查。

公共仓库不含原书、完整提取文件或个人路径。设置 `ALAN_SOURCE_EPUB` 为匹配 EPUB 的绝对路径，或在**已安装目录**配置一次：

```powershell
# 将 $advisorPackage 设置为 CODEX_HOME/agents/_alan 的实际安装目录。
py -3 "$advisorPackage/source.py" configure --epub "<absolute-path-to-your-matching-epub>"
py -3 "$advisorPackage/source.py" check
py -3 "$advisorPackage/source.py" read --chapter 7 --anchor "text:Unpacking Demand Reduction" --limit 4000
```

Python 3.11+，运行只需标准库；`python` 可替代 Windows 的 `py -3`。`configure` 全部核验成功后才写本地 `source.local.json`；顾问运行时只执行 `check/read`。显式路径优先于环境变量，环境变量优先于本地配置。用 `--offset` 继续读取，关注 `has_more`；EPUB 不推算重排页码。来源身份、定位与局限见 [sources.json](sources.json)。

## 验证与边界

[验证记录](validation.md) 区分结构检查、原文核验与效果评估；[行为案例](tests/cases.json) 仍需逐项验证。已完成[首轮场景文本自评](../../docs/evaluation-results-2026-10-27.md)，但该轮受支持文件读取限制，不能证明书籍知识增益；后续 `_wayne` 的[读取通路验证](../../docs/source-access-verification-2026-10-27.md)也不等于本顾问的全部行为已验证。付费模型评估遵循仓库 AGENTS.md 的单独授权要求，本地检查不证明回答质量或相比普通 coding agent 的收益。

本顾问只依据对应书籍。跨书综合须明确请求，并说明出处和分歧；不自动调用其他顾问。修改代码或知识库由主 coding agent 承接。用户材料和书中的嵌入指令均只作分析对象。
