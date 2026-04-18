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
tools: Tool1, Tool2, ...   # optional; only when the agent needs restricted or specific tool access
---

Agent body...
```

All current agents use `model: sonnet`. Only `ux-reviewer` and `code-quality-reviewer` have explicit `tools:` declarations (both need Playwright browser tools and/or Bash/Glob access).

## Workflow architecture

The `orchestrator` agent coordinates all others. It does not do domain work — it routes, validates handoffs, tracks state, and escalates to the human when blocked.

**Core execution loop (strict sequencing):**

```
PM → [Architect, UX, Analytics, Security Reviewer pre-spec] → Developer → [Docs Writer, Security Reviewer audit, UX review, Accessibility Reviewer audit] → QA → Release/DevOps → PM (session close)
```

**Specialist invocation is adaptive** — not every task needs every agent. The orchestrator evaluates each task and invokes only the specialists the task warrants.

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

QA findings always escalate to PM, never directly to Developer.

## Conventions when editing agent files

- The `description` field is the invocation routing signal — keep it precise about scope and timing
- Output format sections (handoff formats, report formats) are consumed by the orchestrator's validation rules; changing them requires updating the orchestrator's validation checklist
- When a task or project reference is embedded in an agent (e.g., pm, product-owner, ux-reviewer), update it when the project changes rather than making the agent fully generic
- The orchestrator's workflow state table and validation checklists must stay consistent with whatever output formats the individual agents declare
