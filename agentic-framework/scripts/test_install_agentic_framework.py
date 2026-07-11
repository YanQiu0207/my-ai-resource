"""Regression tests for framework installation."""

import tempfile
import unittest
from pathlib import Path
import sys
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install_agentic_framework as installer


class InstallTest(unittest.TestCase):
    """Verify preflight conflict checks and failure rollback."""

    def _make_source(self, root: Path) -> Path:
        source = root / "source"
        for name in installer.CONTENT_DIRS:
            directory = source / name
            directory.mkdir(parents=True)
            (directory / "new.txt").write_text(name, encoding="utf-8")
        return source

    def test_later_copy_failure_restores_all_target_trees(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = self._make_source(root)
            target = root / "target"
            for client in installer.CLIENT_DIRS:
                for content in installer.CONTENT_DIRS:
                    directory = target / client / content
                    directory.mkdir(parents=True)
                    (directory / "old.txt").write_text("old", encoding="utf-8")

            real_copy = installer.copy_tree
            calls = 0

            def failing_copy(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("simulated failure")
                return real_copy(*args, **kwargs)

            with mock.patch.object(installer, "copy_tree", side_effect=failing_copy):
                with self.assertRaisesRegex(OSError, "simulated failure"):
                    installer.install(source, target, False, True)

            for client in installer.CLIENT_DIRS:
                for content in installer.CONTENT_DIRS:
                    directory = target / client / content
                    self.assertEqual("old", (directory / "old.txt").read_text())
                    self.assertFalse((directory / "new.txt").exists())

    def test_directory_symlink_node_and_contents_are_restored(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = self._make_source(root)
            target = root / "target"
            linked_directory = root / "linked-skills"
            linked_directory.mkdir()
            (linked_directory / "old.txt").write_text("old", encoding="utf-8")
            link = target / ".codex" / "skills"
            link.parent.mkdir(parents=True)
            try:
                link.symlink_to(linked_directory, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlink is unavailable: {error}")

            real_copy = installer.copy_tree
            calls = 0

            def failing_copy(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated failure")
                return real_copy(*args, **kwargs)

            with mock.patch.object(installer, "copy_tree", side_effect=failing_copy):
                with self.assertRaisesRegex(OSError, "simulated failure"):
                    installer.install(source, target, False, True)

            self.assertTrue(link.is_symlink())
            self.assertEqual("old", (link / "old.txt").read_text(encoding="utf-8"))
            self.assertFalse((linked_directory / "new.txt").exists())

    def test_rollback_continues_and_preserves_copy_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = self._make_source(root)
            target = root / "target"
            for content in installer.CONTENT_DIRS:
                directory = target / ".codex" / content
                directory.mkdir(parents=True)
                (directory / "old.txt").write_text("old", encoding="utf-8")

            real_copy = installer.copy_tree
            copy_calls = 0

            def failing_copy(*args, **kwargs):
                nonlocal copy_calls
                copy_calls += 1
                if copy_calls == 3:
                    raise OSError("original copy failure")
                return real_copy(*args, **kwargs)

            real_remove = installer._remove_path
            remove_calls = 0

            def failing_remove(path):
                nonlocal remove_calls
                remove_calls += 1
                if remove_calls == 1:
                    raise OSError("rollback failure")
                return real_remove(path)

            with mock.patch.object(installer, "copy_tree", side_effect=failing_copy), \
                    mock.patch.object(installer, "_remove_path", side_effect=failing_remove):
                with self.assertRaisesRegex(OSError, "original copy failure") as raised:
                    installer.install(source, target, False, True)

            self.assertEqual("old", (
                target / ".codex" / "agents" / "old.txt"
            ).read_text(encoding="utf-8"))
            self.assertFalse((target / ".codex" / "agents" / "new.txt").exists())
            if hasattr(raised.exception, "__notes__"):
                self.assertIn("rollback failure", "\n".join(raised.exception.__notes__))


if __name__ == "__main__":
    unittest.main()
