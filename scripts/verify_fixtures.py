#!/usr/bin/env python3
"""Verify the demo scenarios against their immutable source.

The scenarios are not stored as long-lived branches on this upstream
repository. Each one is an immutable annotated tag (``sourceRef`` in
``demo-manifest.json``) pointing at a recorded commit (``sourceCommit``). This
script checks, without needing any scenario branch to exist upstream, that
every source ref still:

  - peels to the exact recorded ``sourceCommit``,
  - shares the recorded ``fixtureBaseCommit`` as its merge base,
  - changes only the declared ``expectedChangedPaths``,
  - and passes its own tests.

It also confirms ``main`` still descends from the recorded fixture base. Run it
from a full clone that has the ``fixture-v1-*`` tags fetched (see README).
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import tempfile
from pathlib import Path


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, check=check, text=True, capture_output=True)


def resolve_commit(repo: Path, ref: str) -> str:
    """Peel ref (tag/branch/sha) to a commit SHA, or exit with a clear error."""
    result = run("git", "rev-list", "-n", "1", ref, cwd=repo, check=False)
    if result.returncode or not result.stdout.strip():
        raise SystemExit(f"missing source ref: {ref}; fetch the fixture-v1-* tags")
    return result.stdout.strip()


def resolve_base_branch(repo: Path, branch: str) -> str:
    """Resolve the mainline tip across full clones and CI PR checkouts.

    A local full clone has ``main``; a pull_request checkout is detached with no
    local branch, so fall back to the fetched remote ref (and finally HEAD, the
    PR merge commit, which still contains the fixture base)."""
    for candidate in (branch, f"refs/heads/{branch}", f"refs/remotes/origin/{branch}",
                      f"origin/{branch}", "FETCH_HEAD", "HEAD"):
        if run("git", "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}",
               cwd=repo, check=False).returncode == 0:
            return candidate
    raise SystemExit(f"could not resolve base branch {branch!r}")


def test_commit(repo: Path, sha: str, command: str) -> None:
    with tempfile.TemporaryDirectory(prefix="veripsa-fixture-") as td:
        worktree = Path(td) / "tree"
        run("git", "worktree", "add", "--detach", str(worktree), sha, cwd=repo)
        try:
            result = subprocess.run(shlex.split(command), cwd=worktree, text=True, capture_output=True)
            if result.returncode:
                raise SystemExit(f"{sha[:12]}: tests failed\n{result.stdout}\n{result.stderr}")
        finally:
            run("git", "worktree", "remove", "--force", str(worktree), cwd=repo, check=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo / "demo-manifest.json").read_text(encoding="utf-8"))

    if manifest.get("fixtureMode") != "materialize":
        raise SystemExit(f"unexpected fixtureMode: {manifest.get('fixtureMode')!r}")

    base = manifest["fixtureBaseCommit"]
    if run("git", "cat-file", "-e", f"{base}^{{commit}}", cwd=repo, check=False).returncode:
        raise SystemExit(f"fixture base commit is unavailable: {base}; fetch full history")

    main_ref = resolve_base_branch(repo, manifest["baseBranch"])
    if run("git", "merge-base", "--is-ancestor", base, main_ref, cwd=repo, check=False).returncode:
        raise SystemExit(f"{manifest['baseBranch']} ({main_ref}) is not descended from the recorded fixture base")
    if not args.skip_tests:
        test_commit(repo, resolve_commit(repo, main_ref), "python -m pytest -q")
        print(f"{manifest['baseBranch']}: tests verified")

    for scenario in manifest["scenarios"]:
        ref = scenario["sourceRef"]
        expected_sha = scenario["sourceCommit"]
        sha = resolve_commit(repo, ref)
        if sha != expected_sha:
            raise SystemExit(f"{ref}: peels to {sha} but manifest records {expected_sha}")

        merge_base = run("git", "merge-base", sha, base, cwd=repo).stdout.strip()
        if merge_base != base:
            raise SystemExit(f"{ref}: merge base {merge_base} != manifest {base}")

        changed = [p for p in run("git", "diff", "--name-only", f"{base}..{sha}", cwd=repo).stdout.splitlines() if p]
        expected = sorted(scenario["expectedChangedPaths"])
        if sorted(changed) != expected:
            raise SystemExit(f"{ref}: changed paths {changed} != {expected}")

        if not args.skip_tests:
            test_commit(repo, sha, scenario["expectedTestCommand"])
        print(f"{ref} -> {sha[:12]} ({scenario['outputBranch']}): commit/base/diff/tests verified")


if __name__ == "__main__":
    main()
