# The Jobs to Be Done Playbook：来源与访问

这是 `_manuel` 按需读取的方法资料，无独立 agent 身份或调用入口。各书观点分别归属；综合分析是本次应用推导。


- 依据 The Jobs to Be Done Playbook，2020，Jim Kalbach。版权页没有明确版次号，本包不猜测“第一版”。sources.json 记录 ISBN、文件指纹及选定章节覆盖。
- 本书介绍并组合多种方法，保留其归属：Switch、ODI、价值主张画布等不能都说成 Kalbach 原创，更不能把不同方法当作一个作者统一的理论。原文有图表，文字读取不能替代图示验证。
- Job map 表达完成主任务的阶段目标；不要把产品界面点击流程直接改名为 job map，也不要与购买或消费旅程混为一谈。job story 是组织讨论的方法，写出句式并不完成验证。
- 已发布原则为选定段落的原创概括。精确公式、引文、歧义或未覆盖论述须先查原文；缺失时说明限制，不从记忆复原，不编页码。
- Python 3.11+：`source.py check` 或 `source.py read --chapter N --anchor "text:章节小标题"`。sources.json 提供精确定位，按 limit/offset 分段，不能声称读过截断部分。安装器提供同级 ../_shared 公共读取库。
- 路径优先级为显式参数、JTBD_SOURCE_EPUB、旧 JIM_SOURCE_EPUB、本目录 source.local.json；运行时不 configure，不扫描无关文件。工具或来源失败明确报告。
