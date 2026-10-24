# Baseline, stage 1: fast-path tasks

Recorded 2026-10-24 against `main` at 4b6c1a9 (after PR #5), before any roles are folded into the main session. Two runs per task, with the Sonnet reviewer.

| Task | Run | Finished | Tier ok | Tests | Hidden | Judge | Human replies | Agent runs | Cost | Minutes | Guard blocks | Default branch safe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| blank-titles | blank-titles-r1 | yes | yes (fast) | yes | yes | 4/4 | 0 | 5 | $1.67 | 5.6 | 2 | yes |
| blank-titles | blank-titles-r2 | yes | yes (fast) | yes | yes | 4/4 | 0 | 5 | $1.28 | 4.4 | 1 | yes |
| counter-plural | counter-plural-r1 | yes | yes (fast) | yes | yes | 3/3 | 0 | 4 | $1.13 | 4.0 | 2 | yes |
| counter-plural | counter-plural-r2 | yes | yes (fast) | yes | yes | 3/3 | 0 | 4 | $0.82 | 2.8 | 0 | yes |

Total agent cost: $4.90 across 4 runs (judge cost not included).

Reviewer cost: $0.20.

Notes:
- **Guard blocks** were false positives from a guard bug: `$S/path` was split into `$` and `S/path`, and with QA's shell inside `.handoffs/` the guard took the scratch path for a handoff write. Fixed in this branch. Replaying all five blocked commands through the fixed guard allows them.
- **Path and reviewer scores** shown are after two scorer fixes: the fast-path tier is read from the saved `00-brief.md`, and the scope criterion no longer counts the PM's required status, outline, and PRD updates as scope creep.
- **PM ran** only on blank-titles, which is tracked in `docs/status.md`. Counter-plural isn't tracked, so the PM was correctly skipped.
