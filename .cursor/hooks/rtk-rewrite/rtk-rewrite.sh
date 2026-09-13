#!/usr/bin/env bash
# Fail-open wrapper around `rtk hook cursor` / `rtk hook claude`.
# Cursor native beforeShellExecution sends .command; rtk hook cursor reads
# /tool_input/command. Remap stdin, then delegate. Never block the agent.

MODE="${1:-claude}"

allow() {
  if [ "$MODE" = "cursor" ]; then
    printf '{"permission":"allow"}\n'
  fi
  exit 0
}

command -v rtk >/dev/null 2>&1 || allow
command -v jq >/dev/null 2>&1 || allow

INPUT=$(cat)
# Cursor may prefix hook stdin with one or two UTF-8 BOMs.
INPUT="${INPUT#$'\xEF\xBB\xBF'}"
INPUT="${INPUT#$'\xEF\xBB\xBF'}"
[ -n "$INPUT" ] || allow

if [ "$MODE" = "cursor" ]; then
  PAYLOAD=$(printf '%s' "$INPUT" | jq -c '
    def cmd: .tool_input.command // .toolInput.command // .command // empty;
    if cmd == "" then .
    else . + {tool_input: ((.tool_input // {}) + {command: cmd})}
    end
  ') || allow
  printf '%s' "$PAYLOAD" | rtk hook cursor || allow
  exit 0
fi

printf '%s' "$INPUT" | rtk hook claude || allow
exit 0
