"""Task operations independent of the command-line interface."""
from __future__ import annotations
from datetime import date
from typing import Any
from .storage import VALID_PRIORITIES, load_tasks, save_tasks


def _next_id(tasks: list[dict[str, Any]]) -> int:
    return max((task["id"] for task in tasks), default=0) + 1


def add_task(title: str, priority: str = "normal", due: str | None = None, path=None) -> dict[str, Any]:
    title = title.strip()
    if not title:
        raise ValueError("Title cannot be empty")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}")
    if due:
        date.fromisoformat(due)
    tasks = load_tasks(path)
    task = {"id": _next_id(tasks), "title": title, "priority": priority, "due": due, "done": False}
    tasks.append(task)
    save_tasks(tasks, path)
    return task


def list_tasks(path=None, include_done: bool = False, priority: str | None = None, search: str | None = None):
    tasks = load_tasks(path)
    if not include_done:
        tasks = [task for task in tasks if not task["done"]]
    if priority:
        tasks = [task for task in tasks if task["priority"] == priority]
    if search:
        needle = search.casefold()
        tasks = [task for task in tasks if needle in task["title"].casefold()]
    return sorted(tasks, key=lambda task: (task["done"], {"high": 0, "normal": 1, "low": 2}[task["priority"]], task["id"]))


def update_task(task_id: int, path=None, **changes):
    allowed = {"title", "priority", "due"}
    if changes.keys() - allowed:
        raise ValueError("Unsupported task field")
    tasks = load_tasks(path)
    for task in tasks:
        if task["id"] == task_id:
            if "title" in changes:
                title = changes["title"].strip()
                if not title:
                    raise ValueError("Title cannot be empty")
                task["title"] = title
            if "priority" in changes and changes["priority"] is not None:
                if changes["priority"] not in VALID_PRIORITIES:
                    raise ValueError("Invalid priority")
                task["priority"] = changes["priority"]
            if "due" in changes and changes["due"] is not None:
                if changes["due"]:
                    date.fromisoformat(changes["due"])
                task["due"] = changes["due"] or None
            save_tasks(tasks, path)
            return task
    raise KeyError(f"No task with ID {task_id}")


def complete_task(task_id: int, path=None):
    tasks = load_tasks(path)
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(tasks, path)
            return task
    raise KeyError(f"No task with ID {task_id}")


def delete_task(task_id: int, path=None):
    tasks = load_tasks(path)
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            removed = tasks.pop(index)
            save_tasks(tasks, path)
            return removed
    raise KeyError(f"No task with ID {task_id}")


def stats(path=None):
    tasks = load_tasks(path)
    done = sum(task["done"] for task in tasks)
    return {"total": len(tasks), "done": done, "open": len(tasks) - done}