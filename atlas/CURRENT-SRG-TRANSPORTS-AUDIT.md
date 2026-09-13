# Audit of the supplied `reference/srg_transports.py`

## Verdict

The supplied file is a **partial proposal generator, not a contract-clean verified transport tool**. It contains mathematically plausible complement, triangular-graph, and lattice-graph maps, but it cannot be accepted or banked as written.

## Direct execution result

Running the file from the supplied handoff exits with code 1 before any self-test executes:

```text
sqlite3.OperationalError: unable to open database file
```

The file hard-codes `../../evidence/oracle-math.db`, but that database is not in the handoff. The exact stdout, stderr, and exit-code receipts are preserved under `logs/original-run.*`.

## Contract failures found by inspection

1. **Wrong overlap floor.** The file sets `MIN_OVERLAP = 4`; `DOCTRINE.md` and `design_transports.py` require 5.
2. **The construction side is assumed, not computed.** `verify_construction()` says the source “always EXISTS” and checks only the SRG table status. It never constructs a triangular or lattice graph and never recomputes its exact SRG parameters.
3. **It emits beyond the verified overlap.** Verification looks only at decided SRG rows, but after a family passes, `build()` writes edges for every valid `n` in `range(2, 60)`, including cases not independently checked against ground truth.
4. **No EXISTS/NONE balance.** It does not report whether a result is one-sided, contrary to the doctrine’s explicit correction.
5. **Incomplete disagreement evidence.** Complement disagreements are truncated to five entries, so the returned report is not a complete audit trail.
6. **Non-resolvable receipts.** Receipts are prose descriptions without a paper, section, URL, or table row.
7. **Docstring/implementation mismatch.** The header claims a Latin-square transport, but `CONSTRUCTIONS` contains only triangular and lattice families.
8. **Missing requested families.** There is no conference-matrix transport, no explicit Paley construction, and no Steiner block-graph extension.
9. **Repository self-test incompatibility.** The last output line is human text, not JSON with `{"ok": true, ...}`; the supplied `run_selftests.py` convention would therefore mark the module failed even if its internal checks passed.
10. **No connectivity computation.** It does not measure which existing components or blade-bound nodes would move after the proposed edges are added.

## What the replacement changes

The delivered `srg_transports.py` is standalone and standard-library-only. It performs independent endpoint computation, uses `MIN_OVERLAP = 5`, preserves complete agreements/disagreements, reports EXISTS/NONE balance and `[ONE-SIDED]`, emits only the exact checked cases, carries resolvable source receipts, ends with a machine-readable self-test receipt, and includes a separate non-mutating live-database connectivity analyzer.
