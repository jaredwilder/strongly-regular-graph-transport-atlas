# Strongly Regular Graph Transport Atlas

**Author:** Jared Wilder  
**Canonical public subject home created:** 2026-09-13  
**Status:** recovered mathematical program; exact row-level source recovery still in progress

This repository is the focused public home for a strongly-regular-graph parameter and transport program that was previously buried inside the archive-mining release `mathematics-under-the-wrong-filename`.

The source program was found under the non-mathematical archive name:

```text
graph-bridge-real-delivery.zip
```

That filename is exactly why this work was easy to miss.

## Recovered program scale

The source audit reports:

- **119 strongly regular graph parameter tuples** taken against Brouwer's parameter tables;
- **91 existence entries**;
- **28 nonexistence entries**;
- **141 verified composable transport edges**;
- **8 transport types**;
- **211 typed endpoints**;
- **0 reported disagreements** among the verified composable transports.

This is a mathematical transport atlas, not merely a table scraper: it records when one mathematical object or existence statement can be carried into another object class through a typed construction, and it refuses transports whose source and target propositions are not actually equivalent.

## Strongly regular graph convention

A strongly regular graph with parameters

\[
(v,k,\lambda,\mu)
\]

is a `k`-regular graph on `v` vertices such that:

- every adjacent pair has exactly `lambda` common neighbours;
- every nonadjacent pair has exactly `mu` common neighbours.

The standard feasibility identity is

\[
(v-k-1)\mu=k(k-\lambda-1).
\]

Satisfying the arithmetic feasibility conditions is **not** the same as existence. The atlas deliberately distinguishes parameter feasibility, known existence and known nonexistence.

## Recovered nonexistence examples

The buried source explicitly listed the following among its nonexistence side:

```text
(21,10,4,5)
(28,9,0,4)
(33,16,7,8)
(49,16,3,6)
(50,21,4,12)
(56,22,3,12)
(57,28,13,14)
(64,30,18,10)
(69,34,16,17)
(75,32,10,16)
(76,21,2,7)
(76,30,8,14)
(77,38,18,19)
(93,46,22,23)
(95,40,12,20)
(96,38,10,18)
(96,45,24,18)
```

The source says the full 28-entry nonexistence side also includes complements. Until the exact original row table is recovered, this repository will **not reconstruct the missing rows from memory or inference** and pretend they are the original atlas.

## The transport layer

The second half of the program is a typed relation graph between mathematical object classes.

The recovered source reports:

- **141** verified composable edges;
- **8** distinct transports;
- **211** endpoints;
- **0** disagreements in the composition checks.

The transport machinery matters because many classical equivalences in design theory, coding theory, graph theory and matrix theory are only valid under specific parameter conventions and proposition types. A syntactically plausible bridge is not automatically a theorem.

### A load-bearing negative control

The source explicitly refused to emit a transport of the form

```text
Matrix.IsHadamard  <->  hadamard:n
```

because those labels denote different propositions at different levels of specificity. Treating them as interchangeable would collapse distinct mathematical statements.

That refusal is part of the result. A transport atlas that cannot say **no** is not a trustworthy transport atlas.

See [`TRANSPORT-TYPING.md`](TRANSPORT-TYPING.md).

## What is public here now

This repository currently preserves:

1. the recovered program definition and scale;
2. the known strongly-regular nonexistence examples explicitly printed by the source audit;
3. the exact transport-count / endpoint-count / disagreement-count summary;
4. the proposition-typing integrity rule;
5. the source lineage and recovery debt.

## What is not yet reconstructed here

The following original source assets have not yet been recovered into this focused home:

- the complete 119-row parameter table;
- the exact 91/28 row partition in machine-readable form;
- the complete 141-edge transport table;
- the names and definitions of all eight transport types;
- per-edge verifier receipts / proofs;
- the exact 211-endpoint registry;
- the original source hashes from `graph-bridge-real-delivery.zip`.

Those are source-recovery tasks. Missing rows will not be guessed.

## Authority boundary

The counts and examples above are **source-audit facts recovered from the public archive-mining record**. They are not upgraded here into independent historical novelty claims or fresh proofs of every existence/nonexistence row.

Where an existence or nonexistence entry ultimately depends on an external catalogue or classical theorem, the final recovered atlas should name that dependency explicitly.

## Provenance

Before this focused repository existed, the program was publicly visible only as a buried-program paragraph in:

`jaredwilder/mathematics-under-the-wrong-filename`

That release explains that a filename-based mining pass missed 93 mathematically substantive archives whose names did not look mathematical. `graph-bridge-real-delivery.zip` was one of the characteristic misses.

See [`PROVENANCE.md`](PROVENANCE.md) and [`SOURCE-RECOVERY.md`](SOURCE-RECOVERY.md).

## Current status

**PROGRAM PUBLIC / COMPLETE ATLAS BYTES NOT YET RECOVERED.**

The focused home now exists. The next job is exact source reconstruction, not another summary layer.
