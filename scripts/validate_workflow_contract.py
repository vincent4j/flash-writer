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
        "tests/test_profile_store.py",
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

    command = documents.get("commands/flash-writer.md", "")
    require(
        "始终只使用一个 `references/` 目录" in command,
        "初始化命令未声明单一 references",
    )
    require("绝不覆盖" in command, "初始化命令缺少保留同名文件约束")
    require("实际绝对路径" in command, "初始化回执未要求使用实际文件路径")
    require("内置默认风格" in command, "初始化命令未说明默认风格")

    template = documents.get("references/writing-template.md", "")
    require("告诉 AI" in template, "写作模板缺少中性 AI 文案")
    require("告诉 Claude" not in template, "写作模板仍绑定 Claude")
    for heading in ("原则", "受众", "目标", "写作思路", "内容参考"):
        require(
            f"## {heading}（必填）" in template,
            f"写作模板未把 {heading} 标记为必填",
        )
    for heading in ("文章类型", "格式偏好", "写作风格", "图片素材"):
        require(
            f"## {heading}（选填）" in template,
            f"写作模板未把 {heading} 标记为选填",
        )
    require(
        "选填项可以全部留空" in template,
        "写作模板未说明选填项可以留空",
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
