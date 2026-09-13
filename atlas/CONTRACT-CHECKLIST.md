# Acceptance-contract checklist

| Contract item | Delivered evidence | Status |
|---|---|---|
| Read and audit supplied `srg_transports.py` | `CURRENT-SRG-TRANSPORTS-AUDIT.md`, preserved original, raw failed-run receipt | Complete |
| Every cited path/source resolves | `SOURCE-MAP.md`; URLs embedded per ground-truth row | Complete |
| Re-runnable `selftest()` | `srg_transports.py`; final JSON receipt | Pass |
| Independent re-verification | `independent_check.py`, `logs/independent-check.log` | 9/9 pass |
| `MIN_OVERLAP >= 5` | main verifier and report | 5 |
| Honest overlap and disagreements | `verification-output.json` | 8 verified, 0 rejected; complete case records |
| EXISTS/NONE balance | report and `CONNECTIVITY-REPORT.md` | Reported per transport |
| Negative control | six decided false pairings in `selftest()` | Rejected with 6 disagreements |
| No template-only family duplication | distinct constructors/checkers per family | Complete |
| Case-scoped output only | `verified-edges.jsonl` | 141 distinct, 0 self-edges, 0 duplicates |
| Current-state connectivity | `connectivity_impact.py` | Exact analyzer delivered |
| Exact 3,865-node after-count | requires absent live `oracle-math.db` | Explicitly unresolved; no fabricated count |
| Specific remaining bridge gap | `CONNECTIVITY-REPORT.md` | Documented |
