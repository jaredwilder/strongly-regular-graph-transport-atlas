# Strongly Regular Graph Transport Atlas

**Author:** Jared Wilder  
**Status:** original source package recovered; bundled checks replayed on 2026-09-13.

This repository contains a finite strongly regular graph parameter atlas and typed constructions between graph, design and matrix existence statements. Exact data, transport definitions and checks are available alongside the historical audits.

| Object | Contents |
|---|---|
| [Parameter atlas](atlas/brouwer-ground-truth.json) | 119 distinct `(v,k,lambda,mu)` rows: 91 `EXISTS`, 28 `NONE` |
| [Transport edges](atlas/verified-edges.jsonl) | 141 distinct typed edges, with rule and evidence fields |
| [Transport report](atlas/verification-output.json) | Eight transport definitions; 162 recorded case comparisons and zero recorded disagreements |
| [Endpoint index](data/endpoints.json) | 211 endpoints derived from the actual `from` and `to` fields |
| [Transport implementation](atlas/srg_transports.py) | Case-scoped construction, verification and edge generation |
| [Independent checker](atlas/independent_check.py) | Separate finite checks for selected constructions and edge integrity |

All 25 source files match the recovered archive byte-for-byte. Its original SHA-256 manifest covers 24 files plus the manifest itself.

## Reproduce

Python 3.10 or later; standard library only. From the repository root:

```sh
python verification/verify_release.py
python verification/verify_release.py --replay
```

The first command verifies source hashes, parameter rows, typed edges and endpoints. The second also runs the original transport checker, separate checker and synthetic connectivity self-test without overwriting original source receipts. All three passed in the [2026-09-13 replay](verification/replay-2026-09-13.json).

## Mathematical scope

A strongly regular graph with parameters `(v,k,lambda,mu)` is `k`-regular on `v` vertices, with `lambda` common neighbours for adjacent pairs and `mu` for nonadjacent pairs. Its parameters satisfy `(v-k-1)mu = k(k-lambda-1)`; arithmetic feasibility alone does not establish existence.

The atlas is a specific 119-row subset attributed to Brouwer's tables. Original row references and statuses are preserved. This release does not independently establish every catalogue classification or a new historical novelty claim.

Six of the eight transport checks have only positive cases. The source marks them as one-sided. Successful finite replay is not a universal proof of every transport statement.

The original code audit and replacement package are retained separately. The proposition-type mismatch between `Matrix.IsHadamard` and `hadamard:n` remains documented in [TRANSPORT-TYPING.md](TRANSPORT-TYPING.md).

Live-database connectivity remains unresolved because the original database is absent. The connectivity check replayed here uses a synthetic fixture. An independent frozen catalogue version/date and full external-reference audit remain outstanding.

## Provenance

The program was previously summarized in `jaredwilder/mathematics-under-the-wrong-filename`. Original archive: `graph-bridge-real-delivery.zip`, 51,599 bytes, SHA-256:

```text
35e069de7e386442c17888be88ad6fd0585136a8f8cfc60de071f006997ef914
```

Original members are preserved under [atlas/](atlas/README.md). [Source recovery](verification/source-recovery.json) maps public files to original members, byte sizes and SHA-256 values. [SOURCE-RECOVERY.md](SOURCE-RECOVERY.md) lists completed recovery and remaining authority checks.

The historical `DELIVERY-VALIDATION.json` says 23 manifested files. Direct inspection finds 24 manifest entries and 25 source files. The historical file is preserved unchanged and the discrepancy is recorded explicitly.
