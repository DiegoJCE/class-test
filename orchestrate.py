#!/usr/bin/env python3
"""
Multi-agent build loop: Opus plans -> Sonnet builds -> Codex reviews -> fix -> repeat.
Runs hands-off until tasks are done or time runs out, then writes a README and pushes.

Usage (run from inside your fresh project folder, with SPEC.md in it):
    python orchestrate.py --minutes 40
    python orchestrate.py --minutes 40 --push --repo my-class-app

Works on Windows and Mac. Needs: git, claude (Claude Code), optionally codex and gh.
"""
import argparse, re, shutil, subprocess, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--minutes", type=float, default=40, help="hard time budget for the build")
ap.add_argument("--push", action="store_true", help="create GitHub repo and push at the end")
ap.add_argument("--repo", default=None, help="GitHub repo name (default: folder name)")
ap.add_argument("--planner", default="opus")
ap.add_argument("--builder", default="sonnet")
args = ap.parse_args()

START = time.time()
DEADLINE = START + args.minutes * 60
ROOT = Path.cwd()
LOG = ROOT / "agent_log.md"

def exe(name):
    return shutil.which(name)  # resolves claude.cmd / codex.cmd on Windows

CLAUDE, CODEX, GIT, GH = exe("claude"), exe("codex"), exe("git"), exe("gh")
if not CLAUDE or not GIT:
    sys.exit("Need both `claude` and `git` on PATH.")
if not (ROOT / "SPEC.md").exists():
    sys.exit("No SPEC.md in this folder. Write one first.")

def left():
    return DEADLINE - time.time()

def log(msg):
    stamp = f"[{(time.time()-START)/60:5.1f} min]"
    print(stamp, msg, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{stamp} {msg}\n")

def run(cmd, timeout=None):
    t = max(30, min(timeout or left(), left()))
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=t)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"

def claude(prompt, model, max_turns=40):
    return run([CLAUDE, "-p", prompt, "--model", model,
                "--dangerously-skip-permissions", "--max-turns", str(max_turns)])

def git(*a):
    return run([GIT, *a], timeout=60)

def commit(msg):
    git("add", "-A")
    code, out = git("commit", "-m", msg)
    if code == 0:
        log(f"committed: {msg}")

# ---------- setup ----------
if not (ROOT / ".git").exists():
    git("init")
    (ROOT / ".gitignore").write_text("node_modules/\n.env\n__pycache__/\ndist/\n.venv/\n", encoding="utf-8")
    commit("initial commit: spec")

codex_ok = bool(CODEX)
log(f"start. budget {args.minutes} min. codex reviewer: {'yes' if codex_ok else 'no (claude fallback)'}")

# ---------- 1. plan (Opus) ----------
log("planning with " + args.planner)
claude(
    "Read SPEC.md. Write PLAN.md: a numbered checklist of 4-8 small, independently "
    "testable build tasks in the order they should be built, formatted exactly as "
    "'- [ ] 1. task'. Task 1 must produce something runnable. Pick a simple stack "
    "that runs with one command. Do not write any app code yet.",
    args.planner, max_turns=10)
commit("plan")

def tasks():
    text = (ROOT / "PLAN.md").read_text(encoding="utf-8") if (ROOT / "PLAN.md").exists() else ""
    return re.findall(r"- \[ \] (\d+\..*)", text)

# ---------- 2. review ----------
def review():
    # Diff is NOT pasted into the prompt: Windows caps command-line length (~8k via .cmd shims).
    # The reviewer runs `git show HEAD` itself instead.
    prompt = ("You are a code reviewer. Run: git show HEAD  to see the latest commit, and read "
              "SPEC.md. Review that commit for bugs, crashes, and things that contradict the spec. "
              "Do NOT edit files. First line of your reply must be exactly "
              "'VERDICT: PASS' or 'VERDICT: FAIL', then a short list of concrete problems.")
    global codex_ok
    if codex_ok:
        code, out = run([CODEX, "exec", "--sandbox", "read-only", prompt], timeout=300)
        if code == 0 and "VERDICT" in out:
            return "codex", out
        log("codex failed (credits/auth?) -> switching reviewer to fresh claude session")
        codex_ok = False
    code, out = claude(prompt, args.builder, max_turns=5)
    return "claude", out

# ---------- 3. build loop (Sonnet builds, Opus rescues) ----------
while left() > 300:
    todo = tasks()
    if not todo:
        log("all tasks done")
        break
    task = todo[0]
    log(f"building: {task}")
    claude(f"Read SPEC.md and PLAN.md. Implement ONLY this task: {task}. "
           "Run the app/tests to confirm it works and fix any errors. "
           f"Then tick it off in PLAN.md by changing '- [ ] {task}' to '- [x] {task}'.",
           args.builder)
    commit(f"build: {task[:60]}")

    for attempt in range(2):
        if left() < 240:
            break
        who, verdict = review()
        (ROOT / "REVIEW.md").write_text(verdict, encoding="utf-8")
        if "VERDICT: PASS" in verdict:
            log(f"review ({who}): PASS")
            break
        fixer = args.builder if attempt == 0 else args.planner  # escalate to Opus on 2nd fail
        log(f"review ({who}): FAIL -> fixing with {fixer}")
        claude("Read REVIEW.md and fix the real problems it lists (ignore pure style nits). "
               "Run the app to confirm it still works.", fixer)
        commit(f"fix after review ({fixer})")

    if tasks() and tasks()[0] == task:  # builder never ticked it off -> don't loop forever
        log(f"task didn't complete, skipping: {task}")
        p = ROOT / "PLAN.md"
        p.write_text(p.read_text(encoding="utf-8").replace(f"- [ ] {task}", f"- [~] {task}"), encoding="utf-8")

# ---------- 4. wrap up ----------
log("writing README")
DEADLINE = time.time() + 240  # give the wrap-up its own few minutes
claude("Write README.md: what the app does, how to run it (exact commands), and a short "
       "'Built with' note saying it was built by Claude (Opus planner, Sonnet builder) "
       "with Codex review. Make sure the run command actually works.", args.builder, max_turns=10)
commit("readme")

if args.push:
    if not GH:
        log("gh CLI not found; push manually")
    else:
        name = args.repo or ROOT.name
        code, out = run([GH, "repo", "create", name, "--public", "--source", ".", "--push"], timeout=120)
        log("pushed to GitHub" if code == 0 else f"push failed: {out[-300:]}")

log("done")
