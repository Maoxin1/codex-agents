# 不安装 Codex 的两种入口

## 通用角色包

在仓库根目录运行（Python 3.11+；Windows 可用 `py` 替换 `python`）：

```sh
python tools/export_portable.py
```

输出 `dist/portable/portable-agents.zip`、八个独立 Markdown 角色文件以及 `catalog.json`。解压后，将单个角色文件全文放入 AI 工具的系统指令或项目指令；普通对话也可上传文件并说明要采用该角色。目标平台必须容纳该文件全文；没有承诺特定平台导入兼容性或语义效果。

生成器只读取 `managed-files.json` 中列出的角色配置与方法笔记，不打包原书、私人索引、私有覆盖文件、执行脚本或本地路径配置。每个角色包含源文件哈希便于追溯。适配器保留方法和角色边界，将文件读取改为使用已内联的资料；无外部工具时说明限制。通用包不可视为完整原书知识。

## 网页聊天入口

网页可切换八位顾问、进行多轮对话、下载全部通用包或单个角色。每次请求把该角色的完整公开资料作为高优先级指令；不会自动截断资料。角色切换清空对话。当前只支持文本，不提供联网搜索、上传、原书读取或知识库写入。

使用者填写自己的 OpenAI API Key 和账户可用的模型 ID，无需 Codex。密钥仅在页面内存和本次 HTTPS 转发中使用，不保存在数据库、localStorage、日志或源文件。刷新即清空。对话通过网站服务器发送到 OpenAI Responses API（`store:false`）；这不等于上游零数据保留。仅在信任的部署中填写密钥。此版本没有站长代付额度；错误响应不回显上游原始内容。实现依据 [OpenAI 官方文本生成文档](https://developers.openai.com/api/docs/guides/text)。

本地启动，先导出资料，再运行：

```powershell
New-Item -ItemType Directory web/data -Force
Copy-Item dist/portable/catalog.json,dist/portable/portable-agents.zip web/data
Set-Location web
node build.mjs
node local.mjs
```

打开 `http://localhost:8787`。Node.js 22+，无 npm 依赖。生产环境需要 HTTPS；`local.mjs` 仅监听本机。部署到 Sites 时把 `web` 的源文件和生成的 `data` 复制到独立 Site checkout，使用其实际 `.openai/hosting.json` 项目 ID；`node build.mjs` 输出 Cloudflare Worker `dist/server/index.js`，再按 Sites 的源同步、打包、部署流程发布。原始 GitHub 仓库不保存 Site 身份或密钥。新 Site 默认仅所有者可访问，给朋友使用前须明确调整访问范围。

检查：`python -m unittest discover -s tests -p test_portable.py`，在 `web` 目录运行 `node --test test.mjs`，以及原仓库的 `./tests/validate_repository.ps1`。接口测试使用模拟模型服务，不消耗 API 额度；真实模型质量、真实计费调用及跨平台语义一致性仍需另行验证。
