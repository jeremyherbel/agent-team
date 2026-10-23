# Design language

## Color
| Token | Value | Use |
|---|---|---|
| `--color-text` | #1f2328 | Body text |
| `--color-muted` | #b0b0b0 | Completed task titles |
| `--color-accent` | #2f6feb | Primary buttons |
| `--color-danger` | #cf222e | Destructive actions |
| `--color-bg` | #ffffff | Page background |

## Typography
| Role | Font | Size / line height |
|---|---|---|
| Body | system-ui | 16px / 1.5 |
| Heading | system-ui | Browser default h1 |

## Components
- **Buttons:** Accent background, white text, 6px radius. Icon-only buttons are text glyphs.
- **Forms:** Single-line input with the submit button beside it.
- **Lists:** One row per task: checkbox, title, delete button.

## Interaction conventions
- **Focus:** Not yet defined.
- **Feedback:** The list re-renders immediately; there are no toasts.
- **Motion:** None.
