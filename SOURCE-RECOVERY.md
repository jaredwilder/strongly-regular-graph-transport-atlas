# Exact source recovery checklist

The canonical mathematical program is now public. The exact source payload still needs reconstruction.

## Required objects

- [ ] complete 119-row strongly-regular parameter table;
- [ ] exact row-level 91 existence / 28 nonexistence classification;
- [ ] complete 141-edge transport ledger;
- [ ] exact definitions/names of all eight transport types;
- [ ] 211-endpoint registry;
- [ ] rejected/type-mismatched edge ledger;
- [ ] per-edge proof/verifier/citation authority;
- [ ] original source archive/member hashes;
- [ ] replay script for transport composition;
- [ ] Brouwer-table version/date or frozen source reference used by the original atlas.

## Recovery protocol

For each candidate recovered source object:

1. preserve original bytes;
2. compute SHA-256 before normalization;
3. identify source archive and member path;
4. compare counts against `119 / 91 / 28 / 141 / 8 / 211`;
5. run semantic type checks before transport composition;
6. retain rejected edges and conflicts as first-class records;
7. never infer a missing row from complement symmetry unless the source itself records that row or the derived row is explicitly labeled as a new derivation;
8. separate catalogue dependence from independently proved nonexistence/existence;
9. publish a machine-readable manifest and a human-readable atlas together.

## Acceptance gate

The exact recovery is complete only when the reconstructed row/edge payload reproduces the source-level counts and every public summary statement in this repository can be traced to an exact row, proof, verifier, or external dependency.
