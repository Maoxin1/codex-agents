# 2026-10-27 支持文件读取验证

原生 `_wayne` 和修正后的独立 CLI 路径均已成功读取支持文件。这验证读取通路，不代表全部顾问、原书细节或长期使用效果已验证。

## 原因与修复

首轮评估使用 `--ignore-user-config`，同时遗漏了本机已有的 `windows.sandbox` 配置。受影响的 CLI 会话无法读取测试工作区，因而六位需要支持文件的顾问只能给出降级回答。

在同一工作区、同一份公开测试文件上，用同一 `:read-only` 权限配置做了不调用模型的对照：

| Windows 后端 | 返回码 | 文件读取 |
|---|---|---|
| `unelevated` | 1 | Access denied |
| 本机已配置的 `elevated` | 0 | 返回预期测试文本 |

这里的 `elevated` 是 Codex 已配置的 Windows 隔离后端；测试仍使用只读权限，没有切换到 `danger-full-access`。

评估器现在只从用户配置提取已配置的 Windows 隔离后端，显式传入保持隔离的 CLI 会话，不加载用户的模型、插件或宽权限偏好。真实模型调用前，先在同一后端执行一个不消耗模型额度的只读测试；没有有效配置或读取失败就停止。

平台说明参见 [OpenAI permissions 文档](https://learn.chatgpt.com/docs/permissions)和[`--ignore-user-config` 说明](https://learn.chatgpt.com/docs/non-interactive-mode)。

## 两次最小真实验证

1. 通过 `agent_type=_wayne` 原生调用，读取 `core.md`、`principles.md` 和 W04 路由的 `references/sources.md`，返回原则标题、短句、应用及工具计算的 SHA256。父会话独立核对文件内容及哈希，全部一致。
2. 在独立 CLI 会话中，使用 `gpt-6.1-sol / high`、只读权限、禁用联网搜索、保留本机 Windows 隔离后端，再执行同样的读取挑战。返回码 0，三个哈希全部一致，JSONL 中可见实际命令执行记录。

原生调用继承父模型 `gpt-6.1-sol`；未更改任何已发布顾问的默认模型，也未读取私人知识库或原书。

| 公共支持文件 | SHA256 |
|---|---|
| `_wayne/core.md` | `F1AF0A0168D653040C5BC76159385ABF6FE4D6B43E0AEE114BBCA307A436A077` |
| `_wayne/principles.md` | `B56BA274886616AB1892E3E1A9F4DA69F3893D7B149EBABAADC3C6439AF5EBE3` |
| `_wayne/references/sources.md` | `BC0957F4A6F8072A813BA13D93195812A5A400ED2BE61A5CA56412406817A06D` |

W04 的标题为“保留出处与笔记边界”。两次都正确区分了顾问概括与原书引文，未把该文件中的文字当作原书逐字引文。

## 对首轮结论的影响

[首轮 16 份回答](evaluation-results-2026-10-27.md)保留为来源受限条件下的文本记录，不升级成“书籍知识增强已证明”的对比结果。本轮仅增加两次最小模型调用，没有重跑整套评估。

目前可以确认 `_wayne` 的原生注册、支持文件路由和读取能力，以及修正后的 CLI 读取通路。其他顾问的原生调用、正常剪贴板操作、原书精确引用与跨书协作仍按需逐步验证。
