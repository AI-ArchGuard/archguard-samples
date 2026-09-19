# ArchGuard Samples

ArchGuard 的正常与故障合成样例工程集合，用于 Scanner、Platform 集成和端到端验证。

## 当前状态

阶段 1 S7 已提供三个合成 Java 项目、三类失败夹具、Scanner `0.2.0`/Result Schema `0.1.0` 黄金报告及重复性/性能验证脚本。最终接受以 Samples PR、Scanner 提供方 CI 和 `v0.2.0` 发布证据为准；Go 样例仍未启用。

## 职责

- 提供小型、确定、可公开的 Java、Go 和 Python 正常/违规样例；按路线逐个启用，不同时铺开。
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

静态验证样例清单、相对路径和黄金 digest：

```bash
python3 scripts/verify_samples.py .
```

使用已构建的 Scanner 执行全部黄金、失败、三次逐字节重复性和性能上限验证：

```bash
python3 scripts/verify_with_scanner.py \
  --jar ../archguard-scanner/scanner-cli/target/archguard-scanner.jar \
  --samples . \
  --results target/s7-results.json
```

样例不执行自身 Maven 构建，也不访问网络。`samples.json` 是样例版本、退出码、计数、重复次数和性能上限的机器入口；各样例 README 记录目的与预期结果。

## 许可证

本仓库采用 [Apache License 2.0](LICENSE)。
