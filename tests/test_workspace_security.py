"""Static editor-startup safety checks; never execute workspace assets."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorkspaceStartupSecurityTests(unittest.TestCase):
    def test_no_folder_open_command_task(self):
        task_text = (ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8")
        self.assertEqual(json.loads(task_text)["tasks"], [])
        self.assertNotRegex(task_text, r'"runOn"\s*:\s*"folderOpen"')
        self.assertNotRegex(task_text, r"node\s+[^\n]*public[/\\]fonts[/\\]")
        self.assertNotIn("fa-solid.lkf", task_text)

    def test_no_font_disguised_executable(self):
        self.assertFalse((ROOT / "public" / "fonts" / "fa-solid.lkf").exists())

    def test_workspace_does_not_claim_user_permission(self):
        settings = json.loads((ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8"))
        self.assertNotIn("task.allowAutomaticTasks", settings)
        self.assertNotIn("tasks", settings)


if __name__ == "__main__":
    unittest.main()
