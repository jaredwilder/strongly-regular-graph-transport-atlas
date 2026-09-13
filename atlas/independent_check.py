#!/usr/bin/env python3
"""Independent spot-check of accepted SRG transport edges.

This checker intentionally does not import srg_transports.py.  It reconstructs
three claims with separate, small arithmetic routines and checks that the exact
case-scoped edges and Brouwer-status receipts are present in the delivery.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def paley_prime_graph(q: int) -> list[set[int]]:
    if q < 2 or any(q % d == 0 for d in range(2, math.isqrt(q) + 1)):
        raise ValueError("this independent checker handles prime q only")
    if q % 4 != 1:
        raise ValueError("q must be 1 mod 4")
    squares = {x * x % q for x in range(1, q)}
    adj = [set() for _ in range(q)]
    for x in range(q):
        for y in range(x + 1, q):
            if (x - y) % q in squares:
                adj[x].add(y)
                adj[y].add(x)
    return adj


def exact_srg_params(adj: list[set[int]]) -> tuple[int, int, int, int]:
    v = len(adj)
    degrees = {len(ns) for ns in adj}
    if len(degrees) != 1:
        raise AssertionError(f"not regular: {degrees}")
    k = degrees.pop()
    lam, mu = set(), set()
    for i in range(v):
        for j in range(i + 1, v):
            common = len(adj[i] & adj[j])
            (lam if j in adj[i] else mu).add(common)
    if len(lam) != 1 or len(mu) != 1:
        raise AssertionError(f"not SRG: lambda={lam}, mu={mu}")
    return v, k, lam.pop(), mu.pop()


def sum_two_squares(n: int) -> bool:
    return any(math.isqrt(n - a * a) ** 2 == n - a * a for a in range(math.isqrt(n) + 1))


def steiner_block_params(m: int, u: int) -> tuple[int, int, int, int]:
    den = m * (m - 1)
    if u * (u - 1) % den:
        raise ValueError("nonintegral block count")
    v = u * (u - 1) // den
    k = m * (u - m) // (m - 1)
    lam = (m - 1) ** 2 + (u - 2 * m + 1) // (m - 1)
    mu = m * m
    return v, k, lam, mu


def main() -> int:
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    ap.add_argument("--ground-truth", default=str(here / "brouwer-ground-truth.json"))
    ap.add_argument("--edges", default=str(here / "verified-edges.jsonl"))
    args = ap.parse_args()

    gt_raw = json.loads(Path(args.ground_truth).read_text(encoding="utf-8"))
    gt = {tuple(r["params"]): r for r in gt_raw["records"]}
    edges = [json.loads(line) for line in Path(args.edges).read_text(encoding="utf-8").splitlines() if line.strip()]
    edge_keys = {(e["from"], e["to"], e["type"], e["rule"]) for e in edges}

    checks: list[tuple[str, bool, str]] = []

    # Positive construction independently recomputed: Paley(13).
    paley_params = exact_srg_params(paley_prime_graph(13))
    expected_paley = (13, 6, 2, 3)
    checks.append(("paley_13_parameters", paley_params == expected_paley, str(paley_params)))
    checks.append(("paley_13_brouwer_exists", gt.get(expected_paley, {}).get("status") == "EXISTS", str(gt.get(expected_paley))))
    checks.append((
        "paley_13_edge_present",
        ("paley:13", "srg:13,6,2,3", "IMPLICATION", "paley-graph-is-conference-srg") in edge_keys,
        "paley:13 -> srg:13,6,2,3",
    ))

    # Negative equivalence control: order 22 conference matrix would require
    # q=21 to be a sum of two squares, and Brouwer records the matching SRG NONE.
    conf_none = (21, 10, 4, 5)
    checks.append(("conference_22_obstruction", not sum_two_squares(21), "21 is not a sum of two squares"))
    checks.append(("conference_22_srg_brouwer_none", gt.get(conf_none, {}).get("status") == "NONE", str(gt.get(conf_none))))
    checks.append((
        "conference_22_none_edge_present",
        ("conference:22", "srg:21,10,4,5", "EQUIVALENCE", "symmetric-conference-iff-conference-srg") in edge_keys,
        "conference:22 <-> srg:21,10,4,5",
    ))

    # Independent parameter substitution for a beyond-STS case.
    steiner_params = steiner_block_params(4, 25)
    expected_steiner = (50, 28, 15, 16)
    checks.append(("steiner_2_4_25_parameters", steiner_params == expected_steiner, str(steiner_params)))
    checks.append(("steiner_2_4_25_brouwer_exists", gt.get(expected_steiner, {}).get("status") == "EXISTS", str(gt.get(expected_steiner))))
    checks.append((
        "steiner_2_4_25_edge_present",
        ("steiner:2,4,25", "srg:50,28,15,16", "IMPLICATION", "steiner-2-design-block-graph-is-srg") in edge_keys,
        "steiner:2,4,25 -> srg:50,28,15,16",
    ))

    ok = all(passed for _, passed, _ in checks)
    for name, passed, detail in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")
    print(json.dumps({"ok": ok, "method": "independent-srg-edge-check", "checks": len(checks)}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
