"""Validated JSON storage for task records."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

VALID_PRIORITIES = {"low", "normal", "high"}


def default_path() -> Path:
    override = os.environ.get("TASKCLI_DATA")
    return Path(override).expanduser() if override else Path.home() / ".taskcli" / "tasks.json"


def _validate(task: dict[str, Any]) -> None:
    if not isinstance(task.get("id"), int) or task["id"] < 1:
        raise ValueError("Task id must be a positive integer")
    if not isinstance(task.get("title"), str) or not task["title"].strip():
        raise ValueError("Task title cannot be empty")
    if task.get("priority") not in VALID_PRIORITIES:
        raise ValueError("Invalid priority")
    if not isinstance(task.get("done"), bool):
        raise ValueError("Task done flag must be boolean")
    due = task.get("due")
    if due is not None:
        date.fromisoformat(due)


def load_tasks(path: Path | None = None) -> list[dict[str, Any]]:
    file_path = path or default_path()
    if not file_path.exists():
        return []
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Task file contains invalid JSON: {file_path}") from exc
    if not isinstance(data, list):
        raise ValueError("Task file must contain a JSON array")
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each task must be a JSON object")
        _validate(item)
    ids = [item["id"] for item in data]
    if len(ids) != len(set(ids)):
        raise ValueError("Task file contains duplicate IDs")
    return data


def save_tasks(tasks: list[dict[str, Any]], path: Path | None = None) -> None:
    file_path = path or default_path()
    for task in tasks:
        _validate(task)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=file_path.name, suffix=".tmp", dir=file_path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(tasks, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, file_path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise