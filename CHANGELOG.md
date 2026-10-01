# Changelog

所有重要变更记录在此文件。版本遵循语义化版本；项目开发期从 `0.x.y` 开始。

## [Unreleased]

### Added

- 4G：14 个固定合成安全与恢复案例及清单校验；实际运行验证仍由 Platform/Web 测试承担，不启用正式 Evals 或真实模型。

- 初始化仓库治理、协作和质量基线。
- 采用 Apache License 2.0，并在 CI 中固定标准许可证校验和。
- 增加 Scanner S7 的三个合成 Java 项目、非法语法/未知规则/资源上限失败夹具，以及 Result Schema `0.1.0` 黄金报告与 SHA-256 digest。
- 增加无第三方依赖的样例清单校验和 Scanner `0.2.0` 端到端重复性、失败行为与性能上限验证脚本。
