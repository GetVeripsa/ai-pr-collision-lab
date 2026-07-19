#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shlex, subprocess, tempfile
from pathlib import Path

def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, text=True, capture_output=True)

def resolve_ref(repo: Path, branch: str) -> str:
    candidates = [f"refs/remotes/origin/{branch}", f"refs/heads/{branch}", branch]
    for candidate in candidates:
        if run("git", "rev-parse", "--verify", candidate, cwd=repo, check=False).returncode == 0:
            return candidate
    raise SystemExit(f"missing fixture branch: {branch}")

def test_ref(repo: Path, ref: str, command: str) -> None:
    with tempfile.TemporaryDirectory(prefix="veripsa-fixture-") as td:
        worktree = Path(td) / "tree"
        run("git", "worktree", "add", "--detach", str(worktree), ref, cwd=repo)
        try:
            result = subprocess.run(shlex.split(command), cwd=worktree, text=True, capture_output=True)
            if result.returncode:
                raise SystemExit(f"{ref}: tests failed\n{result.stdout}\n{result.stderr}")
        finally:
            run("git", "worktree", "remove", "--force", str(worktree), cwd=repo, check=False)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo / "demo-manifest.json").read_text(encoding="utf-8"))
    base = manifest["fixtureBaseCommit"]
    if run("git", "cat-file", "-e", f"{base}^{{commit}}", cwd=repo, check=False).returncode:
        raise SystemExit(f"fixture base commit is unavailable: {base}; fetch full history")
    main_ref = resolve_ref(repo, manifest["baseBranch"])
    if run("git", "merge-base", "--is-ancestor", base, main_ref, cwd=repo, check=False).returncode:
        raise SystemExit(f"{main_ref} is not descended from the recorded fixture base")
    if not args.skip_tests:
        test_ref(repo, main_ref, "python -m pytest -q")
        print(f"{manifest['baseBranch']}: tests verified")
    for scenario in manifest["scenarios"]:
        ref = resolve_ref(repo, scenario["branch"])
        merge_base = run("git", "merge-base", main_ref, ref, cwd=repo).stdout.strip()
        if merge_base != base:
            raise SystemExit(f"{scenario['branch']}: merge base {merge_base} != manifest {base}")
        changed = [p for p in run("git", "diff", "--name-only", f"{base}..{ref}", cwd=repo).stdout.splitlines() if p]
        expected = sorted(scenario["expectedChangedPaths"])
        if sorted(changed) != expected:
            raise SystemExit(f"{scenario['branch']}: changed paths {changed} != {expected}")
        if not args.skip_tests:
            test_ref(repo, ref, scenario["expectedTestCommand"])
        print(f"{scenario['branch']}: base/diff/tests verified")

if __name__ == "__main__":
    main()
