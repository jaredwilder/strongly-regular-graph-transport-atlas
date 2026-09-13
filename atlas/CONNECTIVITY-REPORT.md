# Connectivity impact report

## Supplied before-state

The handoff snapshot reports:

- 669,153 graph nodes
- 7,408,220 edges
- 73,937 connected components
- giant component `668150` with 524,266 nodes
- 3,865 blade-bound nodes
- 0 blade-bound nodes in the giant component

## What this delivery proves

The verifier emits **141 distinct, case-scoped composable edges** across 8 accepted transports:

| Transport | Type | Overlap | EXISTS / NONE | Disagreements | Emitted edges |
|---|---:|---:|---:|---:|---:|
| SRG complement | equivalence | 70 | 53 / 17 | 0 | 49 |
| symmetric conference ↔ conference SRG | equivalence | 21 | 15 / 6 | 0 | 21 |
| Paley graph → conference SRG | implication | 15 | 15 / 0 | 0 | 15 |
| symmetric conference → doubled Hadamard | implication | 15 | 15 / 0 | 0 | 15 |
| triangular graph → SRG | implication | 10 | 10 / 0 | 0 | 10 |
| lattice graph → SRG | implication | 8 | 8 / 0 | 0 | 8 |
| cyclic Latin-square graph → SRG | implication | 7 | 7 / 0 | 0 | 7 |
| Steiner 2-design block graph → SRG | implication | 16 | 16 / 0 | 0 | 16 |

The edge set has 211 distinct endpoints, including all 119 bundled SRG tuples. Fourteen endpoint labels appear explicitly among the handoff snapshot’s samples, touching sampled nodes in SRG components `135185`, `668209`, and `668272`. This proves the transports touch real blade-bearing SRG islands; it does **not** prove that those components join the giant continent.

## Exact after-state: deliberately not fabricated

The handoff does not contain `oracle-math.db` or a complete node-label-to-component mapping. The aggregate snapshot is insufficient to determine whether any existing `conference:*`, `hadamard:*`, `steiner:*`, or other endpoint is already connected to component `668150`, and therefore it is insufficient to calculate the exact number of blade nodes moved.

Accordingly, this package reports the exact after-state as **not computable from the supplied files**, rather than claiming either zero or a positive merge. Run:

```bash
python connectivity_impact.py \
  --db /path/to/evidence/oracle-math.db \
  --edges verified-edges.jsonl \
  --giant-component 668150 \
  --output connectivity-live.json
```

The analyzer is read-only. It unions the existing components through the proposed composable edges, then reports the exact blade count before/after, original components merged, component sizes merged, missing/new endpoint labels, and the movement count among the original blade-bound nodes.

## What is still missing for a kernel-continent bridge

1. The live database must be supplied to compute the exact component impact.
2. At least one accepted path must terminate at an existing node already in component `668150`.
3. A parameter-safe formal bridge is still absent. In particular, the generic Mathlib declaration `Matrix.IsHadamard` is not by itself equivalent to a concrete existence node `hadamard:n`; emitting that edge would collapse distinct propositions and poison the graph.
4. The strongest next bridge would be a Lean theorem or another exact, parameterized database identity connecting a concrete `hadamard:n`, `conference:n`, `steiner:t,k,v`, or `srg:v,k,lambda,mu` existence proposition to an existing giant-component declaration/OEIS node.
