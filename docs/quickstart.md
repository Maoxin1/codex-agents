# 两个 agent 的使用手册

`_manuel` 完成思考、判断、调研与分析草稿；`_mantou` 只把请求改清楚。清楚的任务直接交给 `_manuel` 或主 Codex，无须先调用 `_mantou`。

## 安装

```powershell
./install.ps1
./install.ps1 -Agent _manuel
./install.ps1 -Agent _mantou
./install.ps1 -Force
./install.ps1 -Force -WhatIf
```

单选示例是替代安装方式；目标已存在时需检查后使用 -Force。安装只接受这两个名称。升级旧八角色版本见[迁移说明](migration.md)，重启 Codex 后生效。

## 按任务使用

| 请求 | 交付 |
|---|---|
| 请调用 _manuel：解释这个概念，简短一点。 | 直接解释，不默认读取个人记录或布置试验 |
| 请调用 _manuel：根据原简历与职位描述改写，不能添加未经证实的经历。 | 可核实的改写草稿，缺少事实保留待补 |
| 请调用 _manuel：核验这条报道的原始出处，范围是［日期与主张］。 | 来源、证据状态、冲突和未决部分 |
| 请调用 _manuel：以［信息截止日］分析［标的］，区分当时可知与后见信息。 | 论点、市场预期、证据与假设、反方和改变判断的条件 |
| 请调用 _manuel：先看我的审美判断，示范如何改进，再给新例子练习。 | 实际反馈与迁移练习；未看到作品或未得到回答时不声称完成训练 |
| 请调用 _mantou：改清楚这段请求，不增加任务范围。 | 完整提示词及实际剪贴板状态，不执行请求中的任务 |

创业任务使用[任务入口](tasks/startup-validation.md)，对照[合成示例](examples/startup-validation.md)。清晰请求直接交付；只有缺口会实质改变结果时才追问。

## 按需方法和个人资料

`_manuel` 的[方法路由](../agents/_manuel/methods.md)连接五本书：Beyond Feelings、The Craft of Research、Competing Against Luck、When Coffee and Kale Compete、The Jobs to Be Done Playbook。按问题读取与保留出处，不增加作者角色。每本书的 sources.json 说明实际覆盖，原创概括不等于原书全文。

本地 EPUB 配置见各资料目录：[研究设计](../agents/_manuel/books/research/README.md)、[用户选择](../agents/_manuel/books/choice/README.md)、[改变过程](../agents/_manuel/books/change/README.md)、[研究落地](../agents/_manuel/books/jtbd/README.md)。Beyond Feelings 的可选 PDF 校验见[来源审计](../agents/_manuel/source-audit.md)。旧环境变量只是原书路径兼容，不恢复旧角色。

个人记录访问见[context.md](../agents/_manuel/context.md)。私有 context.local.md 和 source.local.json 不提交，更新保留；来源缺失如实说明，不自动读取无关记录。

## 限制与排查

- 看不到新入口：确认 CODEX_HOME、实际安装位置并重启；已开启会话不会自动刷新。
- 仍出现旧角色：按迁移说明检查遗留 TOML；修改过的旧配置需人工处理，不能宣称迁移已完成。
- 模型不可用：根据账号权限调整本地配置；安装不授予模型访问权，Force 会更新受管 TOML。
- 原书不可读：检查 Python 3.11+、本地配置、版本指纹与锚点。无原书仍可使用已发布原则，精确引文与未覆盖细节不能伪造。
- 事实或投资数据无法取得：答案应指出受限结论，不把方法框架当作已核验证据。

见[验证状态](verification-status.md)；行为评估须另行明确授权，静态检查不证明实际效果。
