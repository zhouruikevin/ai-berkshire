#!/usr/bin/env python3
"""Generate Qoder skills from AI Berkshire skill source files.

`skills/*.md` is the single source of truth for all platforms. This mirrors
each skill into `.qoder/skills/<name>/SKILL.md` with the frontmatter Qoder
requires (`name` + `description`). Unlike the Codex adapter, no adapter note
is injected — Qoder loads project-level skills directly and consumes the
workflow text as-is.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILLS = ROOT / "skills"
QODER_SKILLS = ROOT / ".qoder" / "skills"


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5 :].lstrip("\n")


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def field_value(frontmatter: str, field: str) -> str | None:
    match = re.search(rf"(?m)^{field}:[ \t]*(.*)$", frontmatter)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def build(name: str, source_text: str) -> str:
    frontmatter, body = split_frontmatter(source_text)
    skill_name = field_value(frontmatter, "name") if frontmatter else None
    description = field_value(frontmatter, "description") if frontmatter else None
    if not skill_name:
        skill_name = name
    if not description:
        title = first_heading(body, name)
        description = f"AI Berkshire 投研技能：{title}。来源 skills/{name}.md。"
    return f"---\nname: {skill_name}\ndescription: {description}\n---\n\n{body.rstrip()}\n"


def main() -> None:
    check = "--check" in sys.argv[1:]
    unknown = [arg for arg in sys.argv[1:] if arg != "--check"]
    if unknown:
        raise SystemExit(f"Unknown argument(s): {', '.join(unknown)}")

    count = 0
    stale: list[str] = []
    for source in sorted(CLAUDE_SKILLS.glob("*.md")):
        name = source.stem
        content = build(name, source.read_text(encoding="utf-8"))
        target = QODER_SKILLS / name / "SKILL.md"
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                stale.append(str(target.relative_to(ROOT)))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        count += 1

    if check:
        if stale:
            print("Qoder skills are out of date:")
            for path in stale:
                print(f"  {path}")
            raise SystemExit(1)
        print(f"Checked {count} Qoder skills in {QODER_SKILLS.relative_to(ROOT)}")
        return

    print(f"Generated {count} Qoder skills in {QODER_SKILLS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
