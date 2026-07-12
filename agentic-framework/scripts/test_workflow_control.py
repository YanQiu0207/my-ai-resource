"""Tests for deterministic workflow control."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "skills"
        / "workflow-code-generation"
        / "scripts"
    ),
)

import lint_task_deps
import workflow_control


def tasks_text(
    states: dict[int, str],
    dependencies: dict[int, list[int]],
    attempts: int = 0,
) -> str:
    """Build the minimum task document used by control-flow tests."""
    sections = []
    for task_id in states:
        deps = ", ".join(
            f"Task {dependency}" for dependency in dependencies[task_id]
        )
        sections.append(
            f"### 任务 {task_id}：测试\n\n"
            f"- 状态：{states[task_id]}\n"
            f"- attempts：{attempts}\n"
            f"- depends_on：[{deps}]\n"
        )
    return "\n".join(sections)


class WorkflowControlTest(unittest.TestCase):
    """Cover deterministic scheduling, transitions, persistence, and recovery."""

    def test_build_waves_is_stable(self) -> None:
        text = tasks_text(
            {3: "未开始", 1: "未开始", 2: "未开始"},
            {3: [1, 2], 1: [], 2: []},
        )
        tasks = lint_task_deps.parse_tasks(text)
        self.assertEqual([[1, 2], [3]], workflow_control.build_waves(tasks))

    def test_same_wave_failure_is_isolated_end_to_end(self) -> None:
        text = tasks_text(
            {1: "进行中", 2: "进行中"}, {1: [], 2: []}, attempts=2
        )
        tasks = lint_task_deps.parse_tasks(text)
        failed = workflow_control.apply_event(tasks, 1, "failure")
        passed = workflow_control.apply_event(tasks, 2, "quality_passed")
        text = workflow_control.update_task_state(text, failed)
        text = workflow_control.update_task_state(text, passed)
        tasks = lint_task_deps.parse_tasks(text)
        merged = workflow_control.apply_event(tasks, 2, "merge_success")
        text = workflow_control.update_task_state(text, merged)
        states = workflow_control._states(lint_task_deps.parse_tasks(text))
        self.assertEqual({1: "需人工", 2: "完成"}, states)

    def test_quality_pass_does_not_complete_before_merge(self) -> None:
        text = tasks_text({1: "进行中"}, {1: []})
        tasks = lint_task_deps.parse_tasks(text)
        quality = workflow_control.apply_event(tasks, 1, "quality_passed")
        self.assertEqual(("进行中", "merge"), (quality.state, quality.action))
        text = workflow_control.update_task_state(text, quality)
        merged = workflow_control.apply_event(
            lint_task_deps.parse_tasks(text), 1, "merge_success"
        )
        self.assertEqual("完成", merged.state)

    def test_merge_requires_persisted_quality_passed_stage(self) -> None:
        running = lint_task_deps.parse_tasks(tasks_text({1: "进行中"}, {1: []}))
        with self.assertRaisesRegex(ValueError, "不允许"):
            workflow_control.apply_event(running, 1, "merge_success")

    def test_failure_recursively_blocks_descendants(self) -> None:
        text = tasks_text(
            {1: "需人工", 2: "未开始", 3: "未开始"},
            {1: [], 2: [1], 3: [2]},
        )
        decisions = workflow_control.propagate_blocked(
            lint_task_deps.parse_tasks(text)
        )
        self.assertEqual([2, 3], [decision.task_id for decision in decisions])

    def test_retry_count_persists_and_survives_reload(self) -> None:
        text = tasks_text({1: "进行中"}, {1: []})
        for expected in (1, 2, 3):
            tasks = lint_task_deps.parse_tasks(text)
            decision = workflow_control.apply_event(tasks, 1, "failure")
            text = workflow_control.update_task_state(text, decision)
            self.assertEqual(
                expected,
                workflow_control._attempts(lint_task_deps.parse_tasks(text)[1]),
            )
        self.assertEqual("需人工", decision.state)

    def test_recovery_skips_completed_and_reconciles_merged(self) -> None:
        text = tasks_text(
            {1: "完成", 2: "进行中", 3: "阻塞"},
            {1: [], 2: [1], 3: [2]},
        )
        actions = workflow_control.plan_recovery(
            lint_task_deps.parse_tasks(text), {2}
        )
        self.assertEqual(
            ["skip", "complete", "unblock"], [item.action for item in actions]
        )

    def test_self_dependency_and_missing_field_fail_closed(self) -> None:
        self_dep = lint_task_deps.parse_tasks(
            tasks_text({1: "未开始"}, {1: [1]})
        )
        with self.assertRaisesRegex(ValueError, "循环"):
            workflow_control.build_waves(self_dep)
        missing = lint_task_deps.parse_tasks(
            "### 任务 1：测试\n- 状态：未开始\n"
        )
        with self.assertRaisesRegex(ValueError, "缺少 depends_on"):
            workflow_control.build_waves(missing)
        with self.assertRaisesRegex(ValueError, "缺少 depends_on"):
            workflow_control.apply_event(missing, 1, "start")

    def test_illegal_transition_and_reason_injection_fail(self) -> None:
        completed = lint_task_deps.parse_tasks(tasks_text({1: "完成"}, {1: []}))
        with self.assertRaisesRegex(ValueError, "不允许"):
            workflow_control.apply_event(completed, 1, "merge_success")
        running = lint_task_deps.parse_tasks(tasks_text({1: "进行中"}, {1: []}))
        with self.assertRaisesRegex(ValueError, "换行"):
            workflow_control.apply_event(
                running, 1, "failure", "x\n- 状态：完成"
            )

    def test_unblock_requires_completed_dependencies(self) -> None:
        ready = lint_task_deps.parse_tasks(
            tasks_text({1: "完成", 2: "阻塞"}, {1: [], 2: [1]})
        )
        self.assertEqual(
            "未开始", workflow_control.apply_event(ready, 2, "unblock").state
        )
        waiting = lint_task_deps.parse_tasks(
            tasks_text({1: "需人工", 2: "阻塞"}, {1: [], 2: [1]})
        )
        with self.assertRaisesRegex(ValueError, "尚未全部完成"):
            workflow_control.apply_event(waiting, 2, "unblock")

    def test_start_requires_completed_dependencies(self) -> None:
        tasks = lint_task_deps.parse_tasks(
            tasks_text({1: "进行中", 2: "未开始"}, {1: [], 2: [1]})
        )
        with self.assertRaisesRegex(ValueError, "尚未全部完成"):
            workflow_control.apply_event(tasks, 2, "start")

    def test_cli_uses_atomic_writer_and_persists_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tasks.md"
            path.write_text(
                tasks_text({1: "进行中"}, {1: []}), encoding="utf-8"
            )
            result = workflow_control.main(
                [str(path), "event", "1", "failure", "--write"]
            )
            self.assertEqual(0, result)
            persisted = path.read_text(encoding="utf-8")
            self.assertIn("- attempts：1", persisted)
            self.assertEqual([], list(path.parent.glob(".tasks.md.*")))

    def test_atomic_write_preserves_permissions_and_crlf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tasks.md"
            original = tasks_text({1: "进行中"}, {1: []}).replace("\n", "\r\n")
            path.write_bytes(original.encode("utf-8"))
            path.chmod(0o640)
            original_mode = path.stat().st_mode & 0o777
            workflow_control.main(
                [str(path), "event", "1", "failure", "--write"]
            )
            data = path.read_bytes()
            self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
            self.assertEqual(original_mode, path.stat().st_mode & 0o777)


if __name__ == "__main__":
    unittest.main()
