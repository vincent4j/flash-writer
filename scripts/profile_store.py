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


class StateFormatError(ValueError):
    def __init__(self, path: Path, message: str) -> None:
        super().__init__(message)
        self.path = path


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def atomic_write_text(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.flash-writer-tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


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
    start_count = text.count(ACTIVE_START)
    end_count = text.count(ACTIVE_END)
    if start_count != 1 or end_count != 1:
        raise StateFormatError(
            path,
            "Expected exactly one active section marker pair; full file was not loaded.",
        )
    start = text.index(ACTIVE_START) + len(ACTIVE_START)
    end = text.index(ACTIVE_END)
    if start > end:
        raise StateFormatError(
            path,
            "Active section end marker appears before the start marker; full file was not loaded.",
        )
    return text[start:end].strip()


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


def normalize_article(article: str) -> str:
    normalized = article.strip()
    if not normalized or "\n" in normalized or "\r" in normalized:
        raise ValueError("article must be a non-empty single-line identifier")
    return normalized


def article_section_bounds(
    path: Path, lines: list[str], article: str
) -> tuple[int, int] | None:
    heading = f"## {normalize_article(article)}"
    matches = [index for index, line in enumerate(lines) if line.strip() == heading]
    if len(matches) > 1:
        raise StateFormatError(path, f"Duplicate article section: {article}")
    if not matches:
        return None
    start = matches[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return start, end


def article_subsection_bounds(
    path: Path,
    lines: list[str],
    section_start: int,
    section_end: int,
    heading: str,
) -> tuple[int, int]:
    matches = [
        index
        for index in range(section_start + 1, section_end)
        if lines[index].strip() == heading
    ]
    if len(matches) != 1:
        raise StateFormatError(
            path,
            f"Expected exactly one '{heading}' subsection in the article section.",
        )
    start = matches[0]
    end = section_end
    for index in range(start + 1, section_end):
        if lines[index].startswith("### "):
            end = index
            break
    return start, end


def current_article_rules(path: Path, article: str | None) -> tuple[bool, str]:
    if not article:
        return False, ""
    lines = path.read_text(encoding="utf-8").splitlines()
    section = article_section_bounds(path, lines, article)
    if section is None:
        return False, ""
    rules_start, rules_end = article_subsection_bounds(
        path, lines, section[0], section[1], "### 当前有效要求"
    )
    return True, "\n".join(lines[rules_start + 1 : rules_end]).strip()


def ensure_article(path: Path, article: str) -> bool:
    normalized = normalize_article(article)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if article_section_bounds(path, lines, normalized) is not None:
        return False
    suffix = "" if text.endswith("\n\n") else "\n" if text.endswith("\n") else "\n\n"
    addition = (
        f"{suffix}## {normalized}\n\n"
        "### 当前有效要求\n\n"
        "### 原始反馈\n"
    )
    atomic_write_text(path, text + addition)
    return True


def update_article(
    path: Path,
    article: str,
    rules: list[str] | None,
    feedback: str | None,
    applied_change: str | None,
) -> tuple[bool, int, bool]:
    started = ensure_article(path, article)
    lines = path.read_text(encoding="utf-8").splitlines()
    section = article_section_bounds(path, lines, article)
    if section is None:
        raise StateFormatError(path, f"Article section was not created: {article}")

    normalized_rules: list[str] | None = None
    if rules is not None:
        rules_start, rules_end = article_subsection_bounds(
            path, lines, section[0], section[1], "### 当前有效要求"
        )
        normalized_rules = [rule.strip().removeprefix("- ").strip() for rule in rules]
        normalized_rules = [rule for rule in normalized_rules if rule]
        replacement = [lines[rules_start], ""]
        replacement.extend(f"- {rule}" for rule in normalized_rules)
        replacement.append("")
        lines[rules_start:rules_end] = replacement

    feedback_appended = feedback is not None
    if feedback_appended:
        section = article_section_bounds(path, lines, article)
        if section is None:
            raise StateFormatError(path, f"Article section disappeared: {article}")
        _, feedback_end = article_subsection_bounds(
            path, lines, section[0], section[1], "### 原始反馈"
        )
        entry = [
            "",
            f"- 用户反馈：{feedback.strip()}",
            f"- 已执行修改：{applied_change.strip()}",
        ]
        lines[feedback_end:feedback_end] = entry

    atomic_write_text(path, "\n".join(lines).rstrip() + "\n")
    return started, len(normalized_rules or []), feedback_appended


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
    article_found, current_rules = current_article_rules(
        paths["feedback_log"], args.article
    )
    current = compact_content_payload(
        paths["feedback_log"], current_rules, args.max_chars
    )
    current["article"] = args.article
    current["requested"] = bool(args.article)
    current["found"] = article_found
    current["loaded"] = article_found
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
                    "loaded_active_sections": 3 if article_found else 2,
                    "feedback_history_loaded": False,
                    "max_chars_per_active_file": args.max_chars,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_article_start(args: argparse.Namespace) -> int:
    state = resolve_state(args.project_dir, args.global_dir)
    paths = state["paths"]
    initialize(paths)
    created = ensure_article(paths["feedback_log"], args.article)
    print(
        json.dumps(
            {
                "ok": True,
                "article": normalize_article(args.article),
                "created": created,
                "feedback_log": str(paths["feedback_log"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_article_update(args: argparse.Namespace) -> int:
    if (args.feedback is None) != (args.applied_change is None):
        raise ValueError("feedback and applied-change must be provided together")
    if args.rule is None and args.feedback is None:
        raise ValueError("provide at least one rule or a feedback/applied-change pair")
    state = resolve_state(args.project_dir, args.global_dir)
    paths = state["paths"]
    initialize(paths)
    started, rules_count, feedback_appended = update_article(
        paths["feedback_log"],
        args.article,
        args.rule,
        args.feedback,
        args.applied_change,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "article": normalize_article(args.article),
                "started": started,
                "rules_replaced": args.rule is not None,
                "rules_count": rules_count,
                "feedback_appended": feedback_appended,
                "feedback_log": str(paths["feedback_log"]),
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

    same_paths = []
    for key, source in sources.items():
        destination = paths[key]
        if source == destination or (
            source.exists()
            and destination.exists()
            and source.samefile(destination)
        ):
            same_paths.append(
                {"key": key, "source": str(source), "destination": str(destination)}
            )
    if same_paths:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "migration_source_is_destination",
                    "message": "Legacy source resolves to the current destination; nothing was moved or deleted.",
                    "paths": same_paths,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

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


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Flash Writer personalization file locations and compact loading."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("init", "load", "article-start", "article-update", "migrate"):
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
                type=positive_int,
                default=DEFAULT_MAX_CHARS,
                help="Maximum active characters loaded from each profile file.",
            )
            command.add_argument(
                "--article",
                help="Load only this article's '当前有效要求' section from feedback-log.md.",
            )
        if name in ("article-start", "article-update"):
            command.add_argument(
                "--article",
                required=True,
                help="Stable single-line article identifier.",
            )
        if name == "article-update":
            command.add_argument(
                "--rule",
                action="append",
                help="Complete active rule. Repeat to replace the article's active rules.",
            )
            command.add_argument(
                "--feedback",
                help="User feedback to append to the raw feedback history.",
            )
            command.add_argument(
                "--applied-change",
                help="Concrete change made in response to the feedback.",
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
    try:
        if args.command == "init":
            return command_init(args)
        if args.command == "load":
            return command_load(args)
        if args.command == "article-start":
            return command_article_start(args)
        if args.command == "article-update":
            return command_article_update(args)
        if args.command == "migrate":
            return command_migrate(args)
    except StateFormatError as error:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "state_format_error",
                    "message": str(error),
                    "path": str(error.path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2
    except ValueError as error:
        print(
            json.dumps(
                {"ok": False, "error": "invalid_argument", "message": str(error)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
