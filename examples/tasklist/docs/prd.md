# Product requirements

## Executive summary
Tasklist is a single-page to-do list for personal use. Sprint 1 shipped the core list. v1.0 adds due dates and an accessibility pass.

## Users
| User type | Goal | Context |
|---|---|---|
| Individual | Keep track of personal to-dos | Desktop and phone browsers, several times a day |

## Core user problems
1. Capturing a to-do takes too long, so people don't bother.
2. People miss things because nothing tells them a task is overdue.

## Non-goals
- Accounts, sync between devices, or sharing
- Recurring tasks, reminders, or notifications

## Release framing
- **v1.0:** Core list, due dates with overdue highlighting, WCAG 2.2 AA. Data stays in the browser.

## Success metrics
None tracked. The app has no analytics and v1.0 does not add any.

## Constraints
- **Accessibility target:** WCAG 2.2 AA
- **Data sensitivity:** Task titles may be personal. They never leave the browser.
- **Supported platforms:** Current Chrome, Firefox, and Safari, desktop and mobile

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Changing the stored task shape breaks existing users' lists | Med | High | Read old data safely; never drop tasks |

## Task status
| Task | Status |
|---|---|
| Core list | Done |
| Reject blank titles | Planned |
| Due dates | Planned |
