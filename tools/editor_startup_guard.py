"""Fail-closed source check for WIP editor-triggered startup execution.

This checks repository files only. It cannot prove whether an editor previously
executed a task on a developer's machine or whether that machine is clean.
"""

from __future__ import annotations

import json
from pathlib import Path
import re


_UNICODE_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")


def _decode_unicode_escapes(source: str) -> str:
    """Reveal JSON Unicode-escaped marker strings, including simple nesting."""
    for _ in range(8):
        decoded = _UNICODE_ESCAPE.sub(lambda match: chr(int(match[1], 16)), source)
        if decoded == source:
            break
        source = decoded
    return source


def check_repository(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    editor = root / ".vscode"
    tasks_file = editor / "tasks.json"
    settings_file = editor / "settings.json"

    # Linux CI is case-sensitive, but VS Code can open these aliases on
    # case-insensitive Windows/macOS filesystems. Refuse ambiguous variants.
    for path in root.iterdir():
        if path.name.casefold() == ".vscode" and path.name != ".vscode":
            errors.append(f"{path.name}: case-variant editor directory forbidden")
    if editor.is_symlink():
        errors.append(".vscode: symlinked editor configuration forbidden")

    def read_json(path: Path) -> object | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(
                f"{path.relative_to(root)}: invalid/unreadable JSON "
                f"({type(exc).__name__})"
            )
            return None

    if tasks_file.is_symlink():
        errors.append(".vscode/tasks.json: symlink forbidden")
    elif tasks_file.exists():
        tasks = read_json(tasks_file)
        if not isinstance(tasks, dict) or tasks.get("tasks") != []:
            errors.append(".vscode/tasks.json: tracked tasks must be empty")

    if settings_file.is_symlink():
        errors.append(".vscode/settings.json: symlink forbidden")
    elif settings_file.exists():
        settings = read_json(settings_file)
        if not isinstance(settings, dict):
            errors.append(".vscode/settings.json: expected a JSON object")
        else:
            if settings.get("task.allowAutomaticTasks") != "off":
                errors.append(
                    ".vscode/settings.json: automatic tasks must explicitly be off"
                )
            if "tasks" in settings:
                errors.append(".vscode/settings.json: embedded tasks are forbidden")

    if editor.is_dir() and not editor.is_symlink():
        for path in editor.rglob("*"):
            if path.is_symlink():
                errors.append(f"{path.relative_to(root)}: editor symlink forbidden")
                continue
            if path.parent == editor and path.name.casefold() in {
                "tasks.json", "settings.json"
            } and path.name not in {"tasks.json", "settings.json"}:
                errors.append(
                    f"{path.relative_to(root)}: case-variant editor entrypoint forbidden"
                )
            if not path.is_file():
                continue
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append(f"{path.relative_to(root)}: unreadable editor source")
                continue
            decoded = _decode_unicode_escapes(source).casefold()
            if "folderopen" in decoded:
                errors.append(
                    f"{path.relative_to(root)}: folderOpen editor trigger forbidden"
                )
            if "fa-solid.lkf" in decoded:
                errors.append(
                    f"{path.relative_to(root)}: disguised loader reference forbidden"
                )

    # VS Code .code-workspace files can declare automatic tasks outside
    # .vscode/tasks.json. WIP has no such files; future additions require review.
    for path in root.rglob("*"):
        parts = path.relative_to(root).parts
        if ".git" in parts:
            continue
        # A symlink to an arbitrary directory can hide a second workspace
        # on hosts that follow it, even when the link target is absent here.
        if path.is_symlink():
            errors.append(f"{path.relative_to(root)}: source symlink requires review")
        # Every subdirectory can be opened as an independent VS Code root.
        # WIP does not currently need nested editor configuration; refuse it.
        if path != editor and path.name.casefold() == ".vscode":
            errors.append(f"{path.relative_to(root)}: nested editor configuration forbidden")
        if path.name.casefold().endswith(".code-workspace"):
            errors.append(
                f"{path.relative_to(root)}: workspace file requires security review"
            )
        if len(parts) >= 3 and tuple(part.casefold() for part in parts[:3]) == (
            "public", "fonts", "fa-solid.lkf"
        ):
            errors.append(
                f"{path.relative_to(root)}: disguised executable asset forbidden"
            )
    for path in (root / "public", root / "public" / "fonts"):
        if path.is_symlink():
            errors.append(f"{path.relative_to(root)}: symlinked asset path forbidden")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = check_repository(root)
    if errors:
        for error in errors:
            print(f"EDITOR_STARTUP_BLOCK: {error}")
        return 1
    print("EDITOR_STARTUP_PASS: no source editor auto-run or disguised loader")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
