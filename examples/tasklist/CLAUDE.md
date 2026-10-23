# Tasklist

A small to-do list web app. No framework and no dependencies: plain ES modules in the browser, served by a tiny Node static server.

## Commands
- Run: `npm start` (http://localhost:3000; set `PORT` to change it)
- Test: `npm test` (Node's built-in test runner)
- There is no build step and no linter.

## Layout
- `public/` — everything the browser loads
  - `tasks.js` — pure task logic, shared with the tests. Keep it free of DOM and storage code.
  - `storage.js` — localStorage persistence
  - `app.js` — DOM rendering and event wiring
- `server.js` — static file server for `public/`
- `test/` — unit tests for `public/tasks.js`

## Project docs
Read these before working: `docs/status.md`, `docs/outline.md`, `docs/prd.md`, `docs/architecture.md`, `docs/decision-log.md`, `docs/design-language.md`, `docs/guidelines.md`.
