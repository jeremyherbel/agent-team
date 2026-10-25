# Evals

End-to-end evals for the agent team. Use them to measure a change to the agents — folding a role into the main session, a new rule, a model change — against a baseline, instead of judging it from one run.

Following [Anthropic's guidance on folding subagents](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop): build evals first, change one thing at a time, run each task more than once (some regressions only show up in one of two runs), and keep a change only if scores don't drop.

## What a run does

1. Copies the example project into a throwaway sandbox (`examples/setup-sandbox.sh`): a fresh git repo with a local stand-in remote, the agents, the guard hook, and settings. Nothing touches a real repository.
2. Runs the orchestrator headless on the task. When it stops to ask, the runner replies with a fixed policy: "Approved. Proceed." to the plan, then "Follow the PM's recommendation on every open decision, and proceed." Each reply counts as a human interruption.
3. Stops when the release handoff exists, the orchestrator stops asking, the task's `budget_usd` is used up, or the turn limit is reached.
4. Scores what was pushed, in a fresh clone of the work branch.

## What gets scored

| Metric | How |
|---|---|
| Finished | A Release/DevOps handoff exists on `agent-handoffs` |
| Tier correct | The first plan is a fast-path plan or a full execution plan, as the task expects |
| Tests | `npm test` passes on the pushed branch |
| Hidden checks | Tests in `hidden/` the agents never see, copied in after the run |
| Judge (optional, `--judge`) | A fresh Sonnet session grades the diff against the task's rubric; capped at $0.50 per run |
| Human replies, agent runs, models, cost, minutes | From the run logs; cost is the conversation's total as reported by Claude Code |
| Guard blocks, default branch untouched, leftover processes | Safety signals |

## Tasks

`tasks.json` defines each task: the prompt, the expected tier, a budget cap, hidden checks, and a rubric. Current tasks, all on `examples/tasklist`:

| Task | Expected tier | Budget cap | Hidden check |
|---|---|---|---|
| `blank-titles` | fast | $6 | Unit tests: whitespace-only titles rejected, titles trimmed |
| `counter-plural` | fast | $6 | Browser check in Chromium: "1 task left" vs. "N tasks left" (needs Playwright) |
| `due-dates` | full | $20 | Unit tests: old saved lists still load; tasks without dates still work |

## Running

**Runs cost real money.** Every run is a set of Claude sessions billed to your account. Measured costs so far: about $1.80 for a fast-path task, and about $21 for a full-workflow task before the lean-run changes. The runner prints a spending cap and asks before starting; each run passes `--max-budget-usd` so it can't exceed its task's `budget_usd`.

```bash
python3 evals/evals.py run --tasks blank-titles,counter-plural --runs 2   # baseline for the fast path
python3 evals/evals.py run --tasks all --runs 2 --judge                  # full baseline
python3 evals/evals.py report evals/results/<timestamp>                  # summary table
python3 evals/evals.py score <run-dir> --task <id> [--judge]             # re-score one run
```

Results go to `evals/results/` (ignored by git), with each run's sandbox, logs, `meta.json`, and `result.json`, plus a `report.md` per batch.

Runs use `--permission-mode bypassPermissions` by default, which is acceptable only because each run is a throwaway sandbox with the guard hook installed. Pass `--permission-mode auto` to match how you'd run the team for real.

## Adding a task

Add an entry to `tasks.json`, and add hidden checks to `hidden/` that test behavior any correct implementation must have — not a particular design. Check that the hidden checks fail on the unmodified example and pass on a correct fix before relying on them.
