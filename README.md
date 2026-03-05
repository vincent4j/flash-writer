# flash-writer

Claude Code 写作技能，快速产出长文。填好模板，产出成品文章。

## 它做什么

你准备一份写作思路文件（模板），描述你要写什么——受众、目标、大纲、风格、参考资料。然后告诉 Claude：`@你的文件名.md 按这个要求执行`。flash-writer 接管整个流程：

1. **对齐** —— 阅读你的模板、参考资料和风格样本
2. **大纲** —— 提出结构化大纲，含每节说明
3. **确认** —— 多轮大纲调整，直到你满意
4. **写作** —— 逐节产出完整文章，匹配你的风格

## 安装

复制到 Claude Code 技能目录：

```bash
cp -r . ~/.claude/skills/flash-writer
```

或者用软链接：

```bash
ln -s /path/to/flash-writer ~/.claude/skills/flash-writer
```

## 快速开始

1. 复制 `references/writing-template.md` 到你的项目目录
2. 填写各部分（受众、目标、大纲、风格、参考资料）
3. 把参考资料放到 `参考资料/` 目录
4. 告诉 Claude：`@你的文件名.md 按这个要求执行`

完整案例请看 `references/real-example.md`。

## 文件结构

```
flash-writer/
├── SKILL.md                        # 主技能文件（规则 + 工作流）
└── references/
    ├── writing-template.md         # 可复制的写作模板
    ├── real-example.md             # 完整实际案例
    └── screenshot-guide.md         # 截图最佳实践
```

## 许可证

MIT
