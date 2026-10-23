# Architecture

## Overview
A static single-page app. `server.js` serves `public/`; everything else runs in the browser. There is no backend data store.

## Stack
- **Language / runtime:** JavaScript (ES modules); Node 20+ for the server and tests
- **UI:** Plain DOM, no framework; one stylesheet with CSS custom properties
- **Data:** Browser localStorage
- **Tests:** `node --test` (unit tests for `public/tasks.js`)
- **Build / deploy:** No build step. Any static host can serve `public/`.

## Components
| Component | Location | Responsibility |
|---|---|---|
| Task logic | `public/tasks.js` | Pure functions over the task array. No DOM, no storage. |
| Storage | `public/storage.js` | Load and save the task array |
| App | `public/app.js` | Render the list and wire events |
| Server | `server.js` | Serve static files from `public/` |

## Data model
| Entity | Fields | Stored in |
|---|---|---|
| Task | `id: string`, `title: string`, `done: boolean` | localStorage key `tasklist.tasks`, as a JSON array |

## State management
`app.js` holds the task array in one module-level variable. Every change goes through `update()`, which saves and re-renders. Logic that transforms tasks belongs in `tasks.js` so it stays testable.

## Security posture
- **Auth:** None
- **Input validation:** Task logic in `tasks.js` decides what is a valid task
- **Rendering:** Task titles are user text. Render them with `textContent`, never `innerHTML`.
- **Secrets:** None

## Constraints and conventions
- No runtime dependencies.
- Stored data from older versions must keep loading. Never drop a user's tasks.
