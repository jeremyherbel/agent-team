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
| `accessibility-reviewer` | WCAG 2.2 AA compliance — spec review and implementation audit |
| `developer` | TDD implementation against specs, documentation, QA handoffs |
| `docs-writer` | User-facing docs, API docs, changelog |
| `code-quality-reviewer` | Bundle contamination, redundant logic, asset bloat, AI slop detection |
| `qa` | Test strategy, acceptance criteria verification, exploratory testing, regression |
| `release-devops` | Release process, deployment checklists, sprint close-out git operations |

## Workflow

```
[Product Owner] → PM → [Architect, UX] → [Analytics, Security spec review, Accessibility spec review] → Developer → Docs Writer + [Security audit, UX review, Accessibility audit, Code Quality] → QA → Release/DevOps → PM (session close)
```

On the full workflow, the core loop (PM → Developer → Docs Writer → QA → Release/DevOps → PM) always runs, in order. Specialist agents (brackets above) are invoked adaptively — only when the task warrants them. Spec reviews wait for the spec they review (Security after Architect, Accessibility and Analytics after UX). The orchestrator manages the whole thing.

Every agent's output is saved as a numbered file in `.handoffs/<task-slug>/`, along with the workflow state, and downstream agents read the full artifacts from disk. `.handoffs/` is a separate git worktree of an orphan branch, `agent-handoffs`, which shares no history with your code and is never merged. The orchestrator commits and pushes after every handoff, so you can resume a task from another machine or environment, and handoffs never show up in code PRs or on your default branch. The branch is readable by anyone who can read the repo, so on a public repo the orchestrator flags that before saving security reports. Requires git 2.42+, or a one-time manual setup on older versions (see the orchestrator).

Small tasks take a **fast path**: Developer → Docs Writer (only if user-visible) → QA → Release/DevOps, from a short task brief the orchestrator posts before it starts. It doesn't wait for your approval, but you can interrupt. No PM, design, or review agents. A task qualifies only if it's small and localized and doesn't touch APIs, data models, auth, user flows, dependencies, or tracking. If any agent finds it doesn't qualify, work stops and the orchestrator proposes the full workflow.

Every agent defaults to Opus. The orchestrator chooses the model for each invocation — Sonnet or Haiku for well-specified or mechanical work, Opus for judgment calls (always for the Architect and Security Reviewer) — and lists its choices in the plan for you to approve or change.

After you approve the plan, the team works without you. It stops only for decisions that are genuinely yours: accepting risk on a serious problem the change introduced or made worse, a critical existing problem, a scope change, a conflict between agents, or going more than 50% over the plan's agent-run budget. Existing problems the reviewers notice go to the backlog instead of into the task.

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

Copy `reference/` to `.claude/agent-reference/` as well. It holds templates that agents read only when they need them (for example, Release/DevOps's runbook and rollback templates). Keep it outside `.claude/agents/`, so Claude Code doesn't load the templates as agents.

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

### Install the safety guard

Copy `hooks/guard.py` to `.claude/hooks/guard.py` in your project, and merge `settings.example.json` into your project's `.claude/settings.json`. Claude Code then runs the guard before every shell command, file read, and file write, including inside the agents. It needs `python3`.

For every session, the guard blocks:
- `sudo`, and disk or power commands
- recursive deletes outside the project
- force pushes, `--all` or `--mirror` pushes, and pushes straight to the default branch
- `git reset --hard` and `git clean -f`
- piping a download into a shell

For the team's agents, it also enforces the workflow rules:
- only the orchestrator, Developer, PM and Release/DevOps push
- only the orchestrator writes `.handoffs/` and pushes `agent-handoffs`
- files are staged by path (no `git add -A` or `git commit -a`)
- agents write only inside the project or a temp directory
- agents never read `.env` secrets (`.env.example` is fine)

The guard is a safety net, not a sandbox. Its shell parsing is best-effort, and it never approves anything, so Claude Code's normal permission checks still apply. If `python3` isn't available, the hook can't run and the guard does nothing, so check that it works after installing.

### Running unattended

Use auto mode: `claude --agent orchestrator --permission-mode auto`. It's the default for interactive sessions on recent Claude Code versions. A classifier reviews each action and blocks risky ones instead of asking you, so the team can work without you while its actions are still checked. Avoid `--permission-mode bypassPermissions` outside a throwaway sandbox: it removes that check and leaves only the guard.

The agents expect certain project documentation to exist — `docs/status.md`, `docs/outline.md`, a PRD/roadmap doc, `architecture.md`, `decision-log.md`. They will tell you what's missing if they can't find what they need. [`templates/`](templates/) has a minimal starting point for each.

## Trying it out

[`examples/`](examples/) has a small sample project with its docs filled in and ready-made tasks: one for the fast path and one for the full workflow. `examples/setup-sandbox.sh` copies an example into a throwaway git repo with the agents installed, so a test run can't touch your real repositories.
