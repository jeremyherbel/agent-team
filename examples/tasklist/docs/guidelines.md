# Coding guidelines

## Conventions
- **Naming:** camelCase functions; files named for what they own
- **Structure:** Task logic goes in `public/tasks.js` as pure functions; DOM code stays in `public/app.js`
- **Errors:** Storage failures fall back to an empty list rather than breaking the page
- **Tests:** Every behavior in `public/tasks.js` has a unit test in `test/tasks.test.js`

## Commands
- Install: none (no dependencies)
- Run: `npm start`
- Test: `npm test`
- Lint: none

## Commit messages
`type(scope): short description` — types: feat, fix, test, docs, refactor, chore
