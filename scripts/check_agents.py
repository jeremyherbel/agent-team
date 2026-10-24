#!/usr/bin/env python3
"""Consistency checks for the agent definition files.

Catches the drift that CLAUDE.md asks editors to prevent: invalid frontmatter,
agents not defaulting to the opus model, agents missing from the orchestrator's tables, mismatched severity scales,
missing Blocking fields, divergent Handoff files sections, and project-specific
leftovers.

Usage: python3 scripts/check_agents.py [repo-root]
Requires PyYAML (pip install pyyaml).
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

FIVE_LEVEL = "Critical / High / Medium / Low / Note"
FOUR_LEVEL = "Critical / Major / Minor / Note"

# Every agent file must be registered here. When you add an agent, add it here
# and to the orchestrator's tables, the README, and CLAUDE.md.
#   display  - name used in the orchestrator's squad and workflow state tables
#   scale    - severity scale its finding format uses ("five", "four", or None)
#   short    - name used in the orchestrator's severity normalization table
#   blocking - its finding format must carry a "Blocking: Yes / No" field
#   advisory - must not be able to write files
AGENTS = {
    "orchestrator":           dict(display=None),
    "product-owner":          dict(display="Product Owner"),
    "pm":                     dict(display="PM"),
    "architect":              dict(display="Architect", scale="four", short="Architect"),
    "ux-reviewer":            dict(display="UX", scale="four", short="UX", blocking=True, advisory=True),
    "analytics":              dict(display="Analytics", advisory=True),
    "security-reviewer":      dict(display="Security Reviewer", scale="five", short="Security", blocking=True, advisory=True),
    "accessibility-reviewer": dict(display="Accessibility Reviewer", scale="four", short="Accessibility", blocking=True, advisory=True),
    "code-quality-reviewer":  dict(display="Code Quality Reviewer", scale="five", short="Code Quality", blocking=True, advisory=True),
    "developer":              dict(display="Developer"),
    "docs-writer":            dict(display="Docs Writer", scale="four", short="Docs", blocking=True),
    "qa":                     dict(display="QA", scale="four", short="QA"),
    "release-devops":         dict(display="Release/DevOps"),
}

DEFAULT_MODEL = "opus"
FRONTMATTER_KEYS = {"name", "description", "model", "tools", "disallowedTools"}
NOT_AGENTS = {"README.md", "CLAUDE.md"}

problems = []


def problem(where, message):
    problems.append(f"{where}: {message}")


def split_tools(value):
    return {t.strip() for t in str(value or "").split(",") if t.strip()}


def section(text, heading):
    """Body of a '## heading' section, up to the next '---' divider."""
    start = text.find(f"## {heading}\n")
    if start == -1:
        return None
    end = text.find("\n---\n", start)
    return text[start:end if end != -1 else len(text)]


def table_first_column(text, after_heading, bold=False):
    """First-column cells of the first markdown table after a heading line."""
    start = text.find(after_heading)
    if start == -1:
        return None
    cells, in_table = [], False
    for line in text[start:].splitlines()[1:]:
        if line.startswith("|"):
            in_table = True
            cell = line.split("|")[1].strip()
            if bold:
                m = re.fullmatch(r"\*\*(.+)\*\*", cell)
                if m:
                    cells.append(m.group(1))
            elif cell and not set(cell) <= set("-:") and cell != "Agent":
                cells.append(cell)
        elif in_table:
            break
    return cells


def check_frontmatter(path, text):
    if not text.startswith("---\n"):
        return problem(path.name, "missing YAML frontmatter")
    try:
        fm = yaml.safe_load(text.split("---\n", 2)[1])
    except yaml.YAMLError as e:
        return problem(path.name, f"frontmatter is not valid YAML ({str(e).splitlines()[0]})")
    if not isinstance(fm, dict):
        return problem(path.name, "frontmatter is not a mapping")
    for key in ("name", "description", "model"):
        if not fm.get(key):
            problem(path.name, f"frontmatter is missing '{key}'")
    for key in set(fm) - FRONTMATTER_KEYS:
        problem(path.name, f"unknown frontmatter key '{key}'")
    if fm.get("model") and fm["model"] != DEFAULT_MODEL:
        problem(path.name, f"model is '{fm['model']}'; every agent defaults to '{DEFAULT_MODEL}' and the orchestrator picks per invocation")
    if fm.get("name") and fm["name"] != path.stem:
        problem(path.name, f"name '{fm['name']}' does not match the file name")
    if AGENTS.get(path.stem, {}).get("advisory"):
        tools, denied = split_tools(fm.get("tools")), split_tools(fm.get("disallowedTools"))
        for t in ("Write", "Edit"):
            if (tools and t in tools) or (not tools and t not in denied):
                problem(path.name, f"advisory agent can use {t}; restrict it with tools: or disallowedTools:")


def check_finding_format(path, text, spec):
    if spec.get("scale") == "five":
        if FIVE_LEVEL not in text or FOUR_LEVEL in text:
            problem(path.name, f"finding format must use the five-level scale ({FIVE_LEVEL}) only")
    elif spec.get("scale") == "four":
        if FOUR_LEVEL not in text or FIVE_LEVEL in text:
            problem(path.name, f"finding format must use the four-level scale ({FOUR_LEVEL}) only")
    if spec.get("blocking") and not re.search(r"Blocking:(\*\*)? Yes / No", text):
        problem(path.name, "finding format is missing the 'Blocking: Yes / No' field")
    if (spec.get("blocking") or path.stem == "qa") and not re.search(r"Origin:(\*\*)? Introduced .*/ Worsened .*/ Pre-existing", text):
        problem(path.name, "finding format is missing the 'Origin: Introduced / Worsened / Pre-existing' field")


def check_leftovers(path, text):
    for n, line in enumerate(text.splitlines(), 1):
        if re.search(r"/sessions/|/Users/|/home/", line):
            problem(f"{path.name}:{n}", "absolute path")
        if re.search(r"`(main|master)`|\b(checkout|--base)\s+(main|master)\b", line) \
                and not re.search(r"do not assume", line, re.I):
            problem(f"{path.name}:{n}", "hardcoded branch name; detect the default branch instead")


def check_orchestrator(text):
    expected = {s["display"] for s in AGENTS.values() if s["display"]}
    for heading, bold, label in (("## The agent squad", True, "squad table"),
                                 ("### Agent status", False, "workflow state table")):
        rows = table_first_column(text, heading, bold=bold)
        if rows is None:
            problem("orchestrator.md", f"{label} not found")
            continue
        for name in sorted(expected - set(rows)):
            problem("orchestrator.md", f"{label} is missing '{name}'")
        for name in sorted(set(rows) - expected):
            problem("orchestrator.md", f"{label} lists unknown agent '{name}'")

    m = re.search(r"^\| Five-level scale \((.+?)\) \| Four-level scale \((.+?)\) \|$", text, re.M)
    if not m:
        return problem("orchestrator.md", "severity normalization table header not found")
    for col, scale in ((m.group(1), "five"), (m.group(2), "four")):
        listed = {s.strip() for s in col.split(",")}
        wanted = {s["short"] for s in AGENTS.values() if s.get("scale") == scale}
        if listed != wanted:
            problem("orchestrator.md", f"severity normalization {scale}-level column lists {sorted(listed)}, expected {sorted(wanted)}")


def check_docs(root):
    flows = {}
    for doc in ("README.md", "CLAUDE.md"):
        text = (root / doc).read_text()
        for name in AGENTS:
            if not re.search(rf"^\| `{re.escape(name)}` \|", text, re.M):
                problem(doc, f"agent table is missing `{name}`")
        flow = [l for l in text.splitlines() if l.startswith("[Product Owner] →")]
        flows[doc] = flow[0] if flow else None
        if not flow:
            problem(doc, "execution flow line not found")
    if None not in flows.values() and len(set(flows.values())) > 1:
        problem("README.md", "execution flow line differs from CLAUDE.md")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
    files = sorted(p for p in root.glob("*.md") if p.name not in NOT_AGENTS)

    for name in sorted(set(AGENTS) - {p.stem for p in files}):
        problem(f"{name}.md", "registered in check_agents.py but the file does not exist")

    handoff_sections = {}
    for path in files:
        spec = AGENTS.get(path.stem)
        if spec is None:
            problem(path.name, "not registered in scripts/check_agents.py AGENTS")
            continue
        text = path.read_text()
        check_frontmatter(path, text)
        check_finding_format(path, text, spec)
        check_leftovers(path, text)
        for ref in re.findall(r"\.claude/agent-reference/([\w.-]+\.md)", text):
            if not (root / "reference" / ref).exists():
                problem(path.name, f"points to .claude/agent-reference/{ref}, but reference/{ref} does not exist")
        if path.stem == "orchestrator":
            check_orchestrator(text)
        else:
            body = section(text, "Handoff files")
            if body is None:
                problem(path.name, "missing the 'Handoff files' section")
            else:
                handoff_sections[path.name] = body

    if handoff_sections:
        reference = max(set(handoff_sections.values()), key=list(handoff_sections.values()).count)
        for name, body in handoff_sections.items():
            if body != reference:
                problem(name, "'Handoff files' section differs from the other agents")

    check_docs(root)

    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s) found.")
        sys.exit(1)
    print(f"All {len(files)} agent files pass.")


if __name__ == "__main__":
    main()
