#!/usr/bin/env python3
"""Copy missing project references and reject unrelated same-name files."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = ("writing-template.md", "real-example.md", "screenshot-guide.md")
TEMPLATE_HEADINGS = (
    "原则与边界", "受众", "目标", "核心观点", "真实案例与事实",
    "写作思路", "写作风格", "格式偏好", "内容参考", "图片素材",
)


def is_flash_writer_file(name: str, path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeError:
        return False
    if name == "writing-template.md":
        headings = [
            line[3:].split("（", 1)[0].strip()
            for line in content.splitlines()
            if line.startswith("## ")
        ]
        expected = iter(TEMPLATE_HEADINGS)
        next_heading = next(expected, None)
        for heading in headings:
            if heading == next_heading:
                next_heading = next(expected, None)
        return next_heading is None
    if name == "real-example.md":
        return content.startswith("# 实际案例：") and "Flash Writer" in content
    return content.startswith("# 截图指南") and "写作思路" in content


def prepare(project_dir: Path) -> dict[str, object]:
    destination = project_dir.expanduser().resolve() / "references"
    conflicts = [
        str(destination / name)
        for name in FILES
        if (destination / name).exists() or (destination / name).is_symlink()
        if not is_flash_writer_file(name, destination / name)
    ]
    if conflicts:
        return {"ok": False, "error": "reference_conflict", "conflicts": conflicts}

    destination.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in FILES:
        target = destination / name
        status = "preserved" if target.exists() else "created"
        if status == "created":
            shutil.copyfile(ROOT / "references" / name, target)
        files[name] = {"path": str(target), "status": status}
    return {"ok": True, "files": files}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    result = prepare(Path(args.project_dir))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
