# Competing Against Luck 方法资料

供 `_manuel` 按问题读取；不单独安装或调用。

- [原则与主题路由](principles.md)
- [来源记录](sources.json)
- [访问规则与限制](source-access.md)

需要精确引文、歧义核对或未覆盖章节时，使用依法取得、版本匹配的本地 EPUB。Python 3.11+，仅标准库。从本目录运行：

```powershell
python source.py configure --epub '匹配原书.epub'
python source.py check
python source.py read --chapter 1 --limit 3000
```

章节与锚点以 sources.json 为准。configure 是用户配置步骤，验证成功才写 source.local.json；回答任务时只执行 check/read。分段读取检查 has_more 与 offset，不把截断当成全文。私有配置不提交，安装更新保留。

读取器支持 `CHOICE_SOURCE_EPUB` 环境变量；旧环境变量 `CLAYTON_SOURCE_EPUB` 继续作为来源配置兼容项，不恢复旧 agent。
