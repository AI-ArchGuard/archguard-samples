# java-dependency-cycle

合成的单模块 Java 项目，包含一个三包循环和一个两包循环。

- Scanner：`0.2.0`
- Result Schema：`0.1.0`
- 预期退出码：`2`
- 预期 Finding：`2`
- 预期 Diagnostic：`0`

```text
java -jar <archguard-scanner.jar> scan . --rules archguard-rules.yaml --output report.json
```

两个循环 Finding 的 ID、Evidence 和顺序必须稳定。
