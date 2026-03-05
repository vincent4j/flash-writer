# 更新日志

所有重要变更都记录在此文件中。

## [Unreleased]

### Changed
- 重构 `/flash-writer` 命令流程：介绍 → 询问目录 → 创建文件 → 引导填写 → 校验完备性 → 进入创作
- 新增写作思路校验步骤，检查必填项完备性和内容矛盾
- `references/` 目录已存在时自动回退为 `writer-references/`
- 文件名使用 markdown 链接格式，支持点击直接打开
- 更新 SKILL.md 触发条件，补充 `/flash-writer` 命令场景
- 更新 README.md 快速开始说明，匹配新流程

### Added
- 新增 `CHANGELOG.md` 更新日志文件
- 新增 `worklog/` 工作日志目录

## [0.1.0] - 2026-03-01

### Added
- 初始版本发布
- `/flash-writer` 命令，支持交互式创建写作模板
- 模板支持链接优先，去掉写死的文件名
- 完整写作工作流：对齐 -> 大纲 -> 确认 -> 写作
- 写作模板 (`references/writing-template.md`)
- 完整实际案例 (`references/real-example.md`)
- 截图最佳实践指南 (`references/screenshot-guide.md`)
