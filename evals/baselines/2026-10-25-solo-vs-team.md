# Plain Claude Code (solo) vs. the agent team

Recorded 2026-10-25. Solo = Claude Code on Opus with the project, its `CLAUDE.md`, and the safety guard only; one added instruction to push a branch. Same tasks, hidden checks, and reviewer as the team baselines.

| Task | Setup | Run | Finished | Tier ok | Tests | Hidden | Judge | Human replies | Nudges | Agent runs | Cost | Minutes | Guard blocks | Default branch safe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| blank-titles | solo | blank-titles-r1 | yes | n/a | yes | yes | 3/4 | 0 | 0 | 0 | $0.23 | 0.4 | 0 | yes |
| blank-titles | solo | blank-titles-r2 | yes | n/a | yes | yes | 3/4 | 0 | 0 | 0 | $0.22 | 0.4 | 0 | yes |
| counter-plural | solo | counter-plural-r1 | yes | n/a | yes | yes | 2/3 | 0 | 0 | 0 | $0.22 | 0.4 | 0 | yes |
| counter-plural | solo | counter-plural-r2 | yes | n/a | yes | yes | 2/3 | 0 | 0 | 0 | $0.20 | 0.3 | 0 | yes |
| due-dates | solo | due-dates-r1 | yes | n/a | yes | yes | 7/7 | 0 | 0 | 0 | $0.62 | 2.3 | 0 | yes |
| due-dates | solo | due-dates-r2 | yes | n/a | yes | yes | 7/7 | 0 | 0 | 0 | $0.70 | 2.0 | 0 | yes |

Total agent cost: $2.19 across 6 runs (judge cost not included).

Reviewer cost: $0.34.

| | Solo | Team (fast path, stage 1) | Team (full workflow, stages 3–4) |
|---|---|---|---|
| Small fixes: cost per run | $0.20–0.23 | $0.82–1.67 | — |
| Small fixes: minutes | under 1 | 3–6 | — |
| Due dates: cost per run | $0.62–0.70 | — | $12.14–16.31 |
| Due dates: minutes | about 2 | — | 34–54 |
| Finished, tests, hidden checks | all | all | all |
| Reviewer, due dates | 7/7, 7/7 | — | 6/7 to 7/7 |
| Reviewer, small fixes | missed the changelog every time | 3/3 and 4/4 | — |
| Human replies | 0 | 0 | 1–3 |
| New tests, due dates | 9–10 | — | 39 (stage 3 run 1) |
| Lines changed, due dates | about 170 | — | about 620 |

Caveats: two runs per task on a 200-line app. The hidden checks for due dates only cover backward compatibility, and the reviewer grades the diff, so the team's extra depth (time-zone tests, partial-date handling, browser and accessibility verification) isn't fully measured. The solo changelog misses come from the example's `CLAUDE.md` not mentioning a changelog; the team's Docs Writer adds one by rule.
