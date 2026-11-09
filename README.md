# Codex Agents

为已经会使用 Codex agent 的人提供两个入口：`_manuel` 帮助完成具体的思考、调研与行动任务；`_mantou` 改清楚请求并交付提示词。项目仍在验证实际增益，不承诺比普通模型对话更准确。

## 从任务开始

| 任务 | 准备材料 | 入口与交付 | 当前边界 |
|---|---|---|---|
| 验证创业想法 | 用户情境、现有替代、证据与资源约束 | `_manuel`：关键假设、一项试验与调整条件；[直接开始](docs/tasks/startup-validation.md) | 首个重点验证场景，未证明市场增益 |
| 提升审美判断 | 作品、用途、受众、参照与自己的判断 | `_manuel`：评价依据、示范与反馈 | 视觉检查依赖环境，专业方法和训练效果待验证 |
| 分析指定时点的投资机会 | 标的、信息截止日、期限与原始资料 | `_manuel`：证据、市场预期、估值假设、反方与证伪条件 | [研究规范](agents/_manuel/tasks/investment.md)可用，预测增益未验证 |
| 改写岗位简历 | 职位、原简历、可核实经历与篇幅 | 已有明确请求交给 `_manuel` 或主 Codex；需先改清请求时用 `_mantou` | 不虚构经历，提示词改写不等于简历专业认证 |
| 核验事实或审阅论证 | 具体主张、时间范围与原始材料 | `_manuel`：证据状态、来源与未决部分 | [核验规范](agents/_manuel/tasks/verification.md)按需加载，工具限制如实披露 |

## 安装与使用

在 PowerShell 中获取仓库并安装：

```powershell
git clone https://github.com/Maoxin1/codex-agents.git
cd codex-agents
./install.ps1
```

已有仓库时进入其根目录运行安装即可。单选、更新与预览命令见[使用手册](docs/quickstart.md)；已有旧角色时按[迁移说明](docs/migration.md)处理。

默认安装全部两个 agent。`_manuel` 的书籍和任务资料随其支持目录安装，没有其他可选 agent，也不需要选作者或召集多个顾问。安装目录为 CODEX_HOME/agents，未配置时为用户主目录下的 .codex/agents；安装后重启 Codex。

> 请调用 _manuel：检查这个创业想法。材料是［记录］，约束是［资源与时间］。指出最值得验证的不确定性，给一项能取得行为证据的下一步。

> 请调用 _manuel：根据我的判断与这份作品，指出一个关键遗漏，示范修改，再给不同条件的新例子让我练习。

> 请调用 _mantou：把这段需求改清楚，保持简短，不增加任务范围。

旧八角色版本的用户先读[迁移说明](docs/migration.md)。安装更新不会擅自删除用户修改过的旧配置；迁移脚本支持预览、备份与识别，残留情况会报告。

## 资料与边界

五本书的方法按具体问题读取，保留作者、版次、适用范围与限制；资料集中在 `_manuel` 内。精确引文、歧义与未覆盖内容须核验依法取得、版本匹配的原书，不能把方法当作当代事实证据。新增书籍优先增加资料，不增加 agent。

知识库按用户指定路径、工作区 AGENTS.md 或 MANUEL_VAULT_PATH 解析。私人入口可存于 context.local.md；聊天记录需用户提供导出或可用连接，没有自动历史导入或后台监控。`_manuel` 提供分析与草稿；外部执行由用户或获授权主会话完成。

完整入口见[文档导航](docs/README.md)：使用、方法资料、评估、维护与历史记录均从这里查找。

## 验证

```powershell
./tests/validate_repository.ps1
```

离线检查覆盖精确角色集合、安装与迁移、来源读取、配置和用例资产，不证明回答质量。旧版本结果不代表新版本；真实用户案例仍待收集。见[验证状态](docs/verification-status.md)、[评估方案](docs/evaluation-plan.md)与[创业对照](docs/evaluation/startup-pilot.md)。模型评估需明确授权，不在默认 CI 中运行。

原书全文、私人笔记和投资数据不随仓库分发。配置和原创支持材料采用 [MIT License](LICENSE)，第三方资料权利归原权利人。
