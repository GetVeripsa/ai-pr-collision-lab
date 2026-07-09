# ai-pr-collision-lab

A small, deliberately boring Python order-pricing service used by the [Veripsa guided walkthrough](https://veripsa.com/try). It exists so you can see what a Veripsa Core check looks like on a pair of pull requests that need landing-order attention — without touching a repository you care about.

## Start here

| Need | Link |
| --- | --- |
| Guided walkthrough with copy buttons | <https://veripsa.com/try> |
| Install Veripsa Core | <https://veripsa.com/go/install?source=sandbox_readme> |
| Product overview | <https://veripsa.com/how-it-works> |
| Agent usage guide | <https://veripsa.com/docs/with-agents> |
| Share / quote Veripsa safely | <https://veripsa.com/share> |
| 日本語の共有キット | <https://veripsa.com/ja/share> |
| More examples | <https://github.com/GetVeripsa/veripsa-examples> |

## What's in here

- `orders/pricing.py` — order totals. The file both scenarios edit.
- `orders/catalog.py` — a tiny in-memory product catalog.
- `tests/test_pricing.py` — plain pytest tests.

Two prepared long-lived branches:

| Branch | Pretend author | What it changes |
| --- | --- | --- |
| `collide-a` | "Agent A" | Adds a bulk discount inside `calculate_total` in `orders/pricing.py` |
| `collide-b` | "Agent B" | Adds a large-cart discount in the same small product area |

Both branches are intentionally small. Each branch is easy to review on its own; the point of the lab is to see the PR-level warning shape when parallel work needs a safer landing order.

## Walkthrough (short form of [veripsa.com/try](https://veripsa.com/try))

The guided version with copy buttons lives at **https://veripsa.com/try**. This README is the source of truth for branch names and repo layout.

### 1. Fork this repository

Fork it to your own account. **The two scenario branches must come along:**

- Web UI: on the fork page, **uncheck** "Copy the `main` branch only".
- CLI: `gh repo fork GetVeripsa/ai-pr-collision-lab --clone` — the CLI
  copies all branches by default and clones your fork in one step.

If your fork ended up with only `main`, delete the fork and fork again with the checkbox unchecked.

### 2. Install Veripsa Core on your fork

Install from [veripsa.com/go/install](https://veripsa.com/go/install?source=sandbox_readme): choose **Only select repositories** and pick your fork. Veripsa runs where it is installed — on **your fork**, not on this upstream repository. No sign-up, no credit card, no email collected.

Give the first ingest a moment to finish before opening the PRs in Step 3; a brand-new install can briefly report a PR as Unknown.

### 3. Open the two prepared PRs — on your fork

From a clone of your fork:

```sh
FORK="$(gh api user -q .login)/ai-pr-collision-lab"
gh pr create --repo "$FORK" --base main --head collide-a --title "Demo scenario A" --body "Prepared Veripsa sandbox scenario A."
gh pr create --repo "$FORK" --base main --head collide-b --title "Demo scenario B" --body "Prepared Veripsa sandbox scenario B."
```

The `--repo` flag matters. Without it, `gh` in a fork clone asks you to run `gh repo set-default` — and that picker suggests this **upstream** repository first. PRs opened upstream are invisible to the install on your fork, so the checks you are waiting for never appear. You can also open both PRs from your fork's **Branches** page in the web UI; if you do, make sure the base repository shown in the compare view is your fork, not this one.

### 4. Read the checks

Each PR gets one check, named exactly `Veripsa`. Open the two PRs side by side, read the check summary and the PR comment, then click **Details** for the short explanation behind each verdict.

### 5. Then evaluate on a repository you maintain

This sandbox shows the shape of the check surface, nothing more. It is not a benchmark and it does not predict behaviour on your codebase. Install on a repository you actually work in and read the checks on real PR traffic before changing any merge policy.

## Honest notes

- The check is **advisory by default**. Whether it gates a merge is a branch-protection decision on your side, not something the App forces.
- Veripsa Core is not an AI code reviewer. It does not review style or content, and it does not store source file bodies.
- Nothing runs on this upstream repository on your behalf. Your fork plus your install is the whole demo.

## Running the code (optional)

```sh
python -m pytest
```

Requires Python 3.9+ and `pytest`. The service is intentionally small; it exists to be collided with.
