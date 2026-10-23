# Examples

Small projects for trying the agent team end to end. Each one comes with its project docs filled in (from [`templates/`](../templates/)) and a couple of ready-made tasks.

## Running an example

Don't run the agents inside this repository: they create branches, push, and open PRs. Set up a sandbox instead:

```bash
examples/setup-sandbox.sh tasklist /tmp/tasklist-run
cd /tmp/tasklist-run/project
claude --agent orchestrator
```

The sandbox is a fresh git repo with the agents installed in `.claude/agents/`. Its `origin` is a bare repo next to it (`/tmp/tasklist-run/remote.git`), so pushes stay on your machine. Release/DevOps can't open a real PR there; it should report that rather than fail silently.

## What a run costs

Each run starts real Claude sessions billed to your account, and most agents run on Opus. Measured on `tasklist`:

| Task | Path | Agent runs | Cost | Time |
|---|---|---|---|---|
| Task 1 (blank titles) | Fast path, start to finish | 5 | about $2.30 | about 5 minutes |
| Task 2 (due dates) | Full workflow, stopped before QA round 2 | about 20 | over $20 | about 40 minutes |

Start with Task 1. Run Task 2 only when you want to exercise the full workflow, and expect to answer several decision checkpoints along the way.

## `tasklist`

A to-do list with no framework and no dependencies (`npm start`, `npm test`). It has deliberate rough edges.

**Task 1 — fast path:**
> Users can add blank tasks made of spaces. Reject blank or whitespace-only titles, and trim whitespace from titles.

A good run classifies this as fast path, writes a brief with testable acceptance criteria, uses smaller models, and finishes with Developer → Docs Writer → QA → Release/DevOps. The "1 tasks left" counter is a separate bug: QA may note it, but it is out of scope.

**Task 2 — full workflow:**
> Let users give a task an optional due date. Incomplete tasks that are past their due date should be clearly highlighted.

A good run takes the full workflow:
- The Architect changes the stored task shape without breaking existing lists.
- UX specifies the date input and the overdue styling.
- Accessibility flags the existing problems: an unlabeled input, an unlabeled "×" button, `outline: none`, low-contrast completed tasks, and a counter that isn't announced.
- QA verifies all of it before release.
