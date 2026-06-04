## What is this directory

This is the hook actions while the service/container start/stop.

### Important: hooks are sourced, not forked

Hooks are executed via `. filename` (source), not in a subshell. Therefore:

- **Do NOT use `exit 0` / `exit 1` in hooks** — it terminates the whole sparrow process.
- **Use `return 0` / `return 1` instead** — it exits only the sourced block, and sparrow continues.
- Do NOT use `set -e` inside hooks — it affects the parent shell.

### Available hooks

| Hook file | Timing |
|---|---|
| `before_start.sh` | Before container start (before pull/build and `docker compose up`) |
| `after_start.sh` | After container start |
| `before_stop.sh` | Before container stop |
| `after_stop.sh` | After container stop |
