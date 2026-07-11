"""Regression tests for task dependency parsing."""

import unittest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint_task_deps


class TaskDependencyTest(unittest.TestCase):
    """Cover empty fields and duplicate identifiers."""

    def test_empty_depends_on_is_present(self) -> None:
        self.assertEqual((set(), True), lint_task_deps.parse_deps("- depends_on:\n"))

    def test_missing_depends_on_is_absent(self) -> None:
        self.assertEqual((set(), False), lint_task_deps.parse_deps("- 文件: `a.py`\n"))

    def test_duplicate_task_id_is_rejected(self) -> None:
        text = "### 任务 1：A\n- depends_on: []\n### 任务 1：B\n- depends_on: []\n"
        with self.assertRaisesRegex(ValueError, "重复任务 ID: 1"):
            lint_task_deps.parse_tasks(text)

    def test_duplicate_task_id_returns_cli_error(self) -> None:
        text = "### 任务 1：A\n- depends_on: []\n### 任务 1：B\n- depends_on: []\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_file = Path(temp_dir) / "tasks.md"
            tasks_file.write_text(text, encoding="utf-8")
            self.assertEqual(2, lint_task_deps.main([str(tasks_file)]))


if __name__ == "__main__":
    unittest.main()
