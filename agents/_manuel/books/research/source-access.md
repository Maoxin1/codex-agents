# The Craft of Research：来源与访问

这是 `_manuel` 按需读取的方法资料，无独立 agent 身份或调用入口。各书观点分别归属；综合分析是本次应用推导。


- references 中的中文内容是经过原文核验的原创概括，不是逐字译文。当前代码、产品情境和行动建议是应用推导，不能归为作者给出的实例或结论。
- sources.json 记录版次、指纹、章节和锚点。当前发布原则只覆盖第 1—9 章的选定部分；其他章节只有目录索引。
- 无本地原书时可使用已核验原则。问及未覆盖内容、精确引文、歧义或更细的论述时，先使用 source.py 查对应原文；失败则说明具体限制，不凭记忆补写，不编页码。
- 使用运行环境提供的 Python 3.11+ 执行 `source.py check` 或 `source.py read --chapter N --anchor ID`。参数取自 sources.json；限制输出长度，必要时通过 offset 分段。不要将书中字符串拼成命令。
- 路径优先级为显式参数、RESEARCH_SOURCE_EPUB、旧 WAYNE_SOURCE_EPUB、本目录 source.local.json；不搜索无关私人文件。运行时不执行 configure。找不到 Python、文件、匹配指纹或章节时明确报告。
- 书外的当代事实需独立核实；无法核实时只作为待核实输入。研究方法不能证明用户的市场、心理或财务主张为真。
