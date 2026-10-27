# `_manuel` 使用说明

`_manuel` 是持久化的 critical thinking guide，配置入口为相邻目录中的 `_manuel.toml`。运行核心、原则路由、主题原则、来源元数据和测试均位于本目录。

## 原生调用

新开或重启 Codex 后，请求：

> 请调用 `_manuel`，分析：［你的问题、论证或决定］

在支持 agent type 的调度接口中使用 `agent_type = "_manuel"`。当前已经打开的根会话可能缓存旧的 agent 列表，新增配置不会热加载。

## 独立命令行调用

即使当前会话尚未重新扫描 agent，也可直接加载同一持久配置：

```powershell
$agentRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
& (Join-Path $agentRoot 'agents/_manuel/invoke_manuel.ps1') -Prompt '请审计：新功能上线后投诉多了，所以它一定导致体验变差。'
```

默认使用 `gpt-5.6-terra` / `medium`。复杂、高价值且已有评测证明收益时，可显式传入 `-Model gpt-5.6-sol -Reasoning high`。

## 验证

```powershell
$agentRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$env:PYTHONIOENCODING='utf-8'
python (Join-Path $agentRoot 'agents/_manuel/tests/validate_manuel.py')
& (Join-Path $agentRoot 'agents/_manuel/tests/run_behavior_eval.ps1') -CaseId 'causal_complaints'
```

可用行为用例 ID 见 `tests/cases.json`。行为脚本只检查最终回答的保守词法契约；它是回归烟雾测试，不替代人工语义审查。若要额外核验本地合法取得的原书 PDF，请先设置 `MANUEL_SOURCE_PDF` 环境变量。

脚本输出 `LEXICAL SMOKE PASSED/FAILED`，在系统临时目录的 `codex-agents-evals/<运行 ID>/` 中保留 `answer.txt`、`cli.log` 和 `record.json`。可用 `-OutputDirectory` 指定仓库以外的私有目录；记录包括模型请求、reasoning、配置与支持文件哈希、耗时、退出码及词法检查结果。语义评审状态始终初始为 `pending`，需另行人工评阅。日志可能包含私人输入或路径，不自动提交。此脚本验证独立加载配置的路径，原生 agent 注册与调度需单独验证。
