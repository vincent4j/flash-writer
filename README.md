# Flash Writer 闪电写手

Flash Writer 是一套 AI 长文写作工作流，适用于文章、教程、演讲稿和产品介绍。

> 作者负责思路、观点、资料和最终判断；AI 负责完整成稿。作者只需 review，AI 负责修改并把有效要求延续到后文。

## 它能做什么

- 根据写作思路和参考资料完成整篇长文，不要求作者先写成段落。
- 先确认受众、目标和大纲，再逐节写作，减少整篇返工。
- 借鉴参考资料中的事实和结构，但重新组织和表达，不复制原文。
- 根据自然语言 review 重写正文，并让同类要求在后续章节持续生效。
- 完稿前执行四层自检：硬约束、作者风格、内容事实、作者与读者终审。
- 把确认可复用的写作经验留给下一篇文章。

Flash Writer 始终只有一套正式写作流程，但提供两种准备写作思路的入口：

- **直接开写**：我已经准备好完整的写作思路，确认后按既定流程开始写作。
- **一起梳理**：我先说大致想法，AI 帮我逐步整理成完整的写作思路，确认后再开始写作。

两种入口最终都会形成同一份完整写作思路，使用相同的写作流程和质量标准。

调用时已经附上或指定思路文件，AI 会自动使用该文件及其所在目录，不再询问目录和入口。只说“直接开写”但没有文件时，AI 只询问一次文件，拿到后再开始；明确说“一起梳理”时也不再重复选择。只有裸命令且意图不明时才展示两个入口。

## 工作流程

```text
直接提供完整思路 ─────────┐
                           ├→ 确认完整写作思路
先说大致想法 → AI 对话梳理 ┘
→ 对齐任务和资料
→ 推荐并确认大纲
→ AI 逐节写正文
→ 作者 review，AI 重写
→ L1–L4 四层自检
→ 作者确认完稿
→ 沉淀可复用经验
```

正文阶段，作者可以直接说“铺垫太长”“观点写弱了”“这个案例不合适”。AI 会修改正文、检查同类问题，并把新要求应用到后续章节。作者不需要亲自重写段落。

## 快速开始

### 直接开写

把文件交给 AI：

```text
使用 $flash-writer，根据 @写作思路.md 完成这篇文章。正文由你写，我负责 review。
```

AI 会完整读取已有内容，只指出会导致整篇返工的关键缺失、矛盾和事实边界问题，不会重复询问已经写清楚的信息。

### 一起梳理

如果只有一个主题、观察或零散想法，直接告诉 AI：

```text
使用 $flash-writer，一起梳理。我想写一篇关于……的文章。
```

AI 会先听你自由表达，再根据写作模板中的关键缺口逐步追问。通常每轮最多问两个高影响问题，先确认高层论证路径或章节骨架，再严格按 [`references/writing-template.md`](references/writing-template.md) 的十个原名标题整理完整写作思路。高层骨架写进“写作思路”，不另造栏目；“写作风格”和“格式偏好”保持独立，没有内容的选填部分也填写“暂无”或“无特殊要求”。未确认的补充会标为 `【AI 建议，待确认】`，不确定事实会标为待核实；最终确认后移除临时建议标记，这份完整模板成为权威输入。AI 随后完成个人档案、项目资料和参考来源的读取，只展示读取摘要；仅在发现新冲突时追问，新提取且尚未确认的风格特征才确认。最后把已确认骨架细化成包含章节任务、证据、案例和资料用途的可写大纲。

### 写作思路模板

复制 [`references/writing-template.md`](references/writing-template.md) 到写作目录，填写后交给 AI。模板中的内容分为：

| 类型 | 内容 |
| --- | --- |
| 必须明确 | 原则与边界、受众、目标、核心观点、写作思路 |
| 按需填写 | 真实案例与事实、内容参考、必须包含、禁止事项 |
| 可以留空 | 写作风格、格式偏好、图片素材 |

“写作风格”留空时使用内置默认风格，其他非核心部分由 AI 根据文章需要判断。模板仍支持在每节使用 `》` 标记处理指令。

## 默认风格与自己的风格

“写作风格”留空时，Flash Writer 自动使用 [`references/built-in-style.md`](references/built-in-style.md)。这份内置风格强调真实问题、明确判断、自然口语、短段落、事实边界和移动端阅读。

添加自己的风格有三种方式：

1. 在模板中直接描述规则，例如“判断更直接”“少写背景”“段落保持短”。
2. 提供一篇或多篇自己写的文章链接或本地 Markdown 文件，AI 会提取风格特征并请你确认。
3. 写作过程中直接 review；AI 会重写正文，并把新要求应用到后续章节。

文章级要求和风格样本会覆盖内置风格。确认完稿时，可以把真正可跨文章复用的规则保存到个人写作档案，成为以后优先于内置风格的长期风格。

### 使用 `/flash-writer`

在支持命令的环境中输入：

```text
/flash-writer
```

命令会在用户选择的项目中创建或复用唯一的 `references/` 目录，只补充缺失的模板、案例和截图指南，不覆盖已有文件。

## 四层完稿自检

| 层级 | 检查重点 |
| --- | --- |
| L1 硬约束 | 章节、顺序、指定对象、篇幅、格式、图片和禁用项 |
| L2 作者风格 | 语气、节奏、转场、全文一致性和 AI 套话 |
| L3 内容与事实 | 观点支撑、结构、数据、引用和事实可靠性 |
| L4 作者与读者终审 | 是否准确表达作者观点，读者是否容易理解 |

AI 能够确定的问题会先修复，只把缺少依据或会改变作者核心观点的取舍交给作者。用户明确回复“确认完稿”后，才锁定最终版本并整理长期经验。

## 写作经验如何保存

个性化状态保存在当前用户目录，不写入文章目录或代码仓库：

```text
~/.flash-writer/
├── writing-profile.md
└── projects/
    └── <项目名>-<路径哈希>/
        ├── project-context.md
        └── feedback-log.md
```

- `writing-profile.md`：跨文章复用的写作规则。
- `project-context.md`：只在当前项目延续的背景和约束。
- `feedback-log.md`：当前文章的有效要求和反馈历史。

正常写作只加载当前有效规则，不反复读取全部历史。状态初始化、文章反馈更新和旧状态迁移由 [`scripts/profile_store.py`](scripts/profile_store.py) 处理；完整参数可运行 `python3 scripts/profile_store.py --help` 查看。

## 安装

将整个仓库放入 AI 工具能够发现的 Skill 目录，不要只复制 `SKILL.md`。

```text
~/.agents/skills/flash-writer/
```

安装后可以使用 `$flash-writer`；支持命令注册的环境也可以使用 `/flash-writer`。

本地开发推荐使用符号链接，让安装路径直接指向源码仓库：

```text
~/.agents/skills/flash-writer -> <Flash Writer 源码仓库>
```

## 主要文件

- [`SKILL.md`](SKILL.md)：权威工作流和执行规则。
- [`commands/flash-writer.md`](commands/flash-writer.md)：`/flash-writer` 初始化流程。
- [`references/writing-template.md`](references/writing-template.md)：写作思路模板。
- [`references/built-in-style.md`](references/built-in-style.md)：未指定风格时使用的内置默认风格。
- [`references/real-example.md`](references/real-example.md)：完整协作案例。
- [`references/screenshot-guide.md`](references/screenshot-guide.md)：需要 AI 截图时使用。
- [`scripts/profile_store.py`](scripts/profile_store.py)：写作状态工具。
- [`agents/openai.yaml`](agents/openai.yaml)：Codex UI 元数据。

## 开发验证

```bash
PYTHONPYCACHEPREFIX=/tmp/flash-writer-pycache \
  python3 -m py_compile scripts/profile_store.py

PYTHONPYCACHEPREFIX=/tmp/flash-writer-test-pycache \
  python3 -m unittest discover -s tests -v

python3 scripts/validate_workflow_contract.py
```

[`scripts/validate_workflow_contract.py`](scripts/validate_workflow_contract.py) 检查 Skill、命令、模板、案例和 README 的关键约定是否一致。提交前还应运行当前环境的 Skill 校验器。

## 许可证

[MIT](LICENSE)
