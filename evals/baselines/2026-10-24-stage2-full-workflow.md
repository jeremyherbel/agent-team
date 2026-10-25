# Baseline, stage 2: full workflow (due-dates)

Recorded 2026-10-24 against the same agents as stage 1 (`main` at 4b6c1a9 plus the guard fix). Two runs, with the Sonnet reviewer. **Neither run finished**; the table is re-scored with the harness fixes from this branch.

| Task | Run | Finished | Tier ok | Tests | Hidden | Judge | Human replies | Nudges | Agent runs | Cost | Minutes | Guard blocks | Default branch safe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| due-dates | due-dates-r1 | **no** | yes (full) | yes | yes | 6/7 | 2 | 0 | 21 | $14.75 | 45.9 | 2 | yes |
| due-dates | due-dates-r2 | **no** | yes (full) | **no** | **no** | — | 1 | 0 | 7 | $5.12 | 19.7 | 0 | yes |

Total agent cost: $19.87 across 2 runs (judge cost not included).

Reviewer cost: $0.11 (run 2 had no branch to review).

What happened:
- **Run 1** reached QA round 2 (APPROVED WITH CONDITIONS) for $14.75, versus $20.73 for the pre-lean-run full workflow, which never got past QA round 1. It stopped twice for the human:
  1. Mid-run, to decide whether open backlog item 1 (blank titles) goes first. Following the PM, it ran item 1 as a fast-path sub-task and stacked due-dates on it.
  2. At release, because QA couldn't run Firefox or Safari in this environment and made that a condition of approval. The old runner didn't recognise "Choose one:" as a question and stopped there.
  - The PM applied the Origin rules correctly: it fixed the focus outline the new field would inherit (Introduced) and sent P3–P7 to the backlog. The reviewer's one failing criterion counts the stacked blank-title fix and the new control's accessibility as scope creep.
  - Guard blocks: the orchestrator's `git add .` inside `.handoffs/` (now exempt) and the Docs Writer trying to push (correctly blocked).
- **Run 2** started the Developer as a background agent and ended its turn; the headless process exited with the Developer still working. The runner now sets `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` and nudges with "Continue." when the orchestrator stops without asking anything.

Harness fixes since this run: finish and tier are scoped to the task's own handoff folder, nudges are counted separately from human decisions, more question phrasings are recognised, and the reviewer's pre-existing criterion allows fixes the change introduces or worsens.
