# Transport typing and integrity rules

A transport edge is not accepted merely because two objects are traditionally associated or because their names look equivalent.

## Core rule

Every edge must preserve the **actual proposition being asserted**.

At minimum a transport record should identify:

- source object type;
- source proposition;
- source parameters and convention;
- target object type;
- target proposition;
- target parameters and convention;
- direction: implication or equivalence;
- hypotheses required by the construction;
- proof / verifier / external citation authority;
- whether the edge composes with another edge under those exact types.

## Negative control preserved from the source

The recovered program explicitly refused to emit

```text
Matrix.IsHadamard <-> hadamard:n
```

because a proposition about a specific matrix satisfying a Hadamard property is not the same proposition as the existence of a Hadamard object of an order `n`.

A valid bridge may connect such propositions after supplying the missing existential/object witness map, but they must not be collapsed by label equality.

## Composition law

For edges

```text
A --T1--> B
B --T2--> C
```

composition is legal only when the target proposition/type of `T1` is semantically identical to the source proposition/type required by `T2`, including parameter normalization.

The source audit reports **141 verified composable edges across eight transports, with zero disagreements**. The exact edge ledger and transport definitions still require source recovery.

## Failure states that must remain visible

A reconstructed atlas should distinguish at least:

- `VERIFIED` — construction/proof checked under the stated types;
- `EXTERNAL` — supported by an external theorem/catalogue, dependency named;
- `PARAMETER_ONLY` — arithmetic parameters map, but existence has not been transported;
- `TYPE_MISMATCH` — apparent bridge rejected because propositions differ;
- `HYPOTHESIS_MISSING` — target would require an unstated condition;
- `DIRECTION_ONLY` — implication exists but converse is not justified;
- `QUARANTINED` — source record is ambiguous or conflicts with another record.

The rejected-edge ledger is mathematically useful: it prevents later mining rounds from reintroducing the same semantic error.
