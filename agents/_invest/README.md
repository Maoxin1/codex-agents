# `_invest` 使用说明

`_invest` 是面向本地 Obsidian 知识库的长期投资研究与论点审计 Agent。配置入口是相邻目录中的 `_invest.toml`。

## 适用环境

- Codex GUI 工作区：适合连续研究、确认门、多轮复核和经单独授权后的知识库维护。
- Codex CLI：适合只读研究、自动化检查和行为冒烟测试。
- Obsidian 本地知识系统：适合保存原始资料、投资论点、估值版本、决策日志和事后复盘。

它不执行证券交易，也不替用户决定仓位或承担最终资本决策。

## 安装与知识库配置

在仓库根目录运行：

```powershell
./install.ps1
```

知识库位置按以下优先级解析：

1. 用户在当前请求中明确指定的 vault；
2. 工作区 `AGENTS.md` 定义的默认知识库；
3. 环境变量 `INVEST_VAULT_PATH`。

可为当前 PowerShell 会话设置环境变量：

```powershell
$env:INVEST_VAULT_PATH = '<path-to-your-obsidian-vault>'
```

若以上来源都未定义，Agent 会在确认门中询问，不会猜测其它目录。

## 私有案例地图

公开包只包含 `knowledge-map.md` 模板，不包含个人案例、持仓或笔记正文。安装后可复制模板建立本地覆盖：

```powershell
$agentRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$investRoot = Join-Path $agentRoot 'agents/_invest'
Copy-Item (Join-Path $investRoot 'knowledge-map.md') (Join-Path $investRoot 'knowledge-map.local.md')
```

只在 `knowledge-map.local.md` 中填写 vault 相对路径。该文件已被仓库内的 `.gitignore` 排除；不要把私有案例地图或 Obsidian 笔记提交到公开仓库。

## 原生调用

新开或重启 Codex 后使用：

> 请调用 `_invest`，研究［公司／代码］的当前投资机会。

或：

> 请调用 `_invest`，根据最新财报更新［公司／代码］的投资论点。先完成需求确认，不要直接研究或写入。

## 独立只读调用

```powershell
$agentRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
& (Join-Path $agentRoot 'agents/_invest/invoke_invest.ps1') -VaultPath '<path-to-your-obsidian-vault>' -Prompt '研究某家公司，投资期限3年，重点检查周期位置和估值。'
```

若未设置 `CODEX_HOME`，脚本默认安装在 `$HOME/.codex/agents/_invest`。独立脚本固定为只读，适合测试确认门或生成研究方案。需要连续确认、正式研究或写入 Obsidian 时，请在 Codex 交互会话中原生调用 `_invest`。

## 运行原则

1. 所有正式任务先评估需求。
2. 信息不足时只提必要问题。
3. 信息充分时仍先复述并等待确认。
4. 研究确认和文件写入确认是两道不同授权。
5. 历史案例只作证据与复盘素材，不因事后结果改写事前判断。
6. `_invest` 不执行证券交易。

## 文件说明

- `core.md`：身份、确认门、研究边界和决策纪律。
- `evidence.md`：证据标签、来源等级和冲突处理。
- `workflow.md`：任务路由与交付结构。
- `archive-rules.md`：Obsidian 读取、创建、更新和版本规则。
- `knowledge-map.md`：可公开的案例地图模板。
- `knowledge-map.local.md`：可选的私有案例覆盖，不纳入 Git。
- `CHANGELOG.md`：Agent 配置与测试驱动修订记录。
- `tests/cases.json`：三个轻量行为冒烟测试。
- `tests/validate_invest.py`：静态配置、隐私与可选 vault 验证。

## 验证

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python agents/_invest/tests/validate_invest.py
python agents/_invest/tests/validate_invest.py --vault '<path-to-your-obsidian-vault>'
```

静态验证只确认配置、路由、隐私边界和测试资产完整，不证明投资结论正确。行为测试方法见 `tests/README.md`。
