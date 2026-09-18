# Java 失败夹具

失败夹具固定 Scanner `0.2.0` 的失败关闭行为：

| ID | 输入 | 退出码 | 报告 | 稳定错误码 |
|---|---|---:|---|---|
| `invalid-syntax` | 非法 Java 语法 | `70` | 写入部分有效报告 | `java.syntax.invalid` |
| `unknown-rule` | 未知规则 ID | `64` | 不创建 | `config.schema.invalid` |
| `resource-limit` | `maxFiles: 1` | `70` | 不创建 | `java.limit.files` |

统一验证命令见仓库根 README。错误输出不得包含主机绝对路径、源码全文或异常堆栈。
