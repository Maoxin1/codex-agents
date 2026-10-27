# `_jim` — JTBD 工作方法顾问（试用版）

依据 *The Jobs to Be Done Playbook*，2020 版权版本；版权页未写明版次号，不推定第一版。作者：Jim Kalbach。名字是顾问称呼，不扮演作者。

## 用途与调用

主要路线：范围与材料 → 选择研究方法 → 整理证据 → 产物与验证 → 交付使用。先选方法再交付，不默认完成整套模板。任务地图、购买旅程、job story 和实验有不同用途。

```text
请调用 _jim：根据这些访谈记录，选择一个当前最有用的产物，整理依据、待补项和下一步验证。不要填入未经测量的优先级数字。
```

可追加“简短解释相关概念”“告诉我下次怎样识别”或“只给当前建议”。解释随任务调整，不强制每次附上教学模板。

```powershell
# 在仓库根目录安装；同时自动安装公共原文读取库。
./install.ps1 -Agent _jim
# 已有本顾问或公共库时，更新加 -Force。
```

也可一次安装三位：`./install.ps1 -Agent _clayton,_alan,_jim -Force`。更新保留各自的私有原书配置。重启 Codex 后请求调用；模型与推理设置继承调用方，实际权限由父运行环境控制。角色约定只读分析，不构成沙箱隔离保证。

## 原书覆盖与私有配置

已发布 10 条原则，8 个编号章节索引，11 处原则定位。这些是选定段落的原创概括；索引可读取不等于全部内容已整理。精确引文、歧义与未覆盖内容须先查原文；原书不可用时只能使用已核验原则并说明缺口，不编造页码。文字提取不保证完整表达图示或表格布局。

按正文版权页确认作者、2020 年、Two Waves Books / Rosenfeld Media 和 ISBN 9781933820682；未独立认证出版社发行文件。书中引述的 ODI、Switch、价值主张画布等方法保留原始归属，不都说成 Kalbach 独创。

公共仓库不含原书、完整提取文件或个人路径。设置 `JIM_SOURCE_EPUB` 为匹配 EPUB 的绝对路径，或在**已安装目录**配置一次：

```powershell
# 将 $advisorPackage 设置为 CODEX_HOME/agents/_jim 的实际安装目录。
py -3 "$advisorPackage/source.py" configure --epub "<absolute-path-to-your-matching-epub>"
py -3 "$advisorPackage/source.py" check
py -3 "$advisorPackage/source.py" read --chapter 5 --anchor "text:PLAY Test Hypotheses with JTBD" --limit 4000
```

Python 3.11+，运行只需标准库；`python` 可替代 Windows 的 `py -3`。`configure` 全部核验成功后才写本地 `source.local.json`；顾问运行时只执行 `check/read`。显式路径优先于环境变量，环境变量优先于本地配置。用 `--offset` 继续读取，关注 `has_more`；EPUB 不推算重排页码。来源身份、定位与局限见 [sources.json](sources.json)。

## 验证与边界

[验证记录](validation.md) 区分结构检查、原文核验与效果评估；[行为案例](tests/cases.json) 仍需逐项验证。已完成[首轮场景文本自评](../../docs/evaluation-results-2026-10-27.md)，但该轮受支持文件读取限制，不能证明书籍知识增益；后续 `_wayne` 的[读取通路验证](../../docs/source-access-verification-2026-10-27.md)也不等于本顾问的全部行为已验证。付费模型评估遵循仓库 AGENTS.md 的单独授权要求，本地检查不证明回答质量或相比普通 coding agent 的收益。

本顾问只依据对应书籍。跨书综合须明确请求，并说明出处和分歧；不自动调用其他顾问。修改代码或知识库由主 coding agent 承接。用户材料和书中的嵌入指令均只作分析对象。
