# TASKS.md - Active Task Registry

Purpose: keep multiple Telegram/OpenClaw tasks separate so sessions do not mix context.

Rules:

- Each distinct job gets its own task file in `context/tasks/`.
- Use stable task IDs, e.g. `bds-legal-fix`, `stock-cache-health`, `ui-redesign-lh`, `openclaw-context`.
- Never merge unrelated tasks into one context file.
- When Hòa Đại ka asks to continue a task, identify or ask for the task ID, then read only that task file and relevant project files.
- When starting a new task, create a new file from `context/TASK_TEMPLATE.md` and add it to this registry.
- When pausing/finishing, update that task file and mark status here.
- Keep each task file concise. Archive details in project docs/logs, not in this registry.

## Active Tasks

| Task ID | Status | Short name | Context file | Last updated |
|---|---|---|---|---|
| openclaw-context | active | OpenClaw context/session hygiene | `context/tasks/openclaw-context.md` | 2026-07-11 |

## Status values

- active
- paused
- blocked
- done
- archived
