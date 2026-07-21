import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import profile_store


class ProfileStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.global_dir = self.root / "state"
        self.project.mkdir()
        self.state = profile_store.resolve_state(
            str(self.project), str(self.global_dir)
        )
        self.paths = self.state["paths"]
        profile_store.initialize(self.paths)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def capture_json(self, function, args: argparse.Namespace) -> tuple[int, dict]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            return_code = function(args)
        return return_code, json.loads(output.getvalue())

    def load_args(self, article: str | None = None) -> argparse.Namespace:
        return argparse.Namespace(
            project_dir=str(self.project),
            global_dir=str(self.global_dir),
            max_chars=4000,
            article=article,
        )

    def migrate_args(self, legacy_dir: Path) -> argparse.Namespace:
        return argparse.Namespace(
            project_dir=str(self.project),
            global_dir=str(self.global_dir),
            legacy_dir=str(legacy_dir),
        )

    def test_initialize_is_idempotent(self) -> None:
        self.assertEqual(profile_store.initialize(self.paths), [])

    def test_project_key_isolated_by_resolved_path(self) -> None:
        other = self.root / "other" / "project"
        other.mkdir(parents=True)
        other_state = profile_store.resolve_state(str(other), str(self.global_dir))
        self.assertNotEqual(self.state["project_key"], other_state["project_key"])

    def test_load_reports_missing_article_as_not_found(self) -> None:
        return_code, payload = self.capture_json(
            profile_store.command_load, self.load_args("missing")
        )
        self.assertEqual(return_code, 0)
        current = payload["current_article_rules"]
        self.assertTrue(current["requested"])
        self.assertFalse(current["found"])
        self.assertFalse(current["loaded"])
        self.assertEqual(payload["token_policy"]["loaded_active_sections"], 2)

    def test_article_update_replaces_rules_and_appends_feedback(self) -> None:
        started, rules_count, feedback_appended = profile_store.update_article(
            self.paths["feedback_log"],
            "draft-one",
            ["段落要短", "不要虚构亲历"],
            "铺垫太长",
            "删除两段背景并提前核心观点",
        )
        self.assertTrue(started)
        self.assertEqual(rules_count, 2)
        self.assertTrue(feedback_appended)
        found, rules = profile_store.current_article_rules(
            self.paths["feedback_log"], "draft-one"
        )
        self.assertTrue(found)
        self.assertEqual(rules, "- 段落要短\n- 不要虚构亲历")
        log = self.paths["feedback_log"].read_text(encoding="utf-8")
        self.assertIn("- 用户反馈：铺垫太长", log)
        self.assertIn("- 已执行修改：删除两段背景并提前核心观点", log)

    def test_article_start_is_idempotent(self) -> None:
        self.assertTrue(profile_store.ensure_article(self.paths["feedback_log"], "a"))
        self.assertFalse(profile_store.ensure_article(self.paths["feedback_log"], "a"))
        text = self.paths["feedback_log"].read_text(encoding="utf-8")
        self.assertEqual(text.count("## a"), 1)

    def test_duplicate_article_sections_fail_closed(self) -> None:
        log = self.paths["feedback_log"]
        log.write_text(
            log.read_text(encoding="utf-8")
            + "\n## duplicate\n\n### 当前有效要求\n\n### 原始反馈\n"
            + "\n## duplicate\n\n### 当前有效要求\n\n### 原始反馈\n",
            encoding="utf-8",
        )
        with self.assertRaises(profile_store.StateFormatError):
            profile_store.current_article_rules(log, "duplicate")

    def test_article_update_requires_feedback_pair(self) -> None:
        args = argparse.Namespace(
            project_dir=str(self.project),
            global_dir=str(self.global_dir),
            article="draft",
            rule=None,
            feedback="需要更直接",
            applied_change=None,
        )
        with self.assertRaises(ValueError):
            profile_store.command_article_update(args)

    def test_malformed_active_markers_fail_closed(self) -> None:
        profile = self.paths["writing_profile"]
        profile.write_text(
            profile.read_text(encoding="utf-8").replace(
                profile_store.ACTIVE_END, ""
            ),
            encoding="utf-8",
        )
        with self.assertRaises(profile_store.StateFormatError):
            profile_store.active_content(profile)

    def test_compaction_omits_oversized_content(self) -> None:
        payload = profile_store.compact_content_payload(
            self.paths["writing_profile"], "12345", 4
        )
        self.assertTrue(payload["needs_compaction"])
        self.assertEqual(payload["content"], "")

    def test_migrate_rejects_source_equal_to_destination(self) -> None:
        context = self.paths["project_context"]
        original = context.read_text(encoding="utf-8") + "\n- keep me\n"
        context.write_text(original, encoding="utf-8")
        return_code, payload = self.capture_json(
            profile_store.command_migrate, self.migrate_args(context.parent)
        )
        self.assertEqual(return_code, 2)
        self.assertEqual(payload["error"], "migration_source_is_destination")
        self.assertEqual(context.read_text(encoding="utf-8"), original)

    def test_migrate_rejects_conflicting_destination_without_changes(self) -> None:
        legacy = self.root / "legacy"
        legacy.mkdir()
        source = legacy / "project-context.md"
        source.write_text("legacy", encoding="utf-8")
        destination = self.paths["project_context"]
        destination.write_text("destination", encoding="utf-8")
        return_code, payload = self.capture_json(
            profile_store.command_migrate, self.migrate_args(legacy)
        )
        self.assertEqual(return_code, 2)
        self.assertEqual(payload["error"], "migration_conflict")
        self.assertEqual(source.read_text(encoding="utf-8"), "legacy")
        self.assertEqual(destination.read_text(encoding="utf-8"), "destination")

    def test_max_chars_must_be_positive(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            profile_store.positive_int("0")


if __name__ == "__main__":
    unittest.main()
