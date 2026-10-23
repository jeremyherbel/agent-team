# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A collection of Claude agent definition files for a coordinated multi-agent workflow. Each `.md` file defines one agent's role, responsibilities, operating principles, and output formats. These files are consumed by Claude Code's subagent system — they are not documentation, they are executable agent specifications.

## Usage

All agents are written as generics — none contain hardcoded project names, tech stacks, or app-specific logic. When deployed against a project, agents read the project's own documentation (`docs/status.md`, `docs/outline.md`, `docs/prd.md` or equivalent, `architecture.md`, `decision-log.md`, etc.) to orient themselves. Several agents specify exactly which docs to read and in what order before doing any work.

## Agent file format

Every agent file uses YAML frontmatter followed by a markdown body:

```markdown
---
name: agent-name
description: One paragraph used to determine when to invoke this agent. Be precise — this is the routing signal.
model: sonnet
tools: Tool1, Tool2, ...   # optional allow-list; only when the agent needs specific tool access
disallowedTools: Tool1, ...  # optional deny-list; removes tools from the inherited set
---

Agent body...
```

All current agents use `model: sonnet`. Tool access:
- `ux-reviewer` and `code-quality-reviewer` have explicit `tools:` allow-lists (Playwright browser tools and/or Read/Grep/Glob/Bash, no Write/Edit).
- `security-reviewer`, `accessibility-reviewer`, and `analytics` use `disallowedTools: Write, Edit, NotebookEdit, Agent`. They are advisory and must not edit files, but they keep inherited browser and MCP tools.
- All other agents inherit every tool because they write project files (code, tests, docs, decision log, status docs).

Every agent except the orchestrator has a "Handoff files" section explaining that upstream outputs are read from `docs/handoffs/<task-slug>/`. Keep it identical across agents.

## Workflow architecture

The `orchestrator` agent coordinates all others. It does not do domain work — it routes, validates handoffs, tracks state, and escalates to the human when blocked. It must run as the main session (`claude --agent orchestrator` or `"agent": "orchestrator"` in settings), because subagents have no `AskUserQuestion` tool and cannot get plan approval or escalate mid-run. It saves every agent's output to `docs/handoffs/<task-slug>/` as numbered files, and downstream agents read from there. It commits that directory to the sprint branch and pushes at phase boundaries, so work can resume from another environment.

**Execution flow:**

```
[Product Owner] → PM → [Architect, UX] → [Analytics, Security spec review, Accessibility spec review] → Developer → Docs Writer + [Security audit, UX review, Accessibility audit, Code Quality] → QA → Release/DevOps → PM (session close)
```

**The core loop is strict:** PM → Developer → Docs Writer → QA → Release/DevOps → PM always runs, in that order. **Specialist invocation (brackets) is adaptive.** Not every task needs every agent; the orchestrator invokes only the specialists the task warrants. Spec reviews wait for the spec they review. This flow must match the orchestrator's workflow graph, the README, and this file.

### Agent roles at a glance

| Agent | When invoked |
|---|---|
| `orchestrator` | Start of any non-trivial task |
| `pm` | Task intake and session close; owns `docs/status.md`, `docs/outline.md`, and PRD/roadmap docs |
| `product-owner` | Backlog grooming, user feedback processing, sprint candidate prioritization |
| `architect` | Structural/architectural work; resolves technical decision gates flagged by PM |
| `ux-reviewer` | Pre-implementation (spec) and post-implementation (review) for any user-facing surface |
| `analytics` | Before implementation when tracked user behavior is involved |
| `security-reviewer` | Pre-implementation (spec review) and post-implementation (audit) for auth/data/input surfaces |
| `accessibility-reviewer` | After UX spec is produced; after implementation and before QA |
| `developer` | After all upstream specs are complete |
| `code-quality-reviewer` | Post-implementation before QA; or standalone codebase health check |
| `docs-writer` | After implementation, before QA — changelog is always required |
| `qa` | After implementation and all pre-QA reviews; nothing ships without QA sign-off |
| `release-devops` | Sprint close-out (commit, push, PR); milestone ship checklists |

### Handoff validation

The orchestrator validates each agent's output before passing it forward. Key gates:
- PM handoff: scope verdict explicit, acceptance criteria independently testable
- Developer output: all acceptance criteria confirmed met, QA handoff present
- QA verdict: APPROVED / APPROVED WITH CONDITIONS / NOT APPROVED — explicit

QA findings always escalate to PM, never directly to Developer. The PM recommends but does not accept risk. QA conditions, shipping with Major QA findings, and Critical/High review findings go to the human. QA gets at most two rounds per task before the orchestrator escalates to the human.

Every review finding format carries a `Blocking: Yes / No` field. Security and Code Quality use a five-level severity scale; the others use four levels. The orchestrator's "Severity normalization" table maps between them.

## Conventions when editing agent files

- The `description` field is the invocation routing signal — keep it precise about scope and timing
- Output format sections (handoff formats, report formats) are consumed by the orchestrator's validation rules; changing them requires updating the orchestrator's validation checklist
- Keep every agent fully generic. Never embed project names, file paths, absolute paths, stack assumptions (framework, styling library, build tool, branch names), or product-specific goals. When an agent needs project facts, have it discover them: read the project's docs, inspect the manifest, or detect the default branch. Phrase stack-specific checks as examples ("e.g., Tailwind") and make them conditional on the stack.
- When you deploy these agents to a project, do not edit the copies to add project details. Put those details in the project's own docs (`CLAUDE.md`, `architecture.md`, `docs/guidelines.md`, and so on), which the agents already read.
- Before committing, grep for leftovers: absolute paths (`/sessions/`, `/Users/`, `/home/`), hardcoded branch names (`` `master` ``, `` `main` ``), and product-specific nouns.
- The orchestrator's workflow state table and validation checklists must stay consistent with whatever output formats the individual agents declare
