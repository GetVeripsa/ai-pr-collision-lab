# CLAUDE.md

This repository uses **Veripsa Core** (a GitHub App) to coordinate parallel
pull requests before they merge. When several agents open PRs at once, Veripsa
posts an advisory check on each one saying whether it may overlap other open
PRs, and in what order they are best landed.

The rule below is the actual one we use. We dogfooded it: a cold agent given
only this rule, on a real collision, read the verdict, merged the foundational
PR, held the queued one in order, and did not silence the check.

## Before merging a PR — check Veripsa first

Before merging any pull request, read the Veripsa advisory check and its comment.

1. Run `gh pr checks <n>` to see the Veripsa check status.
2. Run `gh pr view <n> --comments` to read the Veripsa comment.
3. Act on the state:
   - **Clear to land** — go ahead and merge.
   - **Heads up** — read the overlap; if it is fine, proceed.
   - **Wait in line** — do NOT merge. The comment names which PR should land
     first; report that order and wait for it. Do not reorder on your own.
   - **Unknown** — do not read this as "no collision". Ask the human.
4. Only add the `veripsa-ack` label when a human has explicitly decided to
   proceed despite the overlap — never to silence the check.

Learn more: https://veripsa.com/docs/with-agents
