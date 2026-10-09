# Task CLI

A small, dependency-free task manager for your terminal. Tasks are stored in a local JSON file, so your list survives restarts.

## Features

- Add, list, complete, edit, and delete tasks
- Priorities (`low`, `normal`, `high`) and optional due dates
- Filter by status, priority, and search text
- JSON persistence with atomic writes
- Friendly errors and automated tests

## Requirements

- Python 3.10+

## Quick start

```bash
python -m taskcli --help
python -m taskcli add "Build something useful" --priority high --due 2026-12-31
python -m taskcli list
python -m taskcli done 1
```

Run from the repository root. The default data file is `~/.taskcli/tasks.json`. Set `TASKCLI_DATA` to use a different path, especially for testing or portable setups.

## Commands

```text
python -m taskcli add TITLE [--priority low|normal|high] [--due YYYY-MM-DD]
python -m taskcli list [--all] [--priority PRIORITY] [--search TEXT]
python -m taskcli done ID
python -m taskcli edit ID [--title TITLE] [--priority PRIORITY] [--due YYYY-MM-DD]
python -m taskcli delete ID
python -m taskcli stats
```

## Development

```bash
python -m unittest discover -s tests -v
```

No third-party runtime dependencies are required. Released under the MIT License.