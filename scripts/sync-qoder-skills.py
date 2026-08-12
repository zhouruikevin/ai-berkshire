#!/usr/bin/env python3
"""Generate Qoder skills from AI Berkshire skill source files.

`skills/*.md` is the single source of truth for all platforms. This mirrors
each skill into `.qoder/skills/<name>/SKILL.md` with the frontmatter Qoder
requires (`name` + `description`) and injects a Qoder adapter note that
maps Claude Code-specific tool references (Task, Team, run_in_background)
to their Qoder equivalents.
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


def qoder_body(name: str, source_name: str, source_text: str) -> str:
    _, body = split_frontmatter(source_text)
    note = (
        "## Qoder adapter note\n\n"
        f"This skill is generated from `skills/{source_name}`. Qoder and "
        "Claude Code share one canonical workflow.\n\n"
        "- **Tool mapping**: This skill may reference `Task` (background agent), "
        "`Team` (multi-agent), or `run_in_background`. In Qoder, use the `Agent` "
        "tool for background/sub-agents (with `is_background=true` for Bash) and "
        "launch multiple parallel `Agent` calls instead of `Team`.\n"
        "- **Permission config**: `.claude/settings.local.json` references do "
        "not apply. In Qoder, tool permissions are handled by the IDE; if a tool "
        "is blocked, grant it via the IDE\'s permission prompt.\n"
        "- **Project rules**: References to `CLAUDE.md` are for project "
        "conventions. Qoder uses `AGENTS.md` and `.qoder/rules/` for the same "
        "purpose \u2014 follow whichever file is present and scoped to your role.\n"
        "- **Placeholders**: `$ARGUMENTS` and `$CURRENT_DATE` work identically "
        "in Qoder.\n"
        "- **Report output**: Use `qoder_report/` as the output directory (see "
        "CLAUDE.md report naming conventions).\n"
        "- **Shared tools**: Commands use workspace-relative paths (`python3 "
        "tools/...`), run from the repo root.\n\n"
    )
    return note + body.rstrip() + "\n"


def build(name: str, source_name: str, source_text: str) -> str:
    frontmatter, body = split_frontmatter(source_text)
    skill_name = field_value(frontmatter, "name") if frontmatter else None
    description = field_value(frontmatter, "description") if frontmatter else None
    if not skill_name:
        skill_name = name
    if not description:
        title = first_heading(body, name)
        description = f"AI Berkshire \u6295\u7814\u6280\u80fd\uff1a{title}\u3002\u6765\u6e90 skills/{name}.md\u3002"
    body_qoder = qoder_body(name, source_name, source_text)
    return f"---\nname: {skill_name}\ndescription: {description}\n---\n\n{body_qoder.rstrip()}\n"


def main() -> None:
    check = "--check" in sys.argv[1:]
    unknown = [arg for arg in sys.argv[1:] if arg != "--check"]
    if unknown:
        raise SystemExit(f"Unknown argument(s): {', '.join(unknown)}")

    count = 0
    stale: list[str] = []
    for source in sorted(CLAUDE_SKILLS.glob("*.md")):
        name = source.stem
        content = build(name, source.name, source.read_text(encoding="utf-8"))
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
