# 测试与评估工具

从仓库根目录运行。默认验证使用合成数据和模拟 CLI，不调用模型服务，也不修改真实 Codex 安装。

## 完整离线检查

```powershell
./tests/validate_repository.ps1
```

需要 PowerShell 与 Python 3.11+，脚本可使用 python 或 py 启动器。CI 在 Windows 的 Python 3.11、3.13 上运行同一入口。

| 文件 | 覆盖范围 |
|---|---|
| validate_install.ps1 | 两个入口的默认及单选安装、旧参数拒绝、预览、冲突预检与私人文件保留 |
| validate_content.py | Markdown 相对链接、TOML/JSON 解析与公开文本隐私模式 |
| test_two_agents.py | 精确发布集合、当前文档与协作模板、旧入口迁移备份和冲突处理 |
| test_install_manifest.py | 受管清单与 Git 跟踪的 agent 文件一致，不分发私人覆盖 |
| test_book_methods.py、test_research_source.py | 合成 EPUB 的边界、锚点、读取限额、配置与环境变量优先级 |
| test_model_overrides.py | 两个 agent 的默认模型及允许本地覆盖后的其他约束 |
| test_eval_record.py、test_eval_sandbox.py | 模拟 CLI 的记录和失败处理、隔离配置；不运行真实模型 |
| agents/*/tests/validate_*.py | 各 agent 的配置与案例资产检查，由完整验证入口调用 |

`-AllowModelOverride` 仅用于有意修改本地模型配置的检查；发布和 CI 仍使用严格默认值。MANUEL_SOURCE_PDF 未配置时跳过原书核验，不把合成读取器测试称为原书验证。

## 行为评估：需要明确授权

| 入口 | 用途与限制 |
|---|---|
| run_coding_eval.py | 执行[当前两题配对方案](../docs/evaluation-plan.md)，需要 --authorize-model-calls 与仓库外输出目录；配置覆盖不等于原生调度 |
| agents/_manuel/tests/run_behavior_eval.ps1 | 运行指定单轮案例并保存记录；词法结果只作冒烟检查，语义标准仍需人工评阅 |
| [多轮人工协议](../docs/evaluation/task-routing.md) | 根据用户实际后续回答继续，不能把所有轮次压成一次输入 |

详细方案见[评估导航](../docs/evaluation/README.md)。新增或重跑模型评估须确认授权范围；不得把“整理仓库”或“运行测试”自动解释为付费模型调用授权。

修改分发文件时，同步更新 managed-files.json 并将增删纳入 Git 索引，再运行完整检查。测试数据只用合成内容；真实回答、日志和私人书籍保存在仓库外。
