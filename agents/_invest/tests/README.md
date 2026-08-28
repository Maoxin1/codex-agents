# `_invest` 冒烟测试

三个用例位于 `cases.json`：

- `CONFIRM-001`：完整需求也必须先等待确认；
- `EVIDENCE-001`：公司指引与历史事实必须分开；
- `WRITE-001`：研究确认不等于文件写入确认。

## 静态与便携性验证

在仓库根目录运行：

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python agents/_invest/tests/validate_invest.py
```

若要同时检查个人 Obsidian vault 是否可访问：

```powershell
python agents/_invest/tests/validate_invest.py --vault '<path-to-your-obsidian-vault>'
```

也可设置 `INVEST_VAULT_PATH`，验证器会自动读取它。默认测试不依赖维护者的本机目录或私有案例。

## 行为验证

新开 Codex 会话后，逐个发送用例输入并明确要求调用 `_invest`。

- `CONFIRM-001` 在第一轮观察；不得确认执行。
- `EVIDENCE-001` 使用两轮：第一轮让 `_invest` 复述测试任务，第二轮明确确认后再提供 fixture。
- `WRITE-001` 先确认研究但不确认写入，检查它是否停在写入门。

每个用例必须满足全部 `expected`，且不出现任何 `forbidden` 行为。语义等价即可，不按固定关键词判定。

测试通过只表示流程纪律符合当前契约，不表示某项投资研究、估值或未来回报正确。
