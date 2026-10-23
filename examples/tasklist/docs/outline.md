# Outline

## v1.0 definition of done
- A user can capture, complete, and remove tasks, and the list survives a reload.
- A user can see at a glance what is overdue.
- The app meets WCAG 2.2 AA.
- Every behavior in `public/tasks.js` has unit tests.

## Roadmap
| Sprint | Goal | Status |
|---|---|---|
| 1 | Core list with persistence | ✅ Done |
| 2 | Trustworthy input; due dates | In progress |
| 3 | Accessibility pass; v1.0 | Planned |

## Sprint 1: core list
| Task | Acceptance summary | Status | Delivered |
|---|---|---|---|
| Add, complete, delete tasks | Tasks can be added, toggled, removed | ✅ | 2026-10-14 |
| Persistence | List survives a reload | ✅ | 2026-10-14 |
| Remaining counter | Shows count of incomplete tasks | ✅ | 2026-10-14 |

## Sprint 2: trustworthy input; due dates
| Task | Acceptance summary | Status | Delivered |
|---|---|---|---|
| Reject blank task titles | Blank or whitespace-only titles are not added; titles are trimmed | Planned | |
| Optional due dates | A task can have a due date; overdue tasks are highlighted | Planned | |

## Decision gates
| Gate | Decision needed | Blocks | Status |
|---|---|---|---|
| — | — | — | — |

## Backlog
| Priority | Item | Category | Notes |
|---|---|---|---|
| 1 | Reject blank task titles | Bug | Reported by users |
| 2 | Optional due dates with overdue highlighting | Core | Second core problem in the PRD |
| 3 | Filter by active / completed | Enhancement | |
| 4 | Edit a task's title | Enhancement | |
