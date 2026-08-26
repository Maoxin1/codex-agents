# `_manuel` 使用说明

`_manuel` 是持久化的 critical thinking guide，配置入口为相邻目录中的 `_manuel.toml`。运行核心、原则路由、主题原则、来源元数据和测试均位于本目录。

## 原生调用

新开或重启 Codex 后，请求：

> 请调用 `_manuel`，分析：［你的问题、论证或决定］

在支持 agent type 的调度接口中使用 `agent_type = "_manuel"`。当前已经打开的根会话可能缓存旧的 agent 列表，新增配置不会热加载。

## 独立命令行调用

即使当前会话尚未重新扫描 agent，也可直接加载同一持久配置：

```powershell
& "$env:CODEX_HOME\agents\_manuel\invoke_manuel.ps1" -Prompt '请审计：新功能上线后投诉多了，所以它一定导致体验变差。'
```

默认使用 `gpt-5.6-terra` / `medium`。复杂、高价值且已有评测证明收益时，可显式传入 `-Model gpt-5.6-sol -Reasoning high`。

## 验证

```powershell
$env:PYTHONIOENCODING='utf-8'
python "$env:CODEX_HOME\agents\_manuel\tests\validate_manuel.py"
& "$env:CODEX_HOME\agents\_manuel\tests\run_behavior_eval.ps1" -CaseId 'causal_complaints'
```

可用行为用例 ID 见 `tests/cases.json`。行为脚本只检查最终回答的保守词法契约；它是回归烟雾测试，不替代人工语义审查。若要额外核验本地合法取得的原书 PDF，请先设置 `MANUEL_SOURCE_PDF` 环境变量。
