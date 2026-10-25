# Baseline, stage 3: full workflow (due-dates), first finished runs

Recorded 2026-10-25 with the harness fixes and two agent fixes (known decisions asked at plan approval; environment gaps kept out of QA conditions in qa.md). Two runs, with the Sonnet reviewer.

| Task | Run | Finished | Tier ok | Tests | Hidden | Judge | Human replies | Nudges | Agent runs | Cost | Minutes | Guard blocks | Default branch safe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| due-dates | due-dates-r1 | yes | yes (full) | yes | yes | 7/7 | 3 | 0 | 20 | $16.31 | 54.3 | 3 | yes |
| due-dates | due-dates-r2 | yes | yes (full) | yes | yes | 6/7 | 3 | 0 | 21 | $13.96 | 45.1 | 0 | yes |

Total agent cost: $30.27 across 2 runs (judge cost not included).

Reviewer cost: $0.27.

Each run stopped twice after plan approval:
1. **Optional pre-existing fixes and a pre-existing Critical were asked as decisions.** The PM's "the human can opt in" notes (O1–O3, the title-input focus outline) became blocking questions; run 2's reply ("follow the PM") pulled them in, which is what its reviewer failure flags. The unlabelled-checkbox problem was escalated as a Pre-existing Critical, but the feature puts its new overdue description on that checkbox and the PM said AC 9 couldn't pass without the fix — so it was Worsened, which is fixed in the task without asking.
2. **Environment gaps still became QA conditions.** The PM triage recommended making the untested Firefox, Safari, and screen-reader checks conditions of approval, and QA adopted them, so the orchestrator asked the human to accept. Both runs ended the same way: the PR opened with those checks listed as human actions before merge.

Guard blocks in run 1 were false positives (`git branch --show-current` inside `.handoffs/` treated as a write; a `sed -i` script treated as a file path), fixed on this branch. Replaying every block from every eval run through the fixed guard leaves only the Docs Writer's push attempt blocked, which is correct.
