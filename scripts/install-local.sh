#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="$(python3 - "$ROOT_DIR/skill/SKILL.md" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
for line in text.splitlines():
    if line.startswith("name:"):
        print(line.split(":", 1)[1].strip().strip('"'))
        break
else:
    raise SystemExit("SKILL.md is missing name")
PY
)"
TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills/$SKILL_NAME"

if [[ "${1:-}" == "--dry-run" ]]; then
  printf 'Would sync %s/skill/ -> %s/\n' "$ROOT_DIR" "$TARGET_DIR"
  exit 0
fi

mkdir -p "$TARGET_DIR"
rsync -a --delete "$ROOT_DIR/skill/" "$TARGET_DIR/"
printf 'Synced %s -> %s\n' "$SKILL_NAME" "$TARGET_DIR"
