from pathlib import Path
import json
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "demo-manifest.json").read_text(encoding="utf-8"))
readme = (root / "README.md").read_text(encoding="utf-8")
agents = (root / "AGENTS.md").read_text(encoding="utf-8")
for scenario in manifest["scenarios"]:
    for value in (scenario["branch"], scenario["purpose"]):
        if value not in readme:
            raise SystemExit(f"README drift: missing {value!r}")
for key in ("captureDate", "captureCommit"):
    if str(manifest["recordedRun"][key]) not in readme:
        raise SystemExit(f"README drift: missing recordedRun.{key}")
if manifest["compatiblePublicContractVersion"] not in readme:
    raise SystemExit("README drift: missing compatible public contract version")
for state in manifest["agentStates"]:
    if state["token"] not in agents or state["action"] not in agents:
        raise SystemExit(f"AGENTS drift: missing {state['token']}")
print("README and AGENTS match demo-manifest.json")
