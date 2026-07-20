#!/usr/bin/env python3
"""Materialize the demo collision scenarios into your own fork.

The scenario branches are not stored on this upstream repository. Each
scenario is kept as an immutable annotated tag (see ``sourceRef`` in
``demo-manifest.json``). This script recreates those branches in a fork you
control, so anyone can reproduce the two-PR collision walkthrough without a
long-lived branch ever existing on the shared upstream repository.

What it does, in order, for every scenario:

  1. Refuses to run against a dirty working tree (fail closed).
  2. Refuses to target the upstream repository (fork-only).
  3. Fetches the immutable source tags read-only from the canonical repo.
  4. Verifies each source ref peels to the exact recorded commit, shares the
     recorded fixture base, changes only the declared paths, and passes its
     own tests.
  5. Checks the fork's current branch state and is idempotent:
       - branch absent          -> create it (only with --push)
       - branch already at SHA  -> nothing to do, success
       - branch at a different SHA -> stop; never force-push
  6. With --push, creates each branch on the fork with a plain (never forced)
     push.

Data boundary: this script talks only to git/GitHub over your own credential
helper. It sends nothing to Veripsa, prints no tokens or credential URLs, and
carries no file or diff bodies anywhere. Veripsa Core sees data only after you
install the GitHub App on the fork and open the pull requests.

Typical use, from a clone of your fork or of this repository:

    FORK="$(gh api user -q .login)/ai-pr-collision-lab"
    python scripts/materialize_fixtures.py --fork "$FORK" --push
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, check=check, text=True, capture_output=True)


def fail(message: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"materialize: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_slug(value: str) -> tuple[str, str]:
    """Return (owner, repo) from owner/repo or an https/ssh GitHub URL.

    Any userinfo (credentials) in a URL is discarded and never echoed.
    """
    text = value.strip()
    ssh = re.match(r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?/?$", text)
    if ssh:
        return ssh.group("owner"), ssh.group("repo")
    https = re.match(
        r"^https?://(?:[^@/]+@)?github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
        text,
    )
    if https:
        return https.group("owner"), https.group("repo")
    slug = re.match(r"^(?P<owner>[^/\s]+)/(?P<repo>[^/\s]+?)(?:\.git)?$", text)
    if slug:
        return slug.group("owner"), slug.group("repo")
    fail(f"could not parse --fork {value!r}; use owner/repo or a GitHub URL")


def verify_scenario(repo: Path, base: str, scenario: dict, skip_tests: bool) -> str:
    """Verify one scenario against its immutable source; return the source SHA."""
    ref = scenario["sourceRef"]
    expected_sha = scenario["sourceCommit"]
    output = scenario["outputBranch"]

    peeled = run("git", "rev-list", "-n", "1", ref, cwd=repo, check=False)
    if peeled.returncode or not peeled.stdout.strip():
        fail(f"{output}: source ref {ref!r} is missing; could not fetch the immutable tag")
    sha = peeled.stdout.strip()
    if sha != expected_sha:
        fail(f"{output}: source ref {ref} is {sha}, manifest expects {expected_sha}")

    if run("git", "cat-file", "-e", f"{base}^{{commit}}", cwd=repo, check=False).returncode:
        fail(f"{output}: fixture base {base} is unavailable")
    merge_base = run("git", "merge-base", sha, base, cwd=repo).stdout.strip()
    if merge_base != base:
        fail(f"{output}: source does not share the recorded fixture base {base}")

    changed = sorted(
        p for p in run("git", "diff", "--name-only", f"{base}..{sha}", cwd=repo).stdout.splitlines() if p
    )
    expected_paths = sorted(scenario["expectedChangedPaths"])
    if changed != expected_paths:
        fail(f"{output}: source changes {changed}, manifest expects {expected_paths}")

    if not skip_tests:
        command = scenario["expectedTestCommand"]
        with tempfile.TemporaryDirectory(prefix="veripsa-materialize-") as td:
            tree = Path(td) / "tree"
            run("git", "worktree", "add", "--detach", str(tree), sha, cwd=repo)
            try:
                result = subprocess.run(shlex.split(command), cwd=tree, text=True, capture_output=True)
                if result.returncode:
                    fail(f"{output}: scenario tests failed at {sha[:12]}")
            finally:
                run("git", "worktree", "remove", "--force", str(tree), cwd=repo, check=False)

    print(f"  verified {output}: {ref} -> {sha[:12]} (base/diff/tests ok)")
    return sha


def remote_branch_sha(fork_url: str, branch: str, cwd: Path) -> str | None:
    result = run("git", "ls-remote", fork_url, f"refs/heads/{branch}", cwd=cwd, check=False)
    if result.returncode:
        fail(f"could not read the fork over git; check that the fork exists and you can access it")
    line = result.stdout.strip()
    return line.split("\t", 1)[0] if line else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize demo scenarios into your fork.")
    parser.add_argument("--fork", help="Destination fork as owner/repo or a GitHub URL.")
    parser.add_argument("--push", action="store_true", help="Create the branches on the fork.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip the per-scenario test run.")
    parser.add_argument("--allow-dirty", action="store_true", help="Bypass the clean-tree guard.")
    parser.add_argument(
        "--source-remote",
        help="Override the read-only source (defaults to the manifest repository).",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo / "demo-manifest.json").read_text(encoding="utf-8"))
    upstream_owner, upstream_repo = parse_slug(manifest["repository"])
    base = manifest["fixtureBaseCommit"]
    scenarios = manifest["scenarios"]

    # Critical safety invariant, evaluated first so it fires regardless of tree
    # state or --allow-dirty: never target the shared upstream repository.
    if not args.fork:
        fail("--fork is required (owner/repo of the fork you control)")
    fork_owner, fork_repo = parse_slug(args.fork)
    if (fork_owner.lower(), fork_repo.lower()) == (upstream_owner.lower(), upstream_repo.lower()):
        fail(
            f"refusing to target the upstream repository {upstream_owner}/{upstream_repo}; "
            "point --fork at your own fork"
        )

    if not args.allow_dirty:
        dirty = run("git", "status", "--porcelain", cwd=repo, check=False).stdout.strip()
        if dirty:
            fail("working tree is not clean; commit/stash first or pass --allow-dirty")

    fork_url = f"https://github.com/{fork_owner}/{fork_repo}.git"
    source_url = args.source_remote or f"https://github.com/{upstream_owner}/{upstream_repo}.git"

    # Read-only fetch of the immutable source tags; base arrives as ancestor.
    refspecs = [f"refs/tags/{s['sourceRef']}:refs/tags/{s['sourceRef']}" for s in scenarios]
    fetch = run("git", "fetch", "--quiet", source_url, *refspecs, cwd=repo, check=False)
    if fetch.returncode:
        fail("could not fetch the immutable source tags from the canonical repository")

    print(f"source: {upstream_owner}/{upstream_repo}  ->  fork: {fork_owner}/{fork_repo}")

    plans: list[tuple[dict, str, str]] = []  # (scenario, sha, action)
    for scenario in scenarios:
        sha = verify_scenario(repo, base, scenario, args.skip_tests)
        branch = scenario["outputBranch"]
        current = remote_branch_sha(fork_url, branch, repo)
        if current is None:
            action = "create"
        elif current == sha:
            action = "present"
        else:
            fail(
                f"{branch}: fork already has this branch at {current[:12]} (expected {sha[:12]}). "
                "Delete it on your fork to re-materialize; this script never force-pushes."
            )
        plans.append((scenario, sha, action))

    to_create = [(s, sha) for (s, sha, action) in plans if action == "create"]
    already = [s["outputBranch"] for (s, _, action) in plans if action == "present"]
    for name in already:
        print(f"  {name}: already present on the fork at the expected commit (nothing to do)")

    if not args.push:
        if to_create:
            names = ", ".join(s["outputBranch"] for (s, _) in to_create)
            print(f"\nplan: would create {names} on {fork_owner}/{fork_repo}. Re-run with --push.")
        else:
            print("\nnothing to create; the fork is already fully materialized.")
        return

    for scenario, sha in to_create:
        branch = scenario["outputBranch"]
        # Plain push of a known commit to a new branch: a create can never be a
        # non-fast-forward, so --force is neither used nor needed.
        pushed = run("git", "push", fork_url, f"{sha}:refs/heads/{branch}", cwd=repo, check=False)
        if pushed.returncode:
            fail(f"{branch}: push to the fork failed (check your git credentials/permissions)")
        print(f"  created {branch} on {fork_owner}/{fork_repo} at {sha[:12]}")

    print("\nDone. Open the two pull requests on your fork:")
    lead = manifest.get("currentLiveProof", {})
    _ = lead  # live-proof PRs live on upstream; the fork opens its own PRs below
    for scenario in scenarios:
        branch = scenario["outputBranch"]
        print(
            f"  gh pr create --repo {fork_owner}/{fork_repo} --base {manifest['baseBranch']} "
            f"--head {branch} --title {shlex.quote(scenario['pretendAuthor'] + ' demo scenario')} "
            f"--body {shlex.quote('Prepared Veripsa sandbox scenario.')}"
        )


if __name__ == "__main__":
    main()
