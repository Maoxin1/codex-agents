# 从八角色版本迁移到两个 agent

当前只发布 `_manuel` 和 `_mantou`。`-All` 和六个旧名称不再是安装参数。书籍方法已放入 `_manuel/books/`；旧角色资料可从 Git 历史查看，不再分发独立角色。

先更新当前两个 agent，再预览旧入口迁移：

```powershell
./install.ps1 -Force
./migrate-legacy.ps1 -WhatIf
./migrate-legacy.ps1
```

路径来自 CODEX_HOME，未设置时为用户主目录下的 .codex。迁移脚本只处理本项目六个旧名称，不碰其他自定义 agent。

- 旧 TOML 的 SHA-256 与本项目历史发布内容一致时，先复制到 CODEX_HOME/agent-migration-backups/随机目录，校验备份，再移除原入口。备份在 agents 目录之外。
- 修改过或无法识别的 TOML 原样保留并报告。此时尚未完成两入口迁移；请比较自定义内容，将仍需要的方法整理到 `_manuel` 的私有资料后，自行把对应旧 TOML 移出 agents 目录。脚本没有强制删除模式。
- 原书 source.local.json 会备份并复制到新的 books 子目录；原文件保留。目标已有不同内容时保留双方，报告冲突。旧环境变量仍可读取；新变量为 RESEARCH_SOURCE_EPUB、CHOICE_SOURCE_EPUB、CHANGE_SOURCE_EPUB、JTBD_SOURCE_EPUB。
- 旧支持目录、私人笔记、投资知识库索引与其他文件保持原样。保留目录不等于继续注册 agent，脚本不递归删除目录。
- `-WhatIf` 不创建备份或写入任何文件；重复迁移不会再次处理已移除入口。遇到符号链接或目录重定向会停止。

回滚时，将备份中的相应 TOML 复制回 CODEX_HOME/agents；若已出现同名文件，先人工比较，避免覆盖修改。迁移保留了旧支持目录。重启 Codex 让入口变化生效，已开启会话不会自动刷新。

只改变仓库不会改变已安装的本地 agent。安装命令负责更新受管文件，迁移命令负责退役已识别旧入口；执行后检查警告，不能把部分迁移称为全部完成。
