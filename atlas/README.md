# Real graph-bridge delivery

This package replaces the handoff’s partial `reference/srg_transports.py` with a deterministic, contract-clean verifier. It does **not** claim a kernel-continent merge without the live database needed to compute one.

## Files

- `srg_transports.py` — replacement transport proposer/verifier; standard library only.
- `brouwer-ground-truth.json` — exact 119-row Brouwer subset used by the verifier.
- `verified-edges.jsonl` — 141 case-scoped accepted edges; no widened untested ranges.
- `verification-output.json` — complete overlaps, balance, agreements, disagreements, undecided cases, and receipts.
- `independent_check.py` — separate implementation that recomputes Paley(13), a conference nonexistence case, and `S(2,4,25)` without importing the main verifier.
- `connectivity_impact.py` — read-only exact live-DB before/after analyzer; no-argument mode runs its synthetic self-test.
- `run_delivery_selftests.py` — re-executes all three tools and validates their final JSON receipts.
- `SELFTEST-RECEIPT.json` — aggregate 3/3 passing receipt.
- `CURRENT-SRG-TRANSPORTS-AUDIT.md` — direct audit of the supplied file.
- `CONNECTIVITY-REPORT.md` — proven scope and the explicitly unresolved giant-component measurement.
- `SOURCE-MAP.md` — resolvable sources and the exact role of each.
- `logs/` — raw execution receipts, including the original file’s failure.
- `audit/original-srg_transports.py` — byte-preserved supplied implementation for inspection.

## Re-run everything

Requires Python 3.10+ and no third-party packages.

```bash
python run_delivery_selftests.py
```

Expected final line:

```json
{"ok": true, "method": "graph-bridge-delivery-selftests", "passed": 3, "total": 3}
```

## Run the verifier

Bundled exact ground truth:

```bash
python srg_transports.py
```

Against the live repository facts table:

```bash
python srg_transports.py \
  --live-db /path/to/evidence/oracle-math.db \
  --report verification-live.json \
  --edges verified-edges-live.jsonl
```

The file emits an edge only when its exact proposed case is decided, the transport reaches at least five decided overlaps, and there are zero disagreements. One-sided results are retained but explicitly marked.

## Compute exact blade movement

```bash
python connectivity_impact.py \
  --db /path/to/evidence/oracle-math.db \
  --edges verified-edges.jsonl \
  --giant-component 668150 \
  --output connectivity-live.json
```

This operation opens the database read-only and does not insert edges or mutate components.

## Integration note

Copy `srg_transports.py`, `brouwer-ground-truth.json`, and optionally `connectivity_impact.py` into the engine directory. Review `verified-edges.jsonl`, rerun against the live facts table, run the exact connectivity analyzer, and only then merge accepted edges through the repository’s normal database writer.
