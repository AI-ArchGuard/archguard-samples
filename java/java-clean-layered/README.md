# java-clean-layered

合成的单模块 Java 项目，展示 Web → Application → Infrastructure → Domain 的允许依赖、Controller 经 Service 间接访问 Repository、必要注解和低复杂度代码。

- Scanner：`0.2.0`
- Result Schema：`0.1.0`
- 预期退出码：`0`
- 预期 Finding：`0`
- 预期 Diagnostic：`0`

```text
java -jar <archguard-scanner.jar> scan . --rules archguard-rules.yaml --output report.json
```

输出必须与 `expected/report.json` 逐字节一致，并匹配 `expected/report.sha256`。
