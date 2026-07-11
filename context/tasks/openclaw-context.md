# Task: openclaw-context

- Task ID: openclaw-context
- Status: active
- Owner/user intent: Hòa Đại ka wants OpenClaw via Telegram to avoid getting slow/confused from long context, but also avoid losing task state when using fresh sessions. He may have many sessions and many unrelated tasks, so one global CURRENT_CONTEXT.md is not enough.
- Project/folder: `C:\Users\HoaD-CVDT\.openclaw\workspace`
- Scope / boundaries: solve context hygiene and task separation; do not mix unrelated Telegram tasks; keep files small.
- Important files:
  - `AGENTS.md`
  - `context/TASKS.md`
  - `context/TASK_TEMPLATE.md`
  - `context/tasks/openclaw-context.md`
  - legacy/simple handoff: `CURRENT_CONTEXT.md`
- Current facts:
  - `CURRENT_CONTEXT.md` was added first, but user correctly rejected it as too global for many concurrent tasks.
  - Better model: task registry + one context file per distinct task.
- Done:
  - Added task registry and template under `context/`.
  - Created this task-specific context file.
- Next:
  - Update `AGENTS.md` to prefer task-specific context files over global `CURRENT_CONTEXT.md`.
  - Explain to Hòa Đại ka how to use task IDs naturally in Telegram.
- Commands already run:
  - Created `CURRENT_CONTEXT.md` and committed `92aa1339`.
- Tests/checks:
  - Pending git commit for the new task registry.
- Risks / do-not-do:
  - Do not rely on a single global context file for multiple tasks.
  - Do not load all task files every time; read registry, then only the relevant task file.
- Last updated: 2026-07-11

## Handoff summary

Use `context/TASKS.md` as the index. For each separate job, create/read exactly one file in `context/tasks/<task-id>.md`. If user does not give task ID, infer from recent request if obvious; otherwise ask a short disambiguation question.
