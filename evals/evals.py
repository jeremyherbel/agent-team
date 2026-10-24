#!/usr/bin/env python3
"""Run and score end-to-end evals of the agent team.

Each eval run copies an example project into a throwaway sandbox (via
examples/setup-sandbox.sh), runs the orchestrator headless on one task, answers
its questions with a fixed policy, and scores what it pushed to the sandbox's
local remote. Nothing touches a real repository.

  python3 evals/evals.py run --tasks blank-titles --runs 2   # costs money; see README
  python3 evals/evals.py score <run-dir> --task blank-titles [--judge]
  python3 evals/evals.py report <results-dir>

Requires Python 3.8+, git, node, and the claude CLI. The counter-plural check
also needs Playwright (found through NODE_PATH, e.g. a global install).
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

EVALS = Path(__file__).resolve().parent
REPO = EVALS.parent
GUARD_TEXT = "Blocked by agent-team guard"
DEFAULT_BRANCHES = {"main", "master"}
HANDOFF_BRANCH = "agent-handoffs"
# Signs that the orchestrator stopped to wait for a human.
WAITING = re.compile(
    r"awaiting your approval|approve to proceed|workflow blocked|decisions? (?:only you|for you)"
    r"|needs? your (?:decision|approval|input)|reply \"|\?\s*$",
    re.I,
)
FIRST_REPLY = "Approved. Proceed."
LATER_REPLY = "Follow the PM's recommendation on every open decision, and proceed."


def load_tasks():
    return {t["id"]: t for t in json.loads((EVALS / "tasks.json").read_text())["tasks"]}


def sh(args, cwd=None, env=None, timeout=None):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------- logs

def read_events(path):
    events = []
    for line in Path(path).read_text().splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return events


def turn_files(run_dir):
    return sorted(glob.glob(str(Path(run_dir) / "turn*.jsonl")), key=lambda p: int(re.search(r"turn(\d+)", p).group(1)))


def summarize_turn(events):
    """Cost, duration, final text, top-level agent runs, guard blocks, and plan text for one turn."""
    cost = duration = 0.0
    final, texts, agents, blocks = "", [], [], 0
    for e in events:
        if e.get("type") == "result":
            cost = max(cost, e.get("total_cost_usd") or 0)
            duration = max(duration, e.get("duration_ms") or 0)
            final = e.get("result") or final
        msg = e.get("message") or {}
        for block in msg.get("content") or []:
            if not isinstance(block, dict):
                continue
            if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
                if block.get("type") == "text":
                    texts.append(block.get("text", ""))
                if block.get("type") == "tool_use" and block.get("name") in ("Agent", "Task"):
                    inp = block.get("input") or {}
                    agents.append({"agent": inp.get("subagent_type"), "model": inp.get("model", "default")})
            if block.get("type") == "tool_result" and GUARD_TEXT in json.dumps(block.get("content", "")):
                blocks += 1
    return {"cost": cost, "duration_s": duration / 1000, "final": final, "texts": texts, "agents": agents, "guard_blocks": blocks}


# ---------------------------------------------------------------- remote state

def remote_heads(remote):
    out = sh(["git", "ls-remote", "--heads", str(remote)]).stdout
    return {line.split("refs/heads/", 1)[1]: line.split()[0] for line in out.splitlines() if "refs/heads/" in line}


def work_branch(remote):
    heads = remote_heads(remote)
    candidates = [b for b in heads if b not in DEFAULT_BRANCHES and b != HANDOFF_BRANCH]
    if not candidates:
        return None
    dated = [(sh(["git", "log", "-1", "--format=%ct", b], cwd=remote).stdout.strip() or "0", b) for b in candidates]
    return max(dated)[1]


def handoff_files(remote):
    if HANDOFF_BRANCH not in remote_heads(remote):
        return []
    return sh(["git", "ls-tree", "-r", "--name-only", HANDOFF_BRANCH], cwd=remote).stdout.split()


def release_done(remote):
    return any("release" in Path(f).name for f in handoff_files(remote))


# ---------------------------------------------------------------- scoring

def node_env():
    env = dict(os.environ)
    root = sh(["npm", "root", "-g"]).stdout.strip()
    if root:
        env["NODE_PATH"] = root + (os.pathsep + env["NODE_PATH"] if env.get("NODE_PATH") else "")
    return env


def judge(task, diff):
    """Grade the diff against the task's rubric with a fresh Sonnet session. Costs a few cents."""
    rubric = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(task["rubric"]))
    prompt = (
        "You are grading a code change against a rubric. Use only the diff below; do not run tools.\n\n"
        f"Task given to the developers:\n{task['prompt']}\n\nRubric:\n{rubric}\n\n"
        "Reply with only JSON: {\"criteria\": [{\"criterion\": <number>, \"pass\": true|false, \"note\": \"<one line>\"}]}\n\n"
        f"Diff:\n{diff[:120000]}"
    )
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(
            ["claude", "-p", "--model", "sonnet", "--max-budget-usd", "0.50", "--no-session-persistence", "--output-format", "json"],
            input=prompt, cwd=tmp, capture_output=True, text=True, timeout=600)
    try:
        outer = json.loads(r.stdout)
        text = outer.get("result", "")
        inner = json.loads(text[text.index("{"): text.rindex("}") + 1])
        passed = sum(1 for c in inner["criteria"] if c.get("pass"))
        return {"passed": passed, "total": len(task["rubric"]), "criteria": inner["criteria"], "cost": outer.get("total_cost_usd", 0)}
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return {"error": f"could not parse judge output: {e}", "raw": r.stdout[-500:]}


def score(run_dir, task, use_judge=False):
    run_dir = Path(run_dir)
    remote = run_dir / "remote.git"
    meta = json.loads((run_dir / "meta.json").read_text()) if (run_dir / "meta.json").exists() else {}
    turns = [summarize_turn(read_events(f)) for f in turn_files(run_dir)]
    first_texts = "\n".join(turns[0]["texts"] + [turns[0]["final"]]) if turns else ""
    handoffs = handoff_files(remote)
    names = [Path(f).name for f in handoffs]
    # The fast path posts its brief and starts at once, so the saved brief is the reliable signal.
    if any(n.startswith("00-brief") for n in names) or "Fast-Path Plan" in first_texts:
        tier = "fast"
    elif "Execution Plan" in first_texts or any(n.startswith("01-pm") for n in names):
        tier = "full"
    else:
        tier = "unknown"

    heads = remote_heads(remote)
    default = next((b for b in heads if b in DEFAULT_BRANCHES), None)
    default_untouched = (heads.get(default) == meta["initial_default_sha"]) if meta.get("initial_default_sha") \
        else sh(["git", "rev-list", "--count", default], cwd=remote).stdout.strip() == "1"
    branch = work_branch(remote)

    result = {
        "task": task["id"],
        "run_dir": str(run_dir),
        "tier": tier,
        "tier_correct": tier == task["expected_tier"],
        "human_replies": max(len(turns) - 1, 0),
        "agent_runs": sum(len(t["agents"]) for t in turns),
        "agents": [a for t in turns for a in t["agents"]],
        # A resumed (--continue) session reports the conversation's running total, so the last turn's figure is the cost.
        "cost_usd": round(max((t["cost"] for t in turns), default=0), 2),
        # Wall-clock time from the runner; older logs without it fall back to a lower bound.
        "duration_min": meta.get("duration_min") or round(sum(t["duration_s"] for t in turns) / 60, 1),
        "guard_blocks": sum(t["guard_blocks"] for t in turns),
        "default_branch_untouched": default_untouched,
        "work_branch": branch,
        "handoffs_saved": any(f.endswith("state.md") for f in handoffs),
        "release_done": any("release" in Path(f).name for f in handoffs),
        "budget_exhausted": meta.get("budget_exhausted", False),
        "leftover_processes": meta.get("leftover_processes", 0),
    }

    if branch:
        with tempfile.TemporaryDirectory() as tmp:
            clone = Path(tmp) / "work"
            sh(["git", "clone", "-q", "-b", branch, str(remote), str(clone)])
            result["tests_pass"] = sh(["npm", "test"], cwd=clone, timeout=300).returncode == 0
            shutil.copytree(EVALS / "hidden", clone / ".eval-hidden")
            checks = []
            for cmd in task["hidden_checks"]:
                r = subprocess.run(cmd, shell=True, cwd=clone, env=node_env(), capture_output=True, text=True, timeout=300)
                checks.append({"check": cmd, "status": "skipped" if r.returncode == 77 else "pass" if r.returncode == 0 else "fail",
                               "output": (r.stdout + r.stderr)[-800:]})
            result["hidden_checks"] = checks
            result["hidden_pass"] = all(c["status"] == "pass" for c in checks)
            if use_judge:
                base = default or "main"
                diff = sh(["git", "diff", f"origin/{base}...HEAD"], cwd=clone).stdout
                result["judge"] = judge(task, diff)
    else:
        result.update(tests_pass=False, hidden_pass=False, hidden_checks=[])

    (run_dir / "result.json").write_text(json.dumps(result, indent=2))
    return result


# ---------------------------------------------------------------- running

def processes_under(path):
    found = []
    for pid in os.listdir("/proc") if os.path.isdir("/proc") else []:
        if pid.isdigit():
            try:
                if os.path.realpath(f"/proc/{pid}/cwd").startswith(str(path)):
                    found.append(int(pid))
            except OSError:
                pass
    return found


def run_one(task, run_dir, permission_mode, max_turns):
    run_dir = Path(run_dir)
    setup = sh([str(REPO / "examples" / "setup-sandbox.sh"), task["example"], str(run_dir)])
    if setup.returncode != 0:
        sys.exit(f"sandbox setup failed: {setup.stderr}")
    project, remote = run_dir / "project", run_dir / "remote.git"
    meta = {"task": task["id"], "started": datetime.now(timezone.utc).isoformat(),
            "initial_default_sha": remote_heads(remote).get("main"), "permission_mode": permission_mode}

    spent, message, started = 0.0, task["prompt"], time.monotonic()
    for turn in range(1, max_turns + 1):
        remaining = task["budget_usd"] - spent
        # --max-budget-usd caps each invocation; passing what's left of the task budget keeps the
        # whole run under budget_usd whether the CLI counts per invocation or per conversation.
        if remaining < 0.25:
            meta["budget_exhausted"] = True
            break
        args = ["claude", "-p", "--agent", "orchestrator", "--permission-mode", permission_mode,
                "--output-format", "stream-json", "--verbose", "--max-budget-usd", f"{remaining:.2f}"]
        if turn > 1:
            args.insert(2, "--continue")
        with open(run_dir / f"turn{turn}.jsonl", "w") as out, open(run_dir / f"turn{turn}.err", "w") as err:
            subprocess.run(args + [message], cwd=project, stdout=out, stderr=err, timeout=3 * 3600)
        summary = summarize_turn(read_events(run_dir / f"turn{turn}.jsonl"))
        # The reported cost is the conversation's running total, earlier turns included.
        print(f"  turn {turn}: ${summary['cost'] - spent:.2f} (total ${summary['cost']:.2f})", flush=True)
        spent = max(spent, summary["cost"])
        if release_done(remote) or not WAITING.search(summary["final"].strip()):
            break
        message = FIRST_REPLY if turn == 1 else LATER_REPLY

    leftovers = processes_under(run_dir)
    for pid in leftovers:
        try:
            os.kill(pid, 9)
        except OSError:
            pass
    meta.update(leftover_processes=len(leftovers), finished=datetime.now(timezone.utc).isoformat(),
                duration_min=round((time.monotonic() - started) / 60, 1))
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))


# ---------------------------------------------------------------- report

def report(results_dir):
    rows = [json.loads(p.read_text()) for p in sorted(Path(results_dir).glob("*/result.json"))]
    if not rows:
        return "No results found."
    lines = ["| Task | Run | Finished | Tier ok | Tests | Hidden | Judge | Human replies | Agent runs | Cost | Minutes | Guard blocks | Default branch safe |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        j = r.get("judge") or {}
        judge_cell = f"{j['passed']}/{j['total']}" if "passed" in j else ("error" if j else "—")
        yes = lambda v: "yes" if v else "**no**"
        lines.append(f"| {r['task']} | {Path(r['run_dir']).name} | {yes(r['release_done'])} | {yes(r['tier_correct'])} ({r['tier']}) | {yes(r['tests_pass'])} | "
                     f"{yes(r['hidden_pass'])} | {judge_cell} | {r['human_replies']} | {r['agent_runs']} | ${r['cost_usd']:.2f} | "
                     f"{r['duration_min']} | {r['guard_blocks']} | {yes(r['default_branch_untouched'])} |")
    total = sum(r["cost_usd"] for r in rows)
    lines.append(f"\nTotal agent cost: ${total:.2f} across {len(rows)} runs (judge cost not included).")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run tasks end to end (spends money)")
    r.add_argument("--tasks", default="all", help="comma-separated task ids, or 'all'")
    r.add_argument("--runs", type=int, default=2, help="runs per task (default 2)")
    r.add_argument("--out", help="results directory (default evals/results/<timestamp>)")
    r.add_argument("--permission-mode", default="bypassPermissions",
                   help="sandbox runs only; the guard hook stays active (default bypassPermissions)")
    r.add_argument("--max-turns", type=int, default=5, help="max orchestrator turns per run, including the first")
    r.add_argument("--judge", action="store_true", help="also grade each diff with a Sonnet judge (a few cents per run)")
    r.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    s = sub.add_parser("score", help="score an existing run directory")
    s.add_argument("run_dir")
    s.add_argument("--task", required=True)
    s.add_argument("--judge", action="store_true")
    rp = sub.add_parser("report", help="summarize a results directory")
    rp.add_argument("results_dir")
    a = p.parse_args()

    tasks = load_tasks()
    if a.cmd == "score":
        print(json.dumps(score(a.run_dir, tasks[a.task], a.judge), indent=2))
    elif a.cmd == "report":
        print(report(a.results_dir))
    else:
        chosen = list(tasks) if a.tasks == "all" else a.tasks.split(",")
        cap = sum(tasks[t]["budget_usd"] for t in chosen) * a.runs
        print(f"{len(chosen)} task(s) x {a.runs} run(s). Spending cap: ${cap:.2f} (each run stops at its task's budget_usd).")
        if not a.yes and input("Proceed? [y/N] ").strip().lower() != "y":
            sys.exit("Cancelled.")
        out = Path(a.out or EVALS / "results" / datetime.now().strftime("%Y%m%d-%H%M%S"))
        for task_id in chosen:
            for n in range(1, a.runs + 1):
                run_dir = out / f"{task_id}-r{n}"
                print(f"{task_id} run {n}: {run_dir}", flush=True)
                run_one(tasks[task_id], run_dir, a.permission_mode, a.max_turns)
                res = score(run_dir, tasks[task_id], a.judge)
                print(f"  tier {res['tier']} | tests {res['tests_pass']} | hidden {res['hidden_pass']} | ${res['cost_usd']:.2f}", flush=True)
        report_md = report(out)
        (out / "report.md").write_text(report_md + "\n")
        print("\n" + report_md)


if __name__ == "__main__":
    main()
