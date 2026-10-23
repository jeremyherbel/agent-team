# Decision log

## ADR-001: No framework, no dependencies

**Status:** Accepted
**Date:** 2026-10-10

**Context**
The app is small, and the team wants it to run anywhere without an install step.

**Decision**
Use plain ES modules in the browser, Node's standard library for the server, and Node's built-in test runner.

**Rationale**
Nothing in v1.0 needs a framework. Zero dependencies means nothing to install, audit, or upgrade.

**Alternatives considered**
- React + Vite: more structure than the app needs, plus a build step

**Consequences**
- Rendering is manual DOM code in `app.js`
- Revisit if the UI grows past a few views

## ADR-002: Store tasks in localStorage

**Status:** Accepted
**Date:** 2026-10-10

**Context**
v1.0 has no accounts or sync.

**Decision**
Keep the task array as JSON under one localStorage key.

**Rationale**
Simple, works offline, and no data leaves the browser.

**Alternatives considered**
- IndexedDB: more capable, more code, not needed at this size

**Consequences**
- Any change to the task shape needs code that reads older data
