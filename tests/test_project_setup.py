import tempfile
import unittest
from pathlib import Path

from scripts import project_setup


class ProjectSetupTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_creates_missing_files_and_preserves_valid_template(self) -> None:
        first = project_setup.prepare(self.project)
        self.assertTrue(first["ok"])
        template = self.project / "references" / "writing-template.md"
        template.write_text(
            template.read_text(encoding="utf-8") + "\n## 自定义补充\n我的内容\n",
            encoding="utf-8",
        )
        second = project_setup.prepare(self.project)
        self.assertTrue(second["ok"])
        self.assertEqual(second["files"]["writing-template.md"]["status"], "preserved")
        self.assertIn("我的内容", template.read_text(encoding="utf-8"))

    def test_conflict_stops_before_copying_any_file(self) -> None:
        references = self.project / "references"
        references.mkdir()
        collision = references / "writing-template.md"
        collision.write_text("# Another template\n", encoding="utf-8")
        result = project_setup.prepare(self.project)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "reference_conflict")
        self.assertEqual(collision.read_text(encoding="utf-8"), "# Another template\n")
        self.assertFalse((references / "real-example.md").exists())


if __name__ == "__main__":
    unittest.main()
