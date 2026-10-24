#!/usr/bin/env python3
"""PreToolUse guard for the agent team.

Claude Code runs this before every Bash, Write, Edit, and NotebookEdit call
(see settings.example.json). It reads the hook input as JSON on stdin and
exits 2 with a reason on stderr to block the call, or exits 0 to let the
normal permission flow continue. It never approves anything.

Two kinds of rules:
- Safety rules apply to every session: no sudo, no recursive deletes outside
  the project, no force pushes or pushes to the default branch, no discarding
  work with git reset --hard or git clean -f, no piping downloads into a shell,
  no disk or power commands.
- Workflow rules apply when an agent from the team is running (the hook input
  carries agent_type): only some agents may push, only the orchestrator may
  touch .handoffs/ and push the agent-handoffs branch, files are staged by
  path, agents write only inside the project or a temp directory, and agents
  never read .env secrets (templates like .env.example are fine).

Shell parsing is best-effort. The guard is a safety net behind the agents'
instructions and Claude Code's permission system, not a sandbox.
Requires Python 3.8+ and nothing else.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile

HANDOFF_DIR = ".handoffs"
HANDOFF_BRANCH = "agent-handoffs"
# Agents allowed to run git push. Everyone else (reviewers, QA, Docs Writer,
# Architect, Analytics, Product Owner) produces reports or local commits only.
PUSHERS = {"orchestrator", "developer", "pm", "release-devops"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish"}
WRAPPERS = {"env", "nohup", "time", "command", "exec", "nice", "stdbuf", "timeout"}
SEPARATORS = {"&&", "||", ";", "|", "&", "\n", "(", ")"}
READERS = {"cat", "less", "more", "head", "tail", "grep", "rg", "awk", "sed", "source", ".", "strings", "xxd", "base64", "cp"}
SECRET_TEMPLATES = (".example", ".sample", ".template", ".dist")
READ_ONLY_GIT = {"log", "show", "status", "diff", "rev-parse", "ls-files", "ls-remote", "fetch", "blame", "grep", "describe", "cat-file"}


class Blocked(Exception):
    pass


def block(reason):
    raise Blocked(reason)


# ---------------------------------------------------------------- paths

def project_dir(data):
    return os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd())


def temp_dirs(data):
    dirs = {"/tmp", "/var/tmp", tempfile.gettempdir(), os.environ.get("TMPDIR", "")}
    if data.get("scratchpad_dir"):
        dirs.add(data["scratchpad_dir"])
    return {os.path.realpath(d) for d in dirs if d}


def resolve(path, cwd):
    return os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))


def inside(path, root):
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def is_secret_file(path):
    name = os.path.basename(path)
    return name == ".env" or (name.startswith(".env.") and not name.endswith(SECRET_TEMPLATES))


def in_handoffs(path, project):
    return inside(path, os.path.join(project, HANDOFF_DIR))


# ---------------------------------------------------------------- shell parsing

def strip_heredocs(command):
    """Drop heredoc bodies so text written to a file isn't mistaken for commands."""
    lines, out, delim = command.split("\n"), [], None
    for line in lines:
        if delim is not None:
            if line.strip() == delim:
                delim = None
            continue
        out.append(line)
        m = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
        if m:
            delim = m.group(2)
    return "\n".join(out)


def tokenize(command):
    lexer = shlex.shlex(strip_heredocs(command), posix=True, punctuation_chars=True)
    lexer.whitespace = " \t\r"  # keep newlines as command separators
    lexer.commenters = "#"
    return list(lexer)


def segments(tokens):
    """Split tokens into simple commands, remembering which ones a pipe feeds."""
    segs, current, piped = [], [], False
    for tok in tokens:
        if tok in SEPARATORS:
            if current:
                segs.append((current, piped))
            current, piped = [], tok == "|"
        else:
            current.append(tok)
    if current:
        segs.append((current, piped))
    return segs


def strip_prefix(words):
    """Drop leading VAR=value assignments and wrappers like env or nohup."""
    i = 0
    while i < len(words):
        w = words[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w) or w in WRAPPERS:
            i += 1
        elif words[i - 1:i] == ["timeout"] and re.match(r"^\d", w):
            i += 1
        else:
            break
    return words[i:]


def redirect_targets(words):
    targets = []
    for i, w in enumerate(words):
        if w in (">", ">>", ">|", "&>", "&>>") and i + 1 < len(words):
            targets.append(words[i + 1])
    return targets


def without_redirects(words):
    out, skip = [], False
    for w in words:
        if skip:
            skip = False
            continue
        if w in ("<", ">", ">>", ">|", "&>", "&>>", "<<", "<<-", "<<<"):
            skip = True
            continue
        out.append(w)
    return out


# ---------------------------------------------------------------- git helpers

def git_out(args, cwd):
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def default_branches(cwd):
    head = git_out(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd)
    return {head.split("/", 1)[1]} if "/" in head else {"main", "master"}


def split_git(args, cwd):
    """Return (repo_dir, subcommand, sub_args) for `git [global opts] sub ...`."""
    repo, i = cwd, 0
    while i < len(args) and args[i].startswith("-"):
        if args[i] == "-C" and i + 1 < len(args):
            repo = resolve(args[i + 1], repo)
            i += 2
        elif args[i] in ("-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(args):
            i += 2
        else:
            i += 1
    if i >= len(args):
        return repo, None, []
    return repo, args[i], args[i + 1:]


def check_git(args, cwd, agent, project):
    repo, sub, rest = split_git(args, cwd)
    if sub is None:
        return
    opts = [a for a in rest if a.startswith("-")]
    positional = [a for a in rest if not a.startswith("-")]

    if sub == "reset" and "--hard" in opts:
        block("git reset --hard discards uncommitted work. Commit or ask the human instead.")
    if sub == "clean" and any(re.match(r"^-[a-zA-Z]*f", o) or o == "--force" for o in opts):
        block("git clean -f deletes untracked files. Remove specific files by path, or ask the human.")

    if sub == "push":
        if any(o in ("-f", "--force", "--mirror", "--all") or o.startswith("--force-with-lease") or o == "--force-if-includes"
               or (re.match(r"^-[a-zA-Z]+$", o) and "f" in o) for o in opts) or any(p.startswith("+") for p in positional[1:]):
            block("Force pushes and --all/--mirror pushes are not allowed. History on shared branches is never rewritten.")
        current = git_out(["branch", "--show-current"], repo)
        refspecs = positional[1:]
        targets = []
        for spec in refspecs or [current]:
            dst = spec.split(":", 1)[-1]
            if dst == "HEAD" or spec == "HEAD":
                dst = current
            targets.append(dst.replace("refs/heads/", ""))
        if any(t in default_branches(repo) for t in targets):
            block("Pushing directly to the default branch is not allowed. Push a work branch and open a PR.")
        if agent:
            if agent not in PUSHERS:
                block(f"The {agent} agent may not push. Only {', '.join(sorted(PUSHERS))} push; report your result instead.")
            if HANDOFF_BRANCH in targets and agent != "orchestrator":
                block(f"Only the orchestrator pushes the {HANDOFF_BRANCH} branch.")

    if agent:
        if sub == "add" and any(a in ("-A", "--all", ".", ":/", "*", "-u", "--update") for a in rest):
            block("Stage files by path. git add -A, -u, and . can pick up work that QA never verified.")
        if sub == "commit" and any(o in ("--all",) or (re.match(r"^-[a-zA-Z]+$", o) and "a" in o) for o in opts):
            block("git commit -a stages everything. Stage files by path, then commit.")
        if agent != "orchestrator" and in_handoffs(repo, project) and sub not in READ_ONLY_GIT:
            block("Only the orchestrator writes to .handoffs/. Read handoff files; return your output instead.")


# ---------------------------------------------------------------- bash rules

def check_bash(command, data, agent, project, depth=0):
    if depth > 3:
        return
    try:
        tokens = tokenize(command)
    except ValueError:
        # Unbalanced quotes and similar: fall back to plain pattern checks.
        if re.search(r"\bsudo\b|git\s+push\b[^\n]*\s(-f|--force)\b|\brm\s+-[a-zA-Z]*[rR][a-zA-Z]*\s+/(\s|$)", command):
            block("This command matches a blocked pattern and could not be parsed safely. Rewrite it more simply.")
        return

    cwd = data.get("cwd") or project
    temps = temp_dirs(data)
    prev_cmd = None
    for words, piped in segments(tokens):
        targets = redirect_targets(words)
        words = strip_prefix(without_redirects(words))
        if not words:
            continue
        cmd, args = os.path.basename(words[0]), words[1:]

        if cmd == "cd" and args and not args[0].startswith(("$", "-")):
            cwd = resolve(args[0], cwd)

        if cmd in ("sudo", "doas", "su"):
            block(f"{cmd} is not allowed. Agents never need elevated privileges.")
        if cmd.startswith("mkfs") or cmd in ("shutdown", "reboot", "halt", "poweroff", "fdisk", "diskutil"):
            block(f"{cmd} is not allowed.")
        if cmd == "dd" and any(a.startswith("of=/dev/") for a in args):
            block("dd to a device is not allowed.")
        if piped and cmd in SHELLS and prev_cmd in ("curl", "wget"):
            block("Piping a download into a shell is not allowed. Download, read, then run it deliberately.")
        if cmd in SHELLS or cmd == "eval":
            inner = args[args.index("-c") + 1] if "-c" in args and args.index("-c") + 1 < len(args) else (" ".join(args) if cmd == "eval" else None)
            if inner:
                check_bash(inner, data, agent, project, depth + 1)

        if cmd == "rm" and any(a == "--recursive" or (re.match(r"^-[a-zA-Z]+$", a) and re.search("[rR]", a)) for a in args):
            for target in (a for a in args if not a.startswith("-")):
                if target.startswith(("$", "~")) or target in ("/", "/*", ".."):
                    block(f"Recursive delete of {target!r} is not allowed.")
                path = resolve(target, cwd)
                if path == project or not (inside(path, project) or any(inside(path, t) for t in temps)):
                    block(f"Recursive delete outside the project is not allowed: {target}")

        if cmd == "git":
            check_git(args, cwd, agent, project)

        if agent and cmd in READERS and any(is_secret_file(a) for a in args if not a.startswith("-")):
            block("Agents don't read .env files; secrets would end up in transcripts and handoffs. Use .env.example for variable names.")

        if agent and agent != "orchestrator":
            writes = targets[:]
            if cmd in ("rm", "mv", "cp", "tee", "touch", "mkdir", "rmdir", "ln", "truncate"):
                writes += [a for a in args if not a.startswith("-")]
            if cmd == "sed" and any(a.startswith("-i") or a == "--in-place" for a in args):
                writes += [a for a in args if not a.startswith("-")]
            if any(in_handoffs(resolve(w, cwd), project) for w in writes):
                block("Only the orchestrator writes to .handoffs/. Read handoff files; return your output instead.")

        prev_cmd = cmd


# ---------------------------------------------------------------- file-tool rules

def check_file_write(path, data, agent, project):
    if not path or not agent:
        return
    full = os.path.realpath(path)
    if agent != "orchestrator" and in_handoffs(full, project):
        block("Only the orchestrator writes to .handoffs/. Read handoff files; return your output instead.")
    if not inside(full, project) and not any(inside(full, t) for t in temp_dirs(data)):
        block(f"Agents write only inside the project or a temp directory, not {path}.")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # Not our input; stay out of the way.
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}
    agent = data.get("agent_type") or None
    project = project_dir(data)
    try:
        if tool == "Bash":
            check_bash(inp.get("command", ""), data, agent, project)
        elif tool in ("Write", "Edit", "MultiEdit"):
            check_file_write(inp.get("file_path"), data, agent, project)
        elif tool == "Read":
            if agent and is_secret_file(inp.get("file_path", "")):
                block("Agents don't read .env files; secrets would end up in transcripts and handoffs. Use .env.example for variable names.")
        elif tool == "NotebookEdit":
            check_file_write(inp.get("notebook_path"), data, agent, project)
    except Blocked as e:
        print(f"Blocked by agent-team guard: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
