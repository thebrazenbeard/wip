"""Fail-closed regression guard for concealed editor workspace-open execution.

Historical suspicious blobs remain recoverable in Git history. The active
working tree must not configure a hidden task or permission to auto-run one.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from tools.editor_startup_guard import check_repository

ROOT = Path(__file__).resolve().parents[1]
AUTORUN = re.compile(r'"runOn"\s*:\s*"folderOpen"')


class EditorStartupSafetyTests(unittest.TestCase):
    def test_static_source_guard_accepts_current_repository(self):
        self.assertEqual(check_repository(ROOT), [])

    def test_rejects_nonempty_tasks_even_when_no_autorun_declared(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            editor = root / ".vscode"
            editor.mkdir()
            (editor / "tasks.json").write_text(json.dumps({
                "version": "2.0.0", "tasks": [{"label": "manual", "command": "echo safe"}],
            }), encoding="utf-8")
            self.assertIn("tracked tasks must be empty", " ".join(check_repository(root)))

    def test_rejects_hidden_embedded_settings_tasks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            editor = root / ".vscode"
            editor.mkdir()
            (editor / "settings.json").write_text(json.dumps({
                "task.allowAutomaticTasks": "off", "tasks": {"tasks": []},
            }), encoding="utf-8")
            self.assertIn("embedded tasks are forbidden", " ".join(check_repository(root)))

    def test_rejects_unicode_escaped_folderopen_marker_in_nested_editor_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            editor = root / ".vscode" / "nested"
            editor.mkdir(parents=True)
            (editor / "tasks.json").write_text(
                '{"runOptions":{"runOn":"\\u0066olderOpen"}}', encoding="utf-8"
            )
            self.assertIn("folderOpen editor trigger", " ".join(check_repository(root)))

    def test_rejects_workspace_file_outside_repository_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "configs"
            nested.mkdir()
            (nested / "safe.code-workspace").write_text(
                '{"folders":[{"path":".."}]}', encoding="utf-8"
            )
            self.assertIn("workspace file requires", " ".join(check_repository(root)))

    def test_invalid_task_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            editor = root / ".vscode"
            editor.mkdir()
            (editor / "tasks.json").write_text("{invalid-json", encoding="utf-8")
            self.assertIn("invalid/unreadable JSON", " ".join(check_repository(root)))

    def test_dangling_editor_task_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            editor = root / ".vscode"
            editor.mkdir()
            (editor / "tasks.json").symlink_to(root / "outside-tasks.json")
            self.assertTrue(check_repository(root))

    def test_dangling_editor_directory_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".vscode").symlink_to(root / "outside-editor-dir", target_is_directory=True)
            self.assertTrue(check_repository(root))

    def test_dangling_workspace_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "outside.code-workspace").symlink_to(root / "host-workspace.json")
            self.assertTrue(check_repository(root))

    def test_case_variant_editor_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            editor = root / ".VSCode"
            editor.mkdir()
            (editor / "tasks.json").write_text(json.dumps({
                "tasks": [{"runOptions": {"runOn": "folderOpen"}}],
            }), encoding="utf-8")
            self.assertTrue(check_repository(root))

    def test_case_variant_tasks_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            editor = root / ".vscode"
            editor.mkdir()
            (editor / "Tasks.json").write_text(json.dumps({
                "tasks": [{"label": "unreviewed", "command": "echo testing"}],
            }), encoding="utf-8")
            self.assertTrue(check_repository(root))

    def test_case_variant_workspace_extension_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "startup.CODE-WORKSPACE").write_text("{}", encoding="utf-8")
            self.assertTrue(check_repository(root))

    def test_case_variant_disguised_loader_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fonts = root / "public" / "fonts"
            fonts.mkdir(parents=True)
            (fonts / "Fa-Solid.lkf").write_text("inert fixture", encoding="utf-8")
            self.assertIn("disguised executable asset", " ".join(check_repository(root)))

    def test_nested_folder_editor_task_cannot_bypass_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "nested" / ".vscode"
            nested.mkdir(parents=True)
            (nested / "tasks.json").write_text(json.dumps({
                "tasks": [{"runOptions": {"runOn": "folderOpen"}}],
            }), encoding="utf-8")
            self.assertIn("nested editor configuration forbidden", " ".join(check_repository(root)))

    def test_arbitrary_live_and_dangling_ancestor_symlinks_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repo"
            root.mkdir()
            nested = base / "external" / ".vscode"
            nested.mkdir(parents=True)
            (nested / "tasks.json").write_text("{}", encoding="utf-8")
            (root / "nested").symlink_to(base / "external", target_is_directory=True)
            (root / "orphan").symlink_to("missing", target_is_directory=True)
            errors = " ".join(check_repository(root))
            self.assertIn("nested: source symlink requires review", errors)
            self.assertIn("orphan: source symlink requires review", errors)

    def test_no_automatic_workspace_open_tasks(self):
        tasks_path = ROOT / ".vscode" / "tasks.json"
        if not tasks_path.exists():
            return
        document = json.loads(tasks_path.read_text(encoding="utf-8"))
        for task in document.get("tasks", []):
            with self.subTest(task=task.get("label")):
                self.assertNotEqual(
                    task.get("runOptions", {}).get("runOn"),
                    "folderOpen",
                    "Opening a repository must not launch code automatically",
                )

    def test_automatic_task_permission_explicitly_off(self):
        settings_path = ROOT / ".vscode" / "settings.json"
        if not settings_path.exists():
            return
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertEqual(settings.get("task.allowAutomaticTasks"), "off")
        self.assertNotIn("tasks", settings)

    def test_no_folder_open_in_any_editor_configuration(self):
        paths = list((ROOT / ".vscode").glob("*.json"))
        paths.extend(ROOT.glob("*.code-workspace"))
        for path in paths:
            with self.subTest(path=path.name):
                self.assertIsNone(
                    AUTORUN.search(path.read_text(encoding="utf-8")),
                    "Editor configuration must not declare a folderOpen task",
                )

    def test_disguised_node_payload_is_absent(self):
        self.assertFalse(
            (ROOT / "public" / "fonts" / "fa-solid.lkf").exists(),
            "An executable disguised as a font must not be restored",
        )


if __name__ == "__main__":
    unittest.main()
