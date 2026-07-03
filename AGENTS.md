# AGENTS.md

This repository uses Veripsa Core to coordinate parallel pull requests before
they merge. The merge rule for agents is the same one documented in
[CLAUDE.md](./CLAUDE.md): before merging any PR, read the Veripsa advisory
check (`gh pr checks <n>` and `gh pr view <n> --comments`) and act on the
state — merge on **Clear to land**, and on **Wait in line** do NOT merge but
land in the order the comment gives. Only add `veripsa-ack` on an explicit
human decision, never to silence the check.

Learn more: https://veripsa.com/docs/with-agents
