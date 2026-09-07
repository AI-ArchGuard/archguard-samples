# ArchGuard Samples

ArchGuard 的正常与故障合成样例工程集合，用于 Scanner、Platform 集成和端到端验证。

## 当前状态

M0 仓库基线已建立，Java 与 Go 样例工程尚未添加。

## 职责

- 提供小型、确定、可公开的 Java 和 Go 正常/违规样例。
- 为循环依赖、禁止依赖、解析失败和集成流程提供稳定夹具。
- 明确记录每个样例预期结果、适用契约版本和运行方式。
- 支持 Scanner 黄金测试及工作区端到端演示。

## 非职责

- 不实现生产业务功能、Scanner 规则、Platform 服务或 Gateway。
- 不复制真实客户仓库、许可证不明代码、凭据或个人数据。
- 不把故意违规样例误当成生产最佳实践。
- 不依赖外部网络或不可重复数据才能得到预期结果。

## 依赖与契约

- 样例的预期输出与 `archguard-scanner` 的版本化契约对应。
- `archguard-platform` 的端到端测试可引用固定版本或提交的样例。
- 跨仓库架构与工程规范以 [archguard-docs](https://github.com/AI-ArchGuard/archguard-docs) 为准。

## 本地验证

当前基线可执行：

```bash
git diff --check
git status --short
```

新增样例时必须在各样例目录记录构建命令和预期成功/失败结果；当前没有可运行的样例构建。
