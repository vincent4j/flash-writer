#!/usr/bin/env python3
"""Initialize and load Flash Writer's persistent personalization files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


ACTIVE_START = "<!-- flash-writer:active:start -->"
ACTIVE_END = "<!-- flash-writer:active:end -->"
DEFAULT_MAX_CHARS = 4000

PROFILE_TEMPLATE = f"""# Flash Writer 个人写作档案

只保存已经确认、能够跨文章复用的有效规则。不要写入具体文章内容、项目事实、修改历史或已废止规则。

{ACTIVE_START}
## 有效写作规则

## 有效协作偏好

{ACTIVE_END}
"""

PROJECT_CONTEXT_TEMPLATE = f"""# Flash Writer 项目上下文

仅在存在需要跨写作任务延续的项目上下文时填写；独立文章可以保持为空。不预设文章属于系列。

{ACTIVE_START}
## 有效上下文

{ACTIVE_END}
"""

FEEDBACK_LOG_TEMPLATE = """# Flash Writer 反馈日志

按文章追加用户在写作过程中提出的修改意见和已执行修改。正常开始新文章时不要全文加载本文件；仅在当前文章完稿整理时读取对应章节。

每篇文章使用以下结构：

## <写作思路文件名或文章标识>

### 当前有效要求

### 原始反馈
"""


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def find_project_root(project_dir: str) -> Path:
    start = Path(project_dir).expanduser().resolve()
    if start.is_file():
        start = start.parent
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return start


def project_key(project_root: Path) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", project_root.name).strip("-._")
    if not slug:
        slug = "project"
    digest = hashlib.sha256(str(project_root).encode("utf-8")).hexdigest()[:10]
    return f"{slug}-{digest}"


def resolve_state(project_dir: str, global_dir: str | None) -> dict[str, object]:
    project_root = find_project_root(project_dir)
    profile_root = (
        Path(global_dir).expanduser().resolve()
        if global_dir
        else Path.home() / ".flash-writer"
    )
    key = project_key(project_root)
    project_state = profile_root / "projects" / key
    return {
        "project_root": project_root,
        "project_key": key,
        "paths": {
            "writing_profile": profile_root / "writing-profile.md",
            "project_context": project_state / "project-context.md",
            "feedback_log": project_state / "feedback-log.md",
        },
    }


def initialize(paths: dict[str, Path]) -> list[str]:
    created = []
    templates = {
        "writing_profile": PROFILE_TEMPLATE,
        "project_context": PROJECT_CONTEXT_TEMPLATE,
        "feedback_log": FEEDBACK_LOG_TEMPLATE,
    }
    for key, path in paths.items():
        if write_if_missing(path, templates[key]):
            created.append(key)
    return created


def active_content(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if ACTIVE_START not in text or ACTIVE_END not in text:
        return text.strip()
    return text.split(ACTIVE_START, 1)[1].split(ACTIVE_END, 1)[0].strip()


def compact_content_payload(
    path: Path, content: str, max_chars: int
) -> dict[str, object]:
    char_count = len(content)
    needs_compaction = char_count > max_chars
    return {
        "path": str(path),
        "char_count": char_count,
        "needs_compaction": needs_compaction,
        "content": "" if needs_compaction else content,
    }


def compact_payload(path: Path, max_chars: int) -> dict[str, object]:
    return compact_content_payload(path, active_content(path), max_chars)


def current_article_rules(path: Path, article: str | None) -> str:
    if not article:
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    article_heading = f"## {article}".strip()
    start = None
    end = len(lines)
    for index, line in enumerate(lines):
        if line.strip() == article_heading:
            start = index + 1
            continue
        if start is not None and line.startswith("## "):
            end = index
            break
    if start is None:
        return ""

    section = lines[start:end]
    rules_start = None
    rules_end = len(section)
    for index, line in enumerate(section):
        if line.strip() == "### 当前有效要求":
            rules_start = index + 1
            continue
        if rules_start is not None and line.startswith("### "):
            rules_end = index
            break
    if rules_start is None:
        return ""
    return "\n".join(section[rules_start:rules_end]).strip()


def command_init(args: argparse.Namespace) -> int:
    state = resolve_state(args.project_dir, args.global_dir)
    paths = state["paths"]
    created = initialize(paths)
    print(
        json.dumps(
            {
                "ok": True,
                "created": created,
                "project_root": str(state["project_root"]),
                "project_key": state["project_key"],
                "paths": {key: str(path) for key, path in paths.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_load(args: argparse.Namespace) -> int:
    state = resolve_state(args.project_dir, args.global_dir)
    paths = state["paths"]
    initialize(paths)
    profile = compact_payload(paths["writing_profile"], args.max_chars)
    project = compact_payload(paths["project_context"], args.max_chars)
    current_rules = current_article_rules(paths["feedback_log"], args.article)
    current = compact_content_payload(
        paths["feedback_log"], current_rules, args.max_chars
    )
    current["article"] = args.article
    current["loaded"] = bool(args.article)
    print(
        json.dumps(
            {
                "ok": True,
                "project_root": str(state["project_root"]),
                "project_key": state["project_key"],
                "writing_profile": profile,
                "project_context": project,
                "current_article_rules": current,
                "feedback_log": {
                    "path": str(paths["feedback_log"]),
                    "history_loaded": False,
                },
                "token_policy": {
                    "loaded_active_sections": 3 if args.article else 2,
                    "feedback_history_loaded": False,
                    "max_chars_per_active_file": args.max_chars,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_migrate(args: argparse.Namespace) -> int:
    state = resolve_state(args.project_dir, args.global_dir)
    paths = state["paths"]
    legacy_root = (
        Path(args.legacy_dir).expanduser().resolve()
        if args.legacy_dir
        else Path(args.project_dir).expanduser().resolve() / ".flash-writer"
    )
    sources = {
        "project_context": legacy_root / "project-context.md",
        "feedback_log": legacy_root / "feedback-log.md",
    }

    conflicts = []
    for key, source in sources.items():
        destination = paths[key]
        if source.exists() and destination.exists():
            if source.read_bytes() != destination.read_bytes():
                conflicts.append(
                    {"key": key, "source": str(source), "destination": str(destination)}
                )
    if conflicts:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "migration_conflict",
                    "message": "Destination files already exist with different content; nothing was moved.",
                    "conflicts": conflicts,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    write_if_missing(paths["writing_profile"], PROFILE_TEMPLATE)
    moved = []
    removed_duplicates = []
    for key, source in sources.items():
        destination = paths[key]
        if not source.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            source.unlink()
            removed_duplicates.append(key)
        else:
            shutil.move(str(source), str(destination))
            moved.append(key)

    legacy_removed = False
    if legacy_root.exists():
        try:
            legacy_root.rmdir()
            legacy_removed = True
        except OSError:
            legacy_removed = False

    created = initialize(paths)
    print(
        json.dumps(
            {
                "ok": True,
                "project_root": str(state["project_root"]),
                "project_key": state["project_key"],
                "legacy_root": str(legacy_root),
                "legacy_root_removed": legacy_removed,
                "moved": moved,
                "removed_identical_legacy_files": removed_duplicates,
                "created": created,
                "paths": {key: str(path) for key, path in paths.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Flash Writer personalization file locations and compact loading."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("init", "load", "migrate"):
        command = subparsers.add_parser(name)
        command.add_argument(
            "--project-dir",
            required=True,
            help="Directory containing the writing brief or the chosen writing project root.",
        )
        command.add_argument(
            "--global-dir",
            help="Override the global profile directory. Defaults to ~/.flash-writer.",
        )
        if name == "load":
            command.add_argument(
                "--max-chars",
                type=int,
                default=DEFAULT_MAX_CHARS,
                help="Maximum active characters loaded from each profile file.",
            )
            command.add_argument(
                "--article",
                help="Load only this article's '当前有效要求' section from feedback-log.md.",
            )
        if name == "migrate":
            command.add_argument(
                "--legacy-dir",
                help="Legacy project-local .flash-writer directory. Defaults to <project-dir>/.flash-writer.",
            )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init":
        return command_init(args)
    if args.command == "load":
        return command_load(args)
    if args.command == "migrate":
        return command_migrate(args)
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
