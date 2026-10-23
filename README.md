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
| `ux-reviewer` | Interaction design (pre-implementation) and UX review (post-implementation) |
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
[Product Owner] → PM → [Architect, UX] → [Analytics, Security spec review, Accessibility spec review] → Developer → Docs Writer + [Security audit, UX review, Accessibility audit, Code Quality] → QA → Release/DevOps → PM
```

The core loop (PM → Developer → Docs Writer → QA → Release/DevOps → PM) always runs, in order. Specialist agents (brackets above) are invoked adaptively — only when the task warrants them. Spec reviews wait for the spec they review (Security after Architect, Accessibility and Analytics after UX). The orchestrator manages the whole thing.

Every agent's output is saved to `docs/handoffs/<task-slug>/` as a numbered file, along with the workflow state. Downstream agents read the full artifacts from disk. The orchestrator commits the handoff directory to the sprint branch and pushes at each phase boundary, so you can resume a task from another machine or environment.

Risk acceptance stays with you: the PM agent recommends, but QA conditions, shipping with Major QA findings, and Critical/High review findings are escalated to you to decide.

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

Then run the orchestrator as your **main session** — not as a subagent:

```bash
claude --agent orchestrator
```

or make it the default for the project in `.claude/settings.json`:

```json
{
  "agent": "orchestrator"
}
```

Describe the task and it will propose an execution plan for your approval before doing anything, then invoke the other agents as subagents. It has to be the main session because subagents can't ask you questions mid-run, so a subagent orchestrator couldn't get plan approval or escalate blockers.

The agents expect certain project documentation to exist — `docs/status.md`, `docs/outline.md`, a PRD/roadmap doc, `architecture.md`, `decision-log.md`. They will tell you what's missing if they can't find what they need.
