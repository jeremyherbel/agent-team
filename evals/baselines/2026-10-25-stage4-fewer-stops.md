# Stage 4: fewer stops (fixes C, B2, D), due-dates

Recorded 2026-10-25, measured against stage 3. Two runs, with the Sonnet reviewer ($0.27).

| Task | Run | Finished | Tier ok | Tests | Hidden | Judge | Human replies | Nudges | Agent runs | Cost | Minutes | Guard blocks | Default branch safe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| due-dates | due-dates-r1 | yes | yes (full) | yes | yes | 6/7 | 1 | 0 | 21 | $14.13 | 50.0 | 0 | yes |
| due-dates | due-dates-r2 | yes | yes (full) | yes | yes | 6/7 | 2 | 0 | 19 | $12.14 | 34.4 | 1 | yes |

Total agent cost: $26.27 across 2 runs (judge cost not included).

| | Stage 3 | Stage 4 |
|---|---|---|
| Finished | 2/2 | 2/2 |
| Human replies per run | 3, 3 | 1, 2 |
| Cost per run | $16.31, $13.96 | $14.13, $12.14 |
| Reviewer | 7/7, 6/7 | 6/7, 6/7 |

Findings:
- **Stops fell** from three per run to one and two. Run 1 met the goal (plan approval only).
- **Scope crept.** Both runs failed the reviewer's scope criterion for bundling pre-existing fixes (global focus rings, focus kept after toggle, 320px layout, counter colour). Fix D's "builds on it" clause is too broad: agents read nearby accessibility debt as Worsened. Part of each flag is the blank-title fix, which the approved plan sequenced first; the reviewer only sees the diff against `main`.
- **Run 2's second stop** was an opt-in (the title-input label) the orchestrator still waited on, against fix C.
- **Guard:** one block, a bulk `git add` caught by the stage-by-path rule — correct.
