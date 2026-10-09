"""Argument parser and terminal output."""
from __future__ import annotations
import argparse
import sys
from .service import add_task, complete_task, delete_task, list_tasks, stats, update_task
from .storage import VALID_PRIORITIES, default_path


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="taskcli", description="Manage tasks from your terminal")
    root.add_argument("--data", help="JSON data file (overrides TASKCLI_DATA)")
    commands = root.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Create a task")
    add.add_argument("title")
    add.add_argument("--priority", choices=sorted(VALID_PRIORITIES), default="normal")
    add.add_argument("--due", help="Due date in YYYY-MM-DD format")
    listing = commands.add_parser("list", help="List tasks")
    listing.add_argument("--all", action="store_true", help="Include completed tasks")
    listing.add_argument("--priority", choices=sorted(VALID_PRIORITIES))
    listing.add_argument("--search")
    done = commands.add_parser("done", help="Mark a task complete")
    done.add_argument("id", type=int)
    edit = commands.add_parser("edit", help="Edit a task")
    edit.add_argument("id", type=int)
    edit.add_argument("--title")
    edit.add_argument("--priority", choices=sorted(VALID_PRIORITIES))
    edit.add_argument("--due", help="YYYY-MM-DD, or an empty value to clear")
    delete = commands.add_parser("delete", help="Delete a task")
    delete.add_argument("id", type=int)
    commands.add_parser("stats", help="Show task counts")
    return root


def _render(tasks):
    if not tasks:
        print("No tasks found.")
        return
    print(f"{'ID':>4}  {'STATUS':<5} {'PRIORITY':<6} {'DUE':<10}  TITLE")
    print("-" * 64)
    for task in tasks:
        status = "done" if task["done"] else "open"
        print(f"{task['id']:>4}  {status:<5} {task['priority']:<6} {(task['due'] or '-'): <10}  {task['title']}")


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    path = args.data or default_path()
    try:
        if args.command == "add":
            task = add_task(args.title, args.priority, args.due, path)
            print(f"Created task {task['id']}: {task['title']}")
        elif args.command == "list":
            _render(list_tasks(path, args.all, args.priority, args.search))
        elif args.command == "done":
            task = complete_task(args.id, path)
            print(f"Completed task {task['id']}: {task['title']}")
        elif args.command == "edit":
            changes = {key: getattr(args, key) for key in ("title", "priority", "due") if getattr(args, key) is not None}
            if not changes:
                raise ValueError("Provide at least one field to edit")
            task = update_task(args.id, path, **changes)
            print(f"Updated task {task['id']}: {task['title']}")
        elif args.command == "delete":
            task = delete_task(args.id, path)
            print(f"Deleted task {task['id']}: {task['title']}")
        elif args.command == "stats":
            counts = stats(path)
            print(f"Total: {counts['total']} | Open: {counts['open']} | Done: {counts['done']}")
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())