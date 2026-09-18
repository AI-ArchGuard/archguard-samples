# java-architecture-violations

合成的双模块 Java 项目，故意覆盖非法包依赖、跳层依赖、Controller 直连 Repository、跨模块内部包、禁止类型/包/Maven 坐标、复杂度超限和缺少必要注解。

- Scanner：`0.2.0`
- Result Schema：`0.1.0`
- 预期退出码：`2`
- 预期 Finding：`13`
- 预期 Diagnostic：`0`

Finding 分布：复杂度 3、禁止组件 3、非法包依赖 1、内部模块访问 2、分层 2、必要注解 1、Controller→Repository 1。

```text
java -jar <archguard-scanner.jar> scan . --rules archguard-rules.yaml --output report.json
```

此项目只用于确定性违规验证，不是生产代码示范。
