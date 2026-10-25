# `_wayne` — 研究方法顾问（试用版）

在 coding 和需求分析时，帮助把宽泛疑问变成可回答的问题，判断需要什么证据，并检查研究论证。名字是顾问称呼，不代表作者本人。

依据 *The Craft of Research*, Fifth Edition (2024)：Wayne C. Booth、Gregory G. Colomb、Joseph M. Williams、Joseph Bizup、William T. FitzGerald。ISBN 9780226826660。

## 安装和使用

在仓库根目录运行：

```powershell
./install.ps1 -Agent _wayne
```

更新已安装版本可加 `-Force`。重启 Codex 后，明确请求：

```text
请调用 _wayne：用户很少用搜索功能。帮我明确研究问题、关键证据和最小调查步骤。
已有材料：……。请简短说明用到的概念。
```

```text
请调用 _wayne：这三次访谈能否支持“所有用户都需要自动总结”？
指出结论边界，并告诉我什么证据会改变判断。
```

可追加“下次怎样识别这种问题”“举一个当前项目的例子”或“只给当前建议”。默认解释随任务需要调整，不固定输出教学模板。

本包继承调用方的模型与推理设置。行为约定为只读分析；实际工具权限由运行环境和父 agent 控制，配置不保证权限隔离。当前会话不会因安装自动刷新 agent 清单。

## 覆盖与原书访问

- 已发布 9 条原创概括，核验第 1—9 章的 16 处章节锚点。不是逐字翻译，也不表示已提取全书知识。
- 全部 18 章已建立可读取的结构索引。第 10—18 章当前只有索引，必须按需回查原文后才能回答其具体论述。
- 未配置原书时仍可使用已核验原则；精确引文、未覆盖章节和歧义问题会说明回查限制。
- [sources.json](sources.json) 保存版次、文件 SHA256、EPUB 内部位置与章节标题。不同文件即使同版也须重新定位核验，不静默接受指纹不匹配。

公共仓库不包含原书或全文提取物。持有匹配 EPUB 时，可设置 `WAYNE_SOURCE_EPUB` 为绝对路径；也可在**已安装目录**配置一次：

```powershell
# 将 $waynePackage 设置为实际安装目录：CODEX_HOME/agents/_wayne
py -3 "$waynePackage/source.py" configure --epub "<absolute-path-to-your-epub>"
py -3 "$waynePackage/source.py" check
py -3 "$waynePackage/source.py" read --chapter 1 --anchor ah0103 --limit 4000
```

`python` 可替换 Windows 的 `py -3`。`configure` 先验证文件及全部登记锚点，再写入本地 `source.local.json`；运行时顾问只用 `check/read`。环境变量优先于本地配置；显式 `--epub` 优先于环境变量。输出按字符限制，用 `--offset` 继续读取；EPUB 不编造重排页码。

本地配置不进入 Git，安装更新会保留目标目录的配置，也不会复制源目录的私有配置。书中的嵌入指令仅作分析材料处理。

## 验证状态

已完成的检查见 [验证记录](validation.md)。离线回归使用合成文本；真实 EPUB 只在维护者本地检查。行为验收用例见 [tests/cases.json](tests/cases.json)，**模型行为评估尚未运行**，试用效果尚无实证结论。

调用真实模型的评估须遵循仓库 AGENTS.md 的单独授权要求。日常明确请教顾问与批量付费行为评估分别处理。
