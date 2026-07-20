"""Parity check: README.md and AGENTS.md must agree with demo-manifest.json.

The manifest is the authority; prose is not. This fails closed when the docs
drift from the machine contract (scenario names/purposes/sources, the recorded
capture, the reproduce command, the contract version, or the agent-state map).
"""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "demo-manifest.json").read_text(encoding="utf-8"))
readme = (root / "README.md").read_text(encoding="utf-8")
agents = (root / "AGENTS.md").read_text(encoding="utf-8")


def require(text: str, value: str, label: str) -> None:
    if value not in text:
        raise SystemExit(f"{label} drift: missing {value!r}")


for scenario in manifest["scenarios"]:
    for key in ("outputBranch", "purpose", "sourceRef"):
        require(readme, str(scenario[key]), "README")

recorded = manifest["historicalRecordedRun"]
for key in ("captureDate", "captureCommit"):
    require(readme, str(recorded[key]), "README")

require(readme, manifest["reproducibleFixture"]["command"], "README")
require(readme, manifest["compatiblePublicContractVersion"], "README")

for pr in manifest["currentLiveProof"]["pullRequests"]:
    require(readme, f"#{pr}", "README")

for state in manifest["agentStates"]:
    require(agents, state["token"], "AGENTS")
    require(agents, state["action"], "AGENTS")

print("README and AGENTS match demo-manifest.json")
