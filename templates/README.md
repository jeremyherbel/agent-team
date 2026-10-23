# Project doc templates

The agents orient themselves by reading a project's own docs. These are minimal starting points for the docs they expect. Copy `docs/` into your project and fill in the brackets.

| File | Read by | Owned by |
|---|---|---|
| `docs/status.md` | PM, Architect, Product Owner, Docs Writer, Code Quality, Release/DevOps | PM |
| `docs/outline.md` | PM, Architect | PM |
| `docs/prd.md` | Every agent | PM / Product Owner |
| `docs/architecture.md` | Architect, Security, Release/DevOps, Code Quality | Architect |
| `docs/decision-log.md` | Architect, Security, Release/DevOps | Architect |
| `docs/design-language.md` | UX, Accessibility | UX |
| `docs/guidelines.md` | Code Quality, Developer | Architect |

Your project's own `CLAUDE.md` should say how to install, run, test and lint the project, and point to these docs. The agents never edit their own definitions to learn project details; they read these files instead.

Delete sections that don't apply rather than leaving them empty. The PM treats a stale or contradictory doc as a project risk.
