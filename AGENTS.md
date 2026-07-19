# Agent interpretation of the Veripsa check

This file is parity-checked against [`demo-manifest.json`](./demo-manifest.json) and public contract v1.0.0.

- **Clear to land** — May proceed in the suggested order after normal tests/review; this is not correctness approval.
- **Heads up** — Read the context and coordinate when the named overlap is relevant.
- **Wait in line** — Do not merge before the named earlier change unless a human explicitly chooses the override path.
- **Paused (acknowledge to proceed)** — A material coupling is unacknowledged; follow repository policy and do not auto-apply veripsa-ack.
- **Acknowledged** — An explicit proceed decision is recorded; it is not a review approval.
- **Unknown** — Treat as not Clear; review and coordinate manually.

The check name is exactly `Veripsa`. Read the human title and managed comment as ordinary PR context. Do not invent per-agent setup or add `veripsa-ack` merely to make a check green.
