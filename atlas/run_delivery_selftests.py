#!/usr/bin/env python3
"""Re-execute every delivery checker and validate its final JSON receipt."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMANDS = [
    [sys.executable, str(HERE / "srg_transports.py"),
     "--report", str(HERE / "verification-output.json"),
     "--edges", str(HERE / "verified-edges.jsonl")],
    [sys.executable, str(HERE / "independent_check.py")],
    [sys.executable, str(HERE / "connectivity_impact.py")],
]


def main() -> int:
    results = []
    for cmd in COMMANDS:
        proc = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=300)
        last = (proc.stdout.strip().splitlines() or [""])[-1]
        try:
            receipt = json.loads(last)
        except json.JSONDecodeError:
            receipt = {}
        ok = proc.returncode == 0 and receipt.get("ok") is True
        results.append({
            "tool": Path(cmd[1]).name,
            "ok": ok,
            "exit": proc.returncode,
            "method": receipt.get("method", ""),
            "stdout_tail": proc.stdout[-1200:],
            "stderr_tail": proc.stderr[-1200:],
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {Path(cmd[1]).name}: {receipt.get('method', '')}")
    final = {"ok": all(r["ok"] for r in results), "method": "graph-bridge-delivery-selftests", "results": results}
    (HERE / "SELFTEST-RECEIPT.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": final["ok"], "method": final["method"], "passed": sum(r["ok"] for r in results), "total": len(results)}))
    return 0 if final["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
