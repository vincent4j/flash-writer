#!/usr/bin/env python3
"""Validate Flash Writer's cross-file workflow contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    required_files = (
        "SKILL.md",
        "README.md",
        "LICENSE",
        "agents/openai.yaml",
        "commands/flash-writer.md",
        "references/built-in-style.md",
        "references/writing-template.md",
        "references/real-example.md",
        "references/screenshot-guide.md",
        "scripts/profile_store.py",
        "scripts/project_setup.py",
        "tests/test_profile_store.py",
        "tests/test_project_setup.py",
    )
    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"缺少文件：{relative_path}")

    readable_files = [path for path in required_files if (ROOT / path).is_file()]
    documents = {
        path: read(path)
        for path in readable_files
        if Path(path).suffix in {".md", ".yaml"}
    }
    legacy_directory = "writer-" + "references"
    for relative_path, content in documents.items():
        require(
            legacy_directory not in content,
            f"{relative_path} 仍包含旧的双目录名称",
        )

    skill = documents.get("SKILL.md", "")
    require(len(skill.splitlines()) <= 500, "SKILL.md 超过 500 行")
    require(
        skill.startswith("---\nname: flash-writer\n"),
        "SKILL frontmatter 缺少正确名称",
    )
    require(
        "/flash-writer" in skill and "review" in skill,
        "SKILL 触发描述不完整",
    )
    require("article-start" in skill, "SKILL 缺少 article-start")
    require("article-update" in skill, "SKILL 缺少 article-update")
    require(
        "current_article_rules.found" in skill,
        "SKILL 缺少真实文章命中判断",
    )
    require(
        "L1 硬约束门禁" in skill and "L4 作者与读者终审" in skill,
        "SKILL 缺少四层自检",
    )
    require(
        "references/built-in-style.md" in skill
        and "内置默认风格 > Skill 通用规则" in skill,
        "SKILL 缺少内置默认风格或优先级",
    )
    for entry_name in ("直接开写", "一起梳理"):
        require(entry_name in skill, f"SKILL 缺少入口：{entry_name}")
    require(
        "同一份完整写作思路" in skill and "同一套正式写作流程" in skill,
        "SKILL 未声明双入口汇合到同一流程",
    )
    require(
        "通常每轮最多问 2 个问题" in skill
        and "特殊情况下最多 3 个" in skill,
        "SKILL 缺少一起梳理的单轮提问边界",
    )
    require(
        "仍须执行本步的规则与资料加载" in skill
        and "只有读取后新发现的冲突或关键缺失才追问" in skill,
        "SKILL 缺少一起梳理确认后的资料准备边界",
    )
    require(
        "高层论证路径或章节骨架" in skill
        and "补齐每章任务、证据、案例和资料用途" in skill,
        "SKILL 未区分高层骨架和正式可写大纲",
    )
    require(
        "【AI 建议，待确认】" in skill and "移除临时 AI 建议标记" in skill,
        "SKILL 缺少一起梳理的临时标记清理规则",
    )
    require(
        "只说“直接开写”但没有可识别的思路文件时，只询问一次文件" in skill,
        "SKILL 未区分已指定文件和无文件的直接开写",
    )
    require(
        "一起梳理”只展示读取摘要" in skill
        and "新提取且尚未确认的特征才请用户确认" in skill,
        "SKILL 缺少双入口的信息摘要或风格确认差异",
    )
    require(
        "整理前严格读取 `references/writing-template.md`" in skill
        and "把高层论证路径或章节骨架写进“写作思路”" in skill
        and "不得合并“写作风格”和“格式偏好”" in skill,
        "SKILL 缺少一起梳理的模板结构合同",
    )
    require(
        "填写“暂无”或“无特殊要求”" in skill
        and "这份完整模板成为干净的权威输入" in skill,
        "SKILL 缺少空栏目保留或权威输入规则",
    )

    command = documents.get("commands/flash-writer.md", "")
    require(
        "始终只使用一个 `references/` 目录" in command,
        "初始化命令未声明单一 references",
    )
    require("绝不覆盖" in command, "初始化命令缺少保留同名文件约束")
    require("reference_conflict" in command, "初始化命令缺少同名冲突处理")
    require("实际绝对路径" in command, "初始化回执未要求使用实际文件路径")
    require("内置默认风格" in command, "初始化命令未说明默认风格")
    require(
        "第三步 A：直接开写" in command and "第三步 B：一起梳理" in command,
        "初始化命令缺少双入口流程",
    )
    require(
        "通常每轮最多问 2 个问题" in command
        and "特殊情况下最多 3 个" in command,
        "初始化命令缺少一起梳理的提问边界",
    )
    require(
        "从第二步“推荐大纲”进入" in command,
        "初始化命令缺少双入口汇合点",
    )
    require(
        "不要再询问目录、入口或再次索要文件" in command
        and "用户明确说“一起梳理”时，不再询问入口" in command,
        "初始化命令缺少显式意图的自动路由",
    )
    require(
        "只说“直接开写”但当前上下文没有可识别的思路文件时，只询问一次文件" in command,
        "初始化命令未区分有文件和无文件的直接开写",
    )
    require(
        "展示读取摘要，但不再无条件询问" in command
        and "只有新提取且尚未确认的特征才确认" in command,
        "初始化命令缺少一起梳理后的条件式确认",
    )
    require(
        "保留模板中的 `》` 指令机制以及全部 10 个二级标题原名" in command
        and "不得另造“高层写作骨架”等栏目" in command,
        "初始化命令缺少模板原结构约束",
    )
    require(
        "加载个人档案和项目上下文" in command
        and "章节任务、证据、案例和资料用途" in command,
        "初始化命令缺少资料准备或可写大纲细化",
    )
    require(
        "写作思路校验通过，没有缺失或矛盾。进入大纲设计。" in command,
        "初始化命令使用了不准确的阶段回执",
    )

    template = documents.get("references/writing-template.md", "")
    require("告诉 AI" in template, "写作模板缺少中性 AI 文案")
    require("告诉 Claude" not in template, "写作模板仍绑定 Claude")
    for heading in ("原则与边界", "受众", "目标", "核心观点", "写作思路"):
        require(
            f"## {heading}（必填）" in template,
            f"写作模板未把 {heading} 标记为必填",
        )
    for heading in ("格式偏好", "写作风格", "图片素材"):
        require(
            f"## {heading}（选填）" in template,
            f"写作模板未把 {heading} 标记为选填",
        )
    require(
        "## 真实案例与事实（按需填写）" in template
        and "## 内容参考（按需填写）" in template,
        "写作模板缺少按需填写的事实或参考资料",
    )
    template_headings = (
        "原则与边界",
        "受众",
        "目标",
        "核心观点",
        "真实案例与事实",
        "写作思路",
        "写作风格",
        "格式偏好",
        "内容参考",
        "图片素材",
    )
    heading_positions = [template.find(f"## {heading}") for heading in template_headings]
    require(
        all(position >= 0 for position in heading_positions)
        and heading_positions == sorted(heading_positions),
        "写作模板未保留十个二级标题的名称或顺序",
    )
    require(
        "### 必须包含（按需填写）" in template
        and "### 禁止事项（按需填写）" in template,
        "写作模板缺少必须包含或禁止事项",
    )
    require(
        "可以全部留空" in template,
        "写作模板未说明非核心项可以留空",
    )
    require(
        "留空时自动使用 Flash Writer 内置默认风格" in template
        and "添加自己的写作风格" in template,
        "写作模板未说明默认风格或自定义方式",
    )

    built_in_style = documents.get("references/built-in-style.md", "")
    require(
        "用户当前要求、当前文章有效要求" in built_in_style,
        "内置风格缺少覆盖边界",
    )
    require(
        "不复用任何样本文章的主题、项目名称" in built_in_style,
        "内置风格缺少项目内容隔离说明",
    )

    example = documents.get("references/real-example.md", "")
    require(
        "article-start" in example and "article-update" in example,
        "案例缺少文章状态命令",
    )
    require(
        "L1 硬约束" in example and "L4 作者与读者终审" in example,
        "案例缺少四层自检",
    )
    require("确认完稿" in example, "案例缺少显式完稿")
    require(
        "直接开写" in example and "一起梳理" in example,
        "案例缺少双入口说明",
    )
    require(
        "仍会加载个人档案和项目资料" in example
        and "已确认骨架细化" in example,
        "案例缺少资料准备或高层骨架细化说明",
    )
    require(
        "只询问一次文件" in example and "只展示读取摘要" in example,
        "案例缺少无文件路由或条件式读取摘要",
    )
    require(
        "十个原名二级标题" in example
        and "空的选填部分填写“暂无”或“无特殊要求”" in example,
        "案例缺少完整模板落盘规则",
    )

    readme = documents.get("README.md", "")
    require(len(readme.splitlines()) <= 220, "README.md 超过 220 行")
    require("## 默认风格与自己的风格" in readme, "README 缺少自定义风格说明")
    require("agents/openai.yaml" in readme, "README 缺少 UI 元数据说明")
    require(
        "validate_workflow_contract.py" in readme,
        "README 缺少契约验证说明",
    )
    require(
        "python3 -m unittest discover" in readme,
        "README 缺少测试命令",
    )
    require(
        "直接开写" in readme and "一起梳理" in readme,
        "README 缺少双入口说明",
    )
    require(
        "同一份完整写作思路" in readme and "相同的写作流程和质量标准" in readme,
        "README 未说明双入口使用同一流程和质量标准",
    )
    require(
        "自动使用该文件及其所在目录" in readme
        and "只询问一次文件" in readme
        and "【AI 建议，待确认】" in readme,
        "README 缺少自动路由或临时建议标记说明",
    )
    require(
        "十个原名标题" in readme
        and "这份完整模板成为权威输入" in readme,
        "README 缺少完整模板结构或权威输入说明",
    )
    require("[MIT](LICENSE)" in readme, "README 缺少许可证链接")

    if errors:
        print("Flash Writer 工作流契约验证失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Flash Writer 工作流契约验证通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
