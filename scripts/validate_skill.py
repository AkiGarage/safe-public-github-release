#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skill"
SKILL_MD = SKILL_DIR / "SKILL.md"

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY"),
]
PRIVATE_PATH_MARKER = "/" + "Users/"
PRIVATE_PATH_RE = re.compile(re.escape(PRIVATE_PATH_MARKER) + r"[A-Za-z0-9._-]+/")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail("SKILL.md frontmatter must close with ---")
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def iter_files() -> list[Path]:
    ignored_parts = {".git", ".autoreview-reports", ".pytest_cache", "__pycache__"}
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        files.append(path)
    return files


def validate_skill() -> str:
    if not SKILL_MD.exists():
        fail("skill/SKILL.md is missing")
    text = read_text(SKILL_MD)
    fields = parse_frontmatter(text)
    name = fields.get("name")
    description = fields.get("description")
    if not name:
        fail("SKILL.md frontmatter must include name")
    if not description:
        fail("SKILL.md frontmatter must include description")
    if not re.fullmatch(r"[a-z0-9-]{1,63}", name):
        fail(f"Invalid skill name: {name}")
    if len(text.splitlines()) > 500:
        fail("SKILL.md should stay under 500 lines")
    if (SKILL_DIR / "README.md").exists():
        fail("Do not put repo README.md inside the skill package")
    return name


def validate_agents_metadata(skill_name: str) -> None:
    metadata = SKILL_DIR / "agents" / "openai.yaml"
    if not metadata.exists():
        return
    text = read_text(metadata)
    for key in ["display_name", "short_description", "default_prompt"]:
        if key not in text:
            fail(f"agents/openai.yaml missing {key}")
    if f"${skill_name}" not in text:
        fail("agents/openai.yaml default_prompt must mention the skill token")


def validate_text_files() -> None:
    for path in iter_files():
        text = read_text(path)
        rel = path.relative_to(ROOT)
        for index, line in enumerate(text.splitlines(), start=1):
            if line.rstrip() != line:
                fail(f"Trailing whitespace in {rel}:{index}")
        if rel == Path("scripts/validate_skill.py"):
            continue
        if PRIVATE_PATH_RE.search(text):
            fail(f"Private local path found in {rel}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"Secret-like pattern found in {rel}")


def main() -> None:
    skill_name = validate_skill()
    validate_agents_metadata(skill_name)
    validate_text_files()
    print(f"OK: {skill_name}")


if __name__ == "__main__":
    main()
