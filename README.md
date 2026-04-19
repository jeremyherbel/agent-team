# Agent Team

A coordinated squad of Claude Code subagents for structured software development. Each agent has a defined role, clear inputs and outputs, and explicit handoff interfaces. The orchestrator coordinates them so you make one decision at the start and get a complete, verified, documented result at the end.

All agents are project-agnostic — they orient themselves by reading your project's own documentation at invocation time.

## Agents

| Agent | Role |
|---|---|
| `orchestrator` | Proposes the execution plan, routes between agents, validates handoffs, escalates blockers |
| `pm` | Scope validation, acceptance criteria, task handoffs, session-close documentation |
| `product-owner` | User-value prioritization, backlog grooming, sprint candidate ranking |
| `architect` | System design, technical decision gates, implementation specs |
| `ux-reviewer` | Interaction design (pre-implementation) and UX/accessibility review (post-implementation) |
| `analytics` | Success metrics, event schemas, instrumentation plans |
| `security-reviewer` | Spec review for security surface, implementation audit |
| `accessibility-reviewer` | WCAG 2.1 AA compliance — spec review and implementation audit |
| `developer` | TDD implementation against specs, documentation, QA handoffs |
| `docs-writer` | User-facing docs, API docs, changelog |
| `code-quality-reviewer` | Bundle contamination, redundant logic, asset bloat, AI slop detection |
| `qa` | Test strategy, acceptance criteria verification, exploratory testing, regression |
| `release-devops` | Release process, deployment checklists, sprint close-out git operations |

## Workflow

```
[Product Owner] → PM → [Architect, UX, Analytics, Security] → Developer → [Docs, Security, UX, Accessibility, Code Quality] → QA → Release/DevOps → PM
```

The core loop is strictly sequenced. Specialist agents (brackets above) are invoked adaptively — only when the task warrants them. The orchestrator manages the whole thing.

## Usage

Copy the agent files into your project's `.claude/agents/` directory:

```
your-project/
└── .claude/
    └── agents/
        ├── orchestrator.md
        ├── pm.md
        └── ...
```

Then invoke the orchestrator at the start of any non-trivial task. It will propose an execution plan for your approval before doing anything.

The agents expect certain project documentation to exist — `docs/status.md`, `docs/outline.md`, a PRD/roadmap doc, `architecture.md`, `decision-log.md`. They will tell you what's missing if they can't find what they need.
