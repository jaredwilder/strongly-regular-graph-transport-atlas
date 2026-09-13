# Cover note

## `srg_transports.py`

A standalone replacement for the supplied partial transport file. It implements the doctrine’s PROPOSE/VERIFY separation, constructs graphs and matrices exactly, looks up the opposite endpoint in a curated ground-truth subset or the live facts table, enforces five decided overlaps, preserves complete disagreement evidence, and emits only verified cases.

## `brouwer-ground-truth.json`

A deliberately scoped 119-row receipt set covering exactly the parameter tuples exercised by the verifier. Every record includes a Brouwer table URL and a human-readable row note; the file explicitly disclaims being a full SRG database.

## `verified-edges.jsonl` and `verification-output.json`

The machine outputs of a clean run: 141 distinct edges from eight verified transports, with all 162 decided case comparisons retained in the full report. Six transports are honestly marked one-sided; the conference equivalence and complement involution include substantial NONE controls.

## `independent_check.py`

A second implementation, intentionally not importing the verifier. It independently reconstructs and checks Paley(13), rejects conference order 22 through the sum-of-two-squares obstruction plus Brouwer’s NONE row, and checks the beyond-triple-system `S(2,4,25)` block-graph parameters and edge.

## `connectivity_impact.py`

A read-only analyzer for the live database. It computes the exact number of original blade-bound nodes moved into component `668150`; without the live database it runs a synthetic self-test and makes no movement claim.

## Audit and receipts

`CURRENT-SRG-TRANSPORTS-AUDIT.md` records why the original file is not acceptable. `SELFTEST-RECEIPT.json` and `logs/` preserve the successful replacement checks and the original file’s actual execution failure.
