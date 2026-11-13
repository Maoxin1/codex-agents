# 文档导航

当前仓库只提供 `_manuel` 与 `_mantou`。新用户从使用手册开始；旧安装先检查迁移说明。

## 使用

| 需要做什么 | 文档 |
|---|---|
| 安装、选入口、调用和排错 | [使用手册](quickstart.md) |
| 区分 main、固定源码和历史发行版 | [版本与下载入口](release-status.md) |
| 从旧八角色版本升级 | [迁移说明](migration.md) |
| 检查模型、运行环境与本地覆盖 | [兼容性](../COMPATIBILITY.md) |
| 使用思考与行动伙伴 | [_manuel 指南](../agents/_manuel/README.md) |
| 改清楚请求并取得提示词 | [_mantou 指南](../agents/_mantou/README.md) |

## 任务与方法

| 需要做什么 | 文档 |
|---|---|
| 把创业想法推进到验证行动 | [任务入口](tasks/startup-validation.md)、[合成示例](examples/startup-validation.md) |
| 按问题选择五本书的方法 | [方法路由](../agents/_manuel/methods.md) |
| 调研并训练分析能力 | [调研与学习](../agents/_manuel/research.md) |
| 核验事实 | [核验规范](../agents/_manuel/tasks/verification.md) |
| 研究投资机会 | [投资研究](../agents/_manuel/tasks/investment.md)、[证据与估值](../agents/_manuel/tasks/investment-evidence.md) |
| 使用授权的个人记录 | [记录访问与接续](../agents/_manuel/context.md) |

## 验证与维护

- [当前验证状态](verification-status.md)：已有证据与尚未验证的能力。
- [评估方案导航](evaluation/README.md)：单轮对照、创业试用与多轮人工协议。
- [测试说明](../tests/README.md)：离线检查与模型评估的区别、运行入口。
- [贡献规范](../CONTRIBUTING.md)、[发布流程](../RELEASING.md)、[安全反馈](../SECURITY.md)、[变更日志](../CHANGELOG.md)。
- [两个 agent 的产品边界](agent-consolidation-review.md)：当前维护决定。
- [历史索引](history/README.md)：旧设计、结果和变更快照，不作为当前安装指引。

## 仓库结构

| 位置 | 职责 |
|---|---|
| agents/ | 两个 TOML 与各自支持包；`_manuel/books/` 和 tasks/ 是资料，不是额外 agent |
| install.ps1、managed-files.json | 安装入口与明确分发的文件清单 |
| migrate-legacy.ps1、migration/ | 旧入口迁移脚本与历史指纹；与用户指南 docs/migration.md 配套 |
| docs/ | 使用、任务示例、评估与历史记录 |
| tests/ | 仓库级离线回归及明确授权后才运行的评估工具 |
| .github/ | CI 与协作模板 |

用户文档、安装包和历史记录各自保留用途；私人原书、笔记、配置覆盖与评估输出不进入公共分发清单。
