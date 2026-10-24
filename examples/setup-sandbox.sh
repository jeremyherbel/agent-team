#!/usr/bin/env bash
# Copy an example project into a throwaway git repo with the agents installed,
# so a test run can create branches, handoffs, and PRs without touching this repo.
#
# Usage: examples/setup-sandbox.sh <example> <target-dir>
#   e.g. examples/setup-sandbox.sh tasklist /tmp/tasklist-run
#
# Creates:
#   <target-dir>/remote.git  bare repo standing in for the remote ("origin")
#   <target-dir>/project     the example, with .claude/agents/, the guard hook, and settings installed, on branch main
set -euo pipefail

examples="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$examples/.." && pwd)"
name="${1:?usage: setup-sandbox.sh <example> <target-dir>}"
target="${2:?usage: setup-sandbox.sh <example> <target-dir>}"

[ -d "$examples/$name" ] || { echo "No example named '$name' in $examples" >&2; exit 1; }
[ -e "$target" ] && { echo "$target already exists; choose a new directory" >&2; exit 1; }

mkdir -p "$target"
target="$(cd "$target" && pwd)"

git init -q --bare -b main "$target/remote.git"
cp -R "$examples/$name" "$target/project"

mkdir -p "$target/project/.claude/agents"
for f in "$repo"/*.md; do
  case "$(basename "$f")" in
    README.md | CLAUDE.md) ;;
    *) cp "$f" "$target/project/.claude/agents/" ;;
  esac
done

mkdir -p "$target/project/.claude/hooks"
cp "$repo/hooks/guard.py" "$target/project/.claude/hooks/"
cp "$repo/settings.example.json" "$target/project/.claude/settings.json"

cd "$target/project"
git init -q -b main
git config user.name >/dev/null || git config user.name "Sandbox"
git config user.email >/dev/null || git config user.email "sandbox@example.invalid"
git add -A
git commit -q -m "Initial commit"
git remote add origin "$target/remote.git"
git push -q -u origin main

echo "Sandbox ready."
echo "  cd $target/project && claude --agent orchestrator"
