# AGENTS.md

Veripsa Core is installed once as a GitHub App. It automatically observes pull
request changes and creates or updates its native GitHub check. When useful, it
also keeps at most one managed PR comment current. There is no per-agent
installation, required CLI polling command, copied merge rule, or routine ACK
step.

An agent that already reads GitHub checks can use the Veripsa check and comment
as ordinary PR context. `veripsa-ack` is an optional, explicit response to a
specific warning; it is not setup and is not required for normal operation.

Learn more: <https://veripsa.com/docs/with-agents>
