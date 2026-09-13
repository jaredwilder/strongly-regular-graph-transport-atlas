# Source and receipt map

Every external citation used by the verifier is a resolvable primary or authoritative source.

## Brouwer strongly regular graph tables

- Index: https://aeb.win.tue.nl/graphs/srg/srgtab.html
- Orders 1–50: https://aeb.win.tue.nl/graphs/srg/srgtab1-50.html
- Orders 51–100: https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html
- Orders 101–150: https://aeb.win.tue.nl/graphs/srg/srgtab101-150.html
- Orders 151–200: https://aeb.win.tue.nl/graphs/srg/srgtab151-200.html

`brouwer-ground-truth.json` contains only the exact 119 rows used by this verifier. It is deliberately labeled a subset and is not represented as a replacement for Brouwer’s full database.

## Symmetric conference matrices and conference SRGs

- W. H. Haemers and S. M. Parsaie Majd, *Spectral symmetry in conference matrices*, arXiv:2004.05829: https://arxiv.org/abs/2004.05829

The verifier uses the exact relation between a symmetric conference matrix of order `4m+2` and an SRG with parameters `(4m+1, 2m, m-1, m)`. Positive cases are independently built via Paley matrices; negative controls use the exact sum-of-two-squares obstruction and are cross-checked against Brouwer rows.

## Steiner 2-design block graphs

- A. E. Brouwer and H. Van Maldeghem, *Strongly Regular Graphs*, section 8.5.4A: https://homepages.cwi.nl/~aeb/math/srg/rk3/srgw.pdf

The verifier substitutes the published block-graph parameter formula and the stated existence congruences for Steiner 2-designs with block sizes 3, 4, and 5, then checks each resulting SRG tuple against Brouwer’s table.

## Mathlib Hadamard definitions — gap audit only

- `Mathlib.LinearAlgebra.Matrix.HadamardMatrix`: https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Matrix/HadamardMatrix.html

This source is **not** used to claim a kernel bridge. It confirms that Mathlib has the generic `Matrix.IsHadamard` predicate and related theorems, but the handoff graph’s parameter node `hadamard:n` is not automatically equivalent to a generic declaration-head node. No such unsafe edge is emitted.
