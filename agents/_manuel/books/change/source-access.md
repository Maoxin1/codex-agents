# When Coffee and Kale Compete：来源与访问

这是 `_manuel` 按需读取的方法资料，无独立 agent 身份或调用入口。各书观点分别归属；综合分析是本次应用推导。


- 单书基础为 When Coffee and Kale Compete 第二版。标题页明确版次；提取文件 OPF 日期是 2018-04-15，不将其自动当作正式出版日，未核实 ISBN。详见 sources.json。
- 原件为 AZW3，供读取的 EPUB 经本地解包生成；记录两者指纹和解包警告。指纹保证定位文件一致，不证明内容完整性。正文图示可能承载额外含义，文字提取不能代替看图；需要图示时须读取指定图像，否则说明限制。
- 发布原则是选定段落的原创概括。其他章节先查原文；精确引文、歧义、跨流派比较须回查对应论述。失败时说明覆盖缺口，不凭记忆补成作者观点，不编造 EPUB 页码。
- Python 3.11+ 使用 `source.py check/read`。例如 `source.py read --chapter 7 --anchor "text:Unpacking Demand Reduction"`；锚点见 sources.json。按 limit/offset 分段，不能把截断部分说成已读。运行依赖同级 ../_shared，安装器会复制。
- 路径优先级为显式参数、CHANGE_SOURCE_EPUB、旧 ALAN_SOURCE_EPUB、本目录 source.local.json；运行时不 configure，不搜索无关私人文件。工具或来源缺失如实报告。
- 保留本书对 job 与活动、不同解释的区分。不要把 Competing Against Luck 的维度或 The Jobs to Be Done Playbook 的操作方法直接说成本书的同义术语；也不要把作者对其他流派的评价当作已裁定事实。
- 当前竞品表现、市场大小、真实客户心理和付费意愿需独立证据。本书历史案例不能当作当前事实或采用率预测。
