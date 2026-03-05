# Flash Writer 闪电写手

AI 驱动的结构化写作工作流。你提供思路，AI 引导你从大纲到成品，大幅降低写作难度、提升创作效率。

## 它做什么

按照模板完善你的写作思路——受众、目标、章节大纲、风格、参考资料，AI 自动接管后续流程：

1. **对齐** —— 阅读你的思路、参考资料和风格样本，确认理解无误
2. **大纲** —— 基于你的思路生成结构化大纲，含每节说明
3. **确认** —— 多轮大纲调整，直到你满意
4. **写作** —— 逐节产出完整文章，匹配你的风格和受众

## 适配工具

通过 [Skills CLI](https://skills.sh/) 一键安装，支持 40+ 主流 AI 编程工具：

| 类别 | 工具 |
|------|------|
| **直接支持** | Claude Code, Cursor, Windsurf, Cline, Codex, GitHub Copilot, Gemini CLI, OpenCode, Roo Code, Qwen Code |
| **通过 symlink** | Augment, OpenClaw, CodeBuddy, Goose, Junie, Kiro CLI, Kode, Continue, Droid, Pi, Qoder, Zencoder 等 |

## 安装

**推荐：Skills CLI（适用于所有支持的工具）**

```bash
npx skills add vincent4j/flash-writer
```

**仅 Claude Code：**

```bash
git clone git@github.com:vincent4j/flash-writer.git ~/.claude/skills/flash-writer
```

## 快速开始

**方式一：`/flash-writer` 命令（Claude Code 推荐）**

在 Claude Code 中输入 `/flash-writer`，按引导操作：
1. 选择文件存放目录（默认项目根目录）
2. 自动创建 `references/` 文件夹，含写作模板和参考案例
3. 打开 `writing-template.md`，填写你的写作思路
4. 告诉 AI「已写完」，系统自动校验完备性后进入创作流程

**方式二：手动创建模板（适用于所有工具）**

1. 复制 `references/writing-template.md` 到你的项目目录
2. 填写各部分（受众、目标、大纲、风格、参考资料）
3. 告诉 AI：`@你的文件名.md 按这个要求执行`

完整案例请看 `references/real-example.md`。

## 文件结构

```
flash-writer/
├── SKILL.md                        # 主技能文件（规则 + 工作流）
├── CHANGELOG.md                    # 更新日志
├── commands/
│   └── flash-writer.md             # /flash-writer 命令定义
├── references/
│   ├── writing-template.md         # 可复制的写作模板
│   ├── real-example.md             # 完整实际案例
│   └── screenshot-guide.md         # 截图最佳实践
└── worklog/                        # 每日工作日志和复盘
```

## 许可证

MIT
