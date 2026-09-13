"""Verified classical transports into strongly-regular-graph parameter nodes.

This file is a contract-clean replacement for the handoff's partial
``reference/srg_transports.py``.  It is deliberately standalone: standard library
only, a bundled exact subset of Brouwer's table, no network access, no LLM calls,
and no dependency on a live repository database.

Verification discipline
-----------------------
Each proposal is checked over every explicitly claimed case.  The two endpoint
statuses are computed independently:

* SRG status: exact lookup in ``brouwer-ground-truth.json``.
* Constructive families: an explicit graph or matrix is built and checked entry
  by entry / pair by pair.
* Symmetric-conference nonexistence controls: the necessary sum-of-two-squares
  condition is computed exactly.
* Steiner 2-design source status for block sizes 3, 4, 5: the exact iff
  congruence theorem quoted in Brouwer--Van Maldeghem, section 8.5.4A.

Only case-scoped edges from a transport with at least MIN_OVERLAP decided cases
and zero disagreements are emitted.  The file never widens a verified sample to
an untested range.
"""
from __future__ import annotations

import argparse
import functools
import itertools
import json
import math
import os
import sqlite3
import sys
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GROUND_TRUTH = os.path.join(HERE, "brouwer-ground-truth.json")
DEFAULT_EDGES = os.path.join(HERE, "verified-edges.jsonl")
DEFAULT_REPORT = os.path.join(HERE, "verification-output.json")
MIN_OVERLAP = 5
DECIDED = {"EXISTS", "NONE"}

BROUWER_INDEX = "https://aeb.win.tue.nl/graphs/srg/srgtab.html"
BROUWER_MONOGRAPH = "https://homepages.cwi.nl/~aeb/math/srg/rk3/srgw.pdf"
CONFERENCE_PAPER = "https://arxiv.org/abs/2004.05829"
MATHLIB_HADAMARD = (
    "https://leanprover-community.github.io/mathlib4_docs/"
    "Mathlib/LinearAlgebra/Matrix/HadamardMatrix.html"
)


# ---------------------------------------------------------------------------
# Ground truth
# ---------------------------------------------------------------------------


def load_ground_truth(path: str = DEFAULT_GROUND_TRUTH) -> dict[tuple[int, int, int, int], dict]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    out: dict[tuple[int, int, int, int], dict] = {}
    for row in data["records"]:
        p = tuple(int(x) for x in row["params"])
        if len(p) != 4:
            raise ValueError(f"bad SRG tuple: {p}")
        status = row["status"]
        if status not in DECIDED | {"OPEN", "UNDECIDED"}:
            raise ValueError(f"bad status {status!r} for {p}")
        if p in out and out[p]["status"] != status:
            raise ValueError(f"conflicting ground truth for {p}")
        out[p] = row
    return out


def load_live_db_srg(path: str) -> dict[tuple[int, int, int, int], dict]:
    """Optional live integration path using the handoff's exact ``facts`` schema."""
    con = sqlite3.connect(path)
    try:
        rows = con.execute(
            "SELECT params,status,source,tier FROM facts WHERE family='srg'"
        ).fetchall()
    finally:
        con.close()
    out = {}
    for params, status, source, tier in rows:
        p = tuple(int(x) for x in params.split(","))
        raw = str(status)
        st = "EXISTS" if raw.startswith("EXISTS") else "NONE" if raw.startswith("NONE") else raw
        out[p] = {
            "params": list(p),
            "status": st,
            "source_url": BROUWER_INDEX if source == "brouwer" else str(source),
            "source_note": f"live facts table; tier={tier}",
        }
    return out


# ---------------------------------------------------------------------------
# Exact finite fields (small prime powers; standard-library only)
# ---------------------------------------------------------------------------


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def prime_power(q: int) -> tuple[int, int] | None:
    if q < 2:
        return None
    if _is_prime(q):
        return q, 1
    for p in range(2, int(math.isqrt(q)) + 1):
        if not _is_prime(p):
            continue
        x, m = q, 0
        while x % p == 0:
            x //= p
            m += 1
        if x == 1 and m >= 2:
            return p, m
    return None


def _poly_trim(a: list[int]) -> list[int]:
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def _poly_mod(dividend: Sequence[int], divisor: Sequence[int], p: int) -> list[int]:
    a = [x % p for x in dividend]
    b = _poly_trim([x % p for x in divisor])
    if not b or b == [0]:
        raise ZeroDivisionError("zero polynomial")
    inv_lead = pow(b[-1], -1, p)
    while len(a) >= len(b) and any(a):
        coeff = a[-1] * inv_lead % p
        shift = len(a) - len(b)
        for i, bi in enumerate(b):
            a[i + shift] = (a[i + shift] - coeff * bi) % p
        _poly_trim(a)
    return _poly_trim(a or [0])


def _monic_polynomials(p: int, degree: int) -> Iterable[list[int]]:
    for lower in itertools.product(range(p), repeat=degree):
        yield list(lower) + [1]


def _is_irreducible(f: Sequence[int], p: int) -> bool:
    degree = len(f) - 1
    if degree <= 0 or f[-1] % p != 1:
        return False
    if f[0] % p == 0:
        return False
    for d in range(1, degree // 2 + 1):
        for g in _monic_polynomials(p, d):
            if _poly_mod(f, g, p) == [0]:
                return False
    return True


@functools.lru_cache(maxsize=None)
def irreducible_polynomial(p: int, degree: int) -> tuple[int, ...]:
    if degree == 1:
        return (0, 1)
    for f in _monic_polynomials(p, degree):
        if _is_irreducible(f, p):
            return tuple(f)
    raise RuntimeError(f"no irreducible polynomial found over GF({p}) of degree {degree}")


class FiniteField:
    """Tiny exact GF(p^m), with elements encoded as base-p coefficient vectors."""

    def __init__(self, q: int):
        pp = prime_power(q)
        if pp is None:
            raise ValueError(f"{q} is not a prime power")
        self.q = q
        self.p, self.m = pp
        self.modulus = irreducible_polynomial(self.p, self.m)

    def decode(self, x: int) -> list[int]:
        if not 0 <= x < self.q:
            raise ValueError(x)
        out = []
        for _ in range(self.m):
            out.append(x % self.p)
            x //= self.p
        return out

    def encode(self, coeffs: Sequence[int]) -> int:
        x = 0
        mul = 1
        for i in range(self.m):
            x += (coeffs[i] % self.p) * mul
            mul *= self.p
        return x

    def add(self, a: int, b: int) -> int:
        aa, bb = self.decode(a), self.decode(b)
        return self.encode([(x + y) % self.p for x, y in zip(aa, bb)])

    def neg(self, a: int) -> int:
        aa = self.decode(a)
        return self.encode([(-x) % self.p for x in aa])

    def sub(self, a: int, b: int) -> int:
        return self.add(a, self.neg(b))

    def mul(self, a: int, b: int) -> int:
        aa, bb = self.decode(a), self.decode(b)
        tmp = [0] * (2 * self.m - 1)
        for i, x in enumerate(aa):
            for j, y in enumerate(bb):
                tmp[i + j] = (tmp[i + j] + x * y) % self.p
        # modulus is f_0 + ... + f_{m-1}x^{m-1} + x^m
        f = self.modulus
        for deg in range(len(tmp) - 1, self.m - 1, -1):
            coeff = tmp[deg] % self.p
            if coeff:
                shift = deg - self.m
                for i in range(self.m):
                    tmp[shift + i] = (tmp[shift + i] - coeff * f[i]) % self.p
        return self.encode(tmp[: self.m])

    def square_set(self) -> set[int]:
        return {self.mul(x, x) for x in range(1, self.q)}


# ---------------------------------------------------------------------------
# Exact graph/matrix checking
# ---------------------------------------------------------------------------

Adjacency = list[set[int]]


def _empty_graph(v: int) -> Adjacency:
    return [set() for _ in range(v)]


def _add_edge(adj: Adjacency, a: int, b: int) -> None:
    if a == b:
        raise ValueError("loop")
    adj[a].add(b)
    adj[b].add(a)


def srg_parameters(adj: Adjacency) -> tuple[int, int, int, int]:
    v = len(adj)
    if v == 0:
        raise ValueError("empty graph")
    for i, ns in enumerate(adj):
        if i in ns:
            raise ValueError("loop")
        if any(j < 0 or j >= v or i not in adj[j] for j in ns):
            raise ValueError("not a simple undirected graph")
    degrees = {len(ns) for ns in adj}
    if len(degrees) != 1:
        raise ValueError(f"not regular: {sorted(degrees)}")
    k = next(iter(degrees))
    lam_values: set[int] = set()
    mu_values: set[int] = set()
    for i in range(v):
        for j in range(i + 1, v):
            common = len(adj[i] & adj[j])
            (lam_values if j in adj[i] else mu_values).add(common)
    if len(lam_values) != 1 or len(mu_values) != 1:
        raise ValueError(
            f"not strongly regular: lambda={sorted(lam_values)}, mu={sorted(mu_values)}"
        )
    return v, k, next(iter(lam_values)), next(iter(mu_values))


def complement_graph(adj: Adjacency) -> Adjacency:
    v = len(adj)
    out = _empty_graph(v)
    for i in range(v):
        for j in range(i + 1, v):
            if j not in adj[i]:
                _add_edge(out, i, j)
    return out


def complement_params(p: Sequence[int]) -> tuple[int, int, int, int]:
    v, k, lam, mu = p
    return v, v - k - 1, v - 2 * k + mu - 2, v - 2 * k + lam


def triangular_graph(n: int) -> Adjacency:
    vertices = list(itertools.combinations(range(n), 2))
    adj = _empty_graph(len(vertices))
    for i, a in enumerate(vertices):
        aa = set(a)
        for j in range(i + 1, len(vertices)):
            if aa.intersection(vertices[j]):
                _add_edge(adj, i, j)
    return adj


def lattice_graph(n: int) -> Adjacency:
    vertices = [(r, c) for r in range(n) for c in range(n)]
    adj = _empty_graph(n * n)
    for i, (r, c) in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            rr, cc = vertices[j]
            if r == rr or c == cc:
                _add_edge(adj, i, j)
    return adj


def latin_square_graph(n: int) -> Adjacency:
    # Cyclic Latin square L(r,c)=r+c mod n; one Latin square plus row/column classes.
    vertices = [(r, c) for r in range(n) for c in range(n)]
    adj = _empty_graph(n * n)
    for i, (r, c) in enumerate(vertices):
        s = (r + c) % n
        for j in range(i + 1, len(vertices)):
            rr, cc = vertices[j]
            if r == rr or c == cc or s == (rr + cc) % n:
                _add_edge(adj, i, j)
    return adj


@functools.lru_cache(maxsize=None)
def paley_graph(q: int) -> tuple[tuple[int, ...], ...]:
    if q % 4 != 1:
        raise ValueError("Paley graph requires q == 1 mod 4")
    field = FiniteField(q)
    squares = field.square_set()
    adj = _empty_graph(q)
    for x in range(q):
        for y in range(x + 1, q):
            if field.sub(x, y) in squares:
                _add_edge(adj, x, y)
    return tuple(tuple(sorted(x)) for x in adj)


def _paley_adj(q: int) -> Adjacency:
    return [set(row) for row in paley_graph(q)]


@functools.lru_cache(maxsize=None)
def paley_conference_matrix(q: int) -> tuple[tuple[int, ...], ...]:
    """Normalized symmetric Paley conference matrix of order q+1."""
    if q % 4 != 1:
        raise ValueError("symmetric Paley conference matrix requires q == 1 mod 4")
    field = FiniteField(q)
    squares = field.square_set()
    n = q + 1
    C = [[0] * n for _ in range(n)]
    for i in range(1, n):
        C[0][i] = C[i][0] = 1
    for x in range(q):
        for y in range(q):
            if x == y:
                continue
            chi = 1 if field.sub(x, y) in squares else -1
            C[x + 1][y + 1] = -chi  # Seidel convention: edge = -1
    return tuple(tuple(row) for row in C)


def verify_conference_matrix(C: Sequence[Sequence[int]]) -> bool:
    n = len(C)
    if n < 2 or any(len(row) != n for row in C):
        return False
    for i in range(n):
        for j in range(n):
            if i == j:
                if C[i][j] != 0:
                    return False
            elif C[i][j] not in (-1, 1) or C[i][j] != C[j][i]:
                return False
    for i in range(n):
        for j in range(n):
            dot = sum(C[i][t] * C[j][t] for t in range(n))
            expected = n - 1 if i == j else 0
            if dot != expected:
                return False
    return True


def graph_from_normalized_conference(C: Sequence[Sequence[int]]) -> Adjacency:
    n = len(C)
    if any(C[0][i] != 1 or C[i][0] != 1 for i in range(1, n)):
        raise ValueError("conference matrix is not normalized")
    adj = _empty_graph(n - 1)
    for i in range(1, n):
        for j in range(i + 1, n):
            if C[i][j] == -1:
                _add_edge(adj, i - 1, j - 1)
    return adj


def hadamard_from_conference(C: Sequence[Sequence[int]]) -> list[list[int]]:
    n = len(C)
    A = [[C[i][j] + (1 if i == j else 0) for j in range(n)] for i in range(n)]
    B = [[C[i][j] - (1 if i == j else 0) for j in range(n)] for i in range(n)]
    H = []
    for i in range(n):
        H.append(A[i] + B[i])
    for i in range(n):
        H.append(B[i] + [-x for x in A[i]])
    return H


def verify_hadamard(H: Sequence[Sequence[int]]) -> bool:
    n = len(H)
    if n == 0 or any(len(row) != n for row in H):
        return False
    if any(x not in (-1, 1) for row in H for x in row):
        return False
    for i in range(n):
        for j in range(i, n):
            dot = sum(H[i][t] * H[j][t] for t in range(n))
            if dot != (n if i == j else 0):
                return False
    return True


def is_sum_of_two_squares(n: int) -> bool:
    for a in range(math.isqrt(n) + 1):
        b2 = n - a * a
        b = math.isqrt(b2)
        if b * b == b2:
            return True
    return False


# ---------------------------------------------------------------------------
# Proposal / verification layer
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Endpoint:
    node: str
    status: str
    evidence: str


@dataclass(frozen=True)
class Case:
    key: str
    left: Callable[[dict], Endpoint]
    right: Callable[[dict], Endpoint]


@dataclass(frozen=True)
class Proposal:
    name: str
    edge_type: str
    tier: str
    receipt: str
    cases: tuple[Case, ...]


def _srg_node(p: Sequence[int]) -> str:
    return "srg:" + ",".join(str(x) for x in p)


def _table_endpoint(gt: dict, p: Sequence[int]) -> Endpoint:
    row = gt.get(tuple(p))
    if row is None:
        return Endpoint(_srg_node(p), "UNDECIDED", "not present in bundled exact subset")
    return Endpoint(
        _srg_node(p),
        row["status"],
        f"{row['source_url']} :: {row['source_note']}",
    )


def _constructed_graph_endpoint(node: str, builder: Callable[[], Adjacency], expected: tuple[int, int, int, int]) -> Endpoint:
    actual = srg_parameters(builder())
    status = "EXISTS" if actual == expected else "NONE"
    return Endpoint(node, status, f"explicit graph check: actual SRG parameters {actual}")


def conference_status(q: int) -> Endpoint:
    node = f"conference:{q + 1}"
    if q % 4 != 1:
        return Endpoint(node, "NONE", "order is not 2 mod 4")
    pp = prime_power(q)
    if pp is not None:
        C = paley_conference_matrix(q)
        ok = verify_conference_matrix(C)
        return Endpoint(
            node,
            "EXISTS" if ok else "NONE",
            f"explicit Paley conference matrix over GF({q}); C*C^T={q}I checked exactly",
        )
    if not is_sum_of_two_squares(q):
        return Endpoint(
            node,
            "NONE",
            f"exact obstruction: {q} is not a sum of two squares",
        )
    return Endpoint(node, "UNDECIDED", "no bundled construction or impossibility proof")


def hadamard_from_conference_status(q: int) -> Endpoint:
    node = f"hadamard:{2 * (q + 1)}"
    left = conference_status(q)
    if left.status != "EXISTS":
        return Endpoint(node, "UNDECIDED", "construction not run because source conference matrix is absent/undecided")
    C = paley_conference_matrix(q)
    H = hadamard_from_conference(C)
    ok = verify_hadamard(H)
    return Endpoint(
        node,
        "EXISTS" if ok else "NONE",
        f"explicit 2x2 block construction from conference order {q+1}; HH^T={2*(q+1)}I checked",
    )


def steiner_2_status(m: int, u: int) -> Endpoint:
    node = f"steiner:2,{m},{u}"
    if m not in (3, 4, 5):
        return Endpoint(node, "UNDECIDED", "bundled exact iff theorem only covers block sizes 3,4,5")
    modulus = m * (m - 1)
    exists = u % modulus in (1, m)
    return Endpoint(
        node,
        "EXISTS" if exists else "NONE",
        f"Brouwer--Van Maldeghem 8.5.4A: S(2,{m},u) exists iff u == 1 or {m} mod {modulus}",
    )


def steiner_block_params(m: int, u: int) -> tuple[int, int, int, int]:
    den = m * (m - 1)
    if u * (u - 1) % den:
        raise ValueError("nonintegral number of blocks")
    if (u - m) % (m - 1) or (u - 2 * m + 1) % (m - 1):
        raise ValueError("nonintegral block-graph parameters")
    return (
        u * (u - 1) // den,
        m * (u - m) // (m - 1),
        (m - 1) ** 2 + (u - 2 * m + 1) // (m - 1),
        m * m,
    )


PALEY_Q = (5, 9, 13, 17, 25, 29, 37, 41, 49, 53, 61, 73, 81, 89, 97)
CONFERENCE_NONE_Q = (21, 33, 57, 69, 77, 93)
TRIANGULAR_N = tuple(range(5, 15))
LATTICE_N = tuple(range(3, 11))
LATIN_N = tuple(range(4, 11))
STEINER_CASES = (
    (3, 13), (3, 15), (3, 19), (3, 21), (3, 25), (3, 27), (3, 31), (3, 33),
    (4, 25), (4, 28), (4, 37), (4, 40), (4, 49),
    (5, 41), (5, 45), (5, 61),
)


def make_proposals(gt: dict) -> tuple[Proposal, ...]:
    # Complement cases use every exact pair for which both endpoints are present.
    seen_pairs: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    complement_cases = []
    for p in sorted(gt):
        c = complement_params(p)
        if c not in gt:
            continue
        keypair = tuple(sorted((tuple(p), tuple(c))))
        if keypair in seen_pairs:
            continue
        seen_pairs.add(keypair)
        complement_cases.append(
            Case(
                key=str(p),
                left=lambda data, p=p: _table_endpoint(data, p),
                right=lambda data, c=c: _table_endpoint(data, c),
            )
        )

    conference_cases = []
    for q in PALEY_Q + CONFERENCE_NONE_Q:
        p = (q, (q - 1) // 2, (q - 5) // 4, (q - 1) // 4)
        conference_cases.append(
            Case(
                key=f"q={q}",
                left=lambda _data, q=q: conference_status(q),
                right=lambda data, p=p: _table_endpoint(data, p),
            )
        )

    paley_cases = []
    for q in PALEY_Q:
        p = (q, (q - 1) // 2, (q - 5) // 4, (q - 1) // 4)
        paley_cases.append(
            Case(
                key=f"q={q}",
                left=lambda _data, q=q, p=p: _constructed_graph_endpoint(
                    f"paley:{q}", lambda: _paley_adj(q), p
                ),
                right=lambda data, p=p: _table_endpoint(data, p),
            )
        )

    conf_hadamard_cases = []
    for q in PALEY_Q:
        conf_hadamard_cases.append(
            Case(
                key=f"q={q}",
                left=lambda _data, q=q: conference_status(q),
                right=lambda _data, q=q: hadamard_from_conference_status(q),
            )
        )

    triangular_cases = []
    for n in TRIANGULAR_N:
        p = (n * (n - 1) // 2, 2 * (n - 2), n - 2, 4)
        triangular_cases.append(
            Case(
                key=f"n={n}",
                left=lambda _data, n=n, p=p: _constructed_graph_endpoint(
                    f"triangular:{n}", lambda: triangular_graph(n), p
                ),
                right=lambda data, p=p: _table_endpoint(data, p),
            )
        )

    lattice_cases = []
    for n in LATTICE_N:
        p = (n * n, 2 * (n - 1), n - 2, 2)
        lattice_cases.append(
            Case(
                key=f"n={n}",
                left=lambda _data, n=n, p=p: _constructed_graph_endpoint(
                    f"lattice:{n}", lambda: lattice_graph(n), p
                ),
                right=lambda data, p=p: _table_endpoint(data, p),
            )
        )

    latin_cases = []
    for n in LATIN_N:
        p = (n * n, 3 * (n - 1), n, 6)
        latin_cases.append(
            Case(
                key=f"n={n}",
                left=lambda _data, n=n, p=p: _constructed_graph_endpoint(
                    f"latin-square:{n}", lambda: latin_square_graph(n), p
                ),
                right=lambda data, p=p: _table_endpoint(data, p),
            )
        )

    steiner_cases = []
    for m, u in STEINER_CASES:
        p = steiner_block_params(m, u)
        steiner_cases.append(
            Case(
                key=f"m={m},u={u}",
                left=lambda _data, m=m, u=u: steiner_2_status(m, u),
                right=lambda data, p=p: _table_endpoint(data, p),
            )
        )

    return (
        Proposal(
            "srg-complement",
            "EQUIVALENCE",
            "published-proof",
            "Classical SRG complement involution; parameters re-derived algebraically and cross-checked against Brouwer rows.",
            tuple(complement_cases),
        ),
        Proposal(
            "symmetric-conference-iff-conference-srg",
            "EQUIVALENCE",
            "published-proof",
            "Haemers--Parsaei Majd, Spectral symmetry in conference matrices, section 2: symmetric conference order 4m+2 iff SRG(4m+1,2m,m-1,m).",
            tuple(conference_cases),
        ),
        Proposal(
            "paley-graph-is-conference-srg",
            "IMPLICATION",
            "published-proof",
            "Paley construction over GF(q), q prime power and q=1 mod 4; graph is built and its exact SRG parameters are recomputed.",
            tuple(paley_cases),
        ),
        Proposal(
            "symmetric-conference-gives-hadamard-double-order",
            "IMPLICATION",
            "published-proof",
            "Block construction H=[[C+I,C-I],[C-I,-C-I]]; entries and HH^T=2nI are checked exactly.",
            tuple(conf_hadamard_cases),
        ),
        Proposal(
            "triangular-line-graph-is-srg",
            "IMPLICATION",
            "published-proof",
            "Line graph of K_n; explicit graph construction and exact common-neighbour count.",
            tuple(triangular_cases),
        ),
        Proposal(
            "lattice-rook-graph-is-srg",
            "IMPLICATION",
            "published-proof",
            "Rook graph on an n by n grid; explicit graph construction and exact common-neighbour count.",
            tuple(lattice_cases),
        ),
        Proposal(
            "cyclic-latin-square-graph-is-srg",
            "IMPLICATION",
            "published-proof",
            "Graph from rows, columns, and symbols of L(r,c)=r+c mod n; constructed and checked exactly.",
            tuple(latin_cases),
        ),
        Proposal(
            "steiner-2-design-block-graph-is-srg",
            "IMPLICATION",
            "published-proof",
            "Brouwer--Van Maldeghem, Strongly regular graphs, section 8.5.4A; includes block sizes 3,4,5 and extends the handoff beyond STS-only cases.",
            tuple(steiner_cases),
        ),
    )


def verify_proposal(proposal: Proposal, gt: dict) -> dict:
    agreements = []
    disagreements = []
    undecided = []
    left_exists = 0
    left_none = 0
    for case in proposal.cases:
        try:
            left = case.left(gt)
            right = case.right(gt)
        except Exception as exc:  # a computation failure is evidence, never silently skipped
            disagreements.append(
                {
                    "case": case.key,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        row = {
            "case": case.key,
            "left": {"node": left.node, "status": left.status, "evidence": left.evidence},
            "right": {"node": right.node, "status": right.status, "evidence": right.evidence},
        }
        if left.status not in DECIDED or right.status not in DECIDED:
            undecided.append(row)
            continue
        if left.status == "EXISTS":
            left_exists += 1
        else:
            left_none += 1
        bad = (
            left.status != right.status
            if proposal.edge_type == "EQUIVALENCE"
            else left.status == "EXISTS" and right.status == "NONE"
        )
        (disagreements if bad else agreements).append(row)
    overlap = len(agreements) + len(disagreements)
    verified = overlap >= MIN_OVERLAP and not disagreements
    return {
        "name": proposal.name,
        "type": proposal.edge_type,
        "tier": proposal.tier,
        "receipt": proposal.receipt,
        "verified": verified,
        "overlap": overlap,
        "exists": left_exists,
        "none": left_none,
        "oneSided": left_exists == 0 or left_none == 0,
        "agreements": agreements,
        "disagreements": disagreements,
        "undecided": undecided,
        "reason": (
            "verified"
            if verified
            else f"only {overlap} decided overlaps; need {MIN_OVERLAP}"
            if overlap < MIN_OVERLAP
            else f"{len(disagreements)} disagreement(s)"
        ),
    }


def verify_all(gt: dict) -> dict:
    proposals = make_proposals(gt)
    results = [verify_proposal(p, gt) for p in proposals]
    return {
        "kind": "srg-transport-verification",
        "minOverlap": MIN_OVERLAP,
        "groundTruthRecords": len(gt),
        "sources": {
            "brouwerTable": BROUWER_INDEX,
            "brouwerMonograph": BROUWER_MONOGRAPH,
            "conferencePaper": CONFERENCE_PAPER,
            "mathlibHadamardDefinition": MATHLIB_HADAMARD,
        },
        "transports": results,
        "verifiedCount": sum(1 for r in results if r["verified"]),
        "rejectedCount": sum(1 for r in results if not r["verified"]),
    }


def build_edges(report: dict) -> list[dict]:
    edges = []
    seen = set()
    for result in report["transports"]:
        if not result["verified"]:
            continue
        for row in result["agreements"]:
            left = row["left"]["node"]
            right = row["right"]["node"]
            if left == right:
                continue
            key = (left, right, result["type"], result["name"])
            if key in seen:
                continue
            seen.add(key)
            edges.append(
                {
                    "from": left,
                    "to": right,
                    "type": result["type"],
                    "tier": result["tier"],
                    "source": "srg-transports-verified",
                    "rule": result["name"],
                    "receipt": result["receipt"],
                    "verified_case": row["case"],
                }
            )
    return edges


def write_outputs(report: dict, edges: list[dict], report_path: str, edge_path: str) -> None:
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")
    with open(edge_path, "w", encoding="utf-8") as fh:
        for edge in edges:
            fh.write(json.dumps(edge, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------
# Self-test: deterministic and independent of the live repository
# ---------------------------------------------------------------------------


def selftest() -> tuple[bool, list[tuple[str, bool]]]:
    gt = load_ground_truth()
    checks: list[tuple[str, bool]] = []

    f9 = FiniteField(9)
    nonzero_products = {f9.mul(a, b) for a in range(1, 9) for b in range(1, 9)}
    checks.append(("gf9_nonzero_closed", 0 not in nonzero_products))
    checks.append(("gf9_distributive_sample", all(
        f9.mul(a, f9.add(b, c)) == f9.add(f9.mul(a, b), f9.mul(a, c))
        for a in range(9) for b in range(9) for c in range(9)
    )))

    checks.append(("paley_9_exact", srg_parameters(_paley_adj(9)) == (9, 4, 1, 2)))
    checks.append(("paley_13_exact", srg_parameters(_paley_adj(13)) == (13, 6, 2, 3)))

    C = paley_conference_matrix(5)
    checks.append(("conference_6_exact", verify_conference_matrix(C)))
    checks.append(("conference_6_to_srg_5", srg_parameters(graph_from_normalized_conference(C)) == (5, 2, 0, 1)))
    checks.append(("conference_22_refuted_by_sum_two_squares", not is_sum_of_two_squares(21)))

    H = hadamard_from_conference(C)
    checks.append(("conference_6_to_hadamard_12", verify_hadamard(H) and len(H) == 12))

    checks.append(("triangular_T5_exact", srg_parameters(triangular_graph(5)) == (10, 6, 3, 4)))
    checks.append(("lattice_L4_exact", srg_parameters(lattice_graph(4)) == (16, 6, 2, 2)))
    checks.append(("latin_square_LS4_exact", srg_parameters(latin_square_graph(4)) == (16, 9, 4, 6)))

    pet = triangular_graph(5)
    checks.append(("complement_formula_exact", srg_parameters(complement_graph(pet)) == complement_params((10, 6, 3, 4))))
    checks.append(("steiner_S2425_formula", steiner_block_params(4, 25) == (50, 28, 15, 16)))
    checks.append(("minimum_overlap_is_five", MIN_OVERLAP == 5))

    report = verify_all(gt)
    checks.append(("all_proposed_transports_verify", report["rejectedCount"] == 0))
    checks.append(("conference_verification_is_balanced", next(
        r for r in report["transports"] if r["name"] == "symmetric-conference-iff-conference-srg"
    )["none"] >= 5))

    # Deliberately false map with six *decided* contradictions: each explicit
    # Paley graph EXISTS, while the paired Brouwer tuple is known NONE.  This
    # proves the verifier rejects a false transport because of disagreements,
    # not merely because one side was absent from the bundled table.
    known_none = [
        (21, 10, 4, 5),
        (33, 16, 7, 8),
        (49, 16, 3, 6),
        (57, 28, 13, 14),
        (69, 34, 16, 17),
        (77, 38, 18, 19),
    ]
    bogus_cases = []
    for q, impossible in zip(PALEY_Q[:6], known_none):
        correct = (q, (q - 1) // 2, (q - 5) // 4, (q - 1) // 4)
        bogus_cases.append(Case(
            key=f"paley-q={q}-versus-none={impossible}",
            left=lambda _data, q=q, correct=correct: _constructed_graph_endpoint(
                f"paley:{q}", lambda: _paley_adj(q), correct
            ),
            right=lambda data, impossible=impossible: _table_endpoint(data, impossible),
        ))
    bogus = Proposal("bogus-paley-to-known-none", "EQUIVALENCE", "none", "negative control", tuple(bogus_cases))
    bogus_result = verify_proposal(bogus, gt)
    checks.append(("false_transport_refused", not bogus_result["verified"]))
    checks.append(("false_transport_has_six_disagreements", len(bogus_result["disagreements"]) == 6))

    return all(ok for _, ok in checks), checks


def _print_human(report: dict, edges: list[dict]) -> None:
    print(f"ground-truth records: {report['groundTruthRecords']}")
    print(f"MIN_OVERLAP: {report['minOverlap']}")
    for r in report["transports"]:
        mark = "VERIFIED" if r["verified"] else "REJECTED"
        sided = " [ONE-SIDED]" if r["oneSided"] else ""
        print(
            f"[{mark}] {r['name']}: overlap={r['overlap']} "
            f"({r['exists']} EXISTS/{r['none']} NONE), "
            f"disagreements={len(r['disagreements'])}{sided}"
        )
    print(f"edges emitted: {len(edges)}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ground-truth", default=DEFAULT_GROUND_TRUTH)
    parser.add_argument("--live-db", help="optional live oracle-math.db; replaces bundled SRG statuses")
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--edges", default=DEFAULT_EDGES)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    ok, checks = selftest()
    for name, passed in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    if not ok:
        print(json.dumps({"ok": False, "method": "srg-transports-verified-selftest", "checks": checks}))
        return 1

    gt = load_live_db_srg(args.live_db) if args.live_db else load_ground_truth(args.ground_truth)
    report = verify_all(gt)
    edges = build_edges(report)
    report["edgeCount"] = len(edges)
    if not args.no_write:
        write_outputs(report, edges, args.report, args.edges)
    _print_human(report, edges)

    final_ok = report["rejectedCount"] == 0
    print(json.dumps({
        "ok": final_ok,
        "method": "srg-transports-verified",
        "verified": report["verifiedCount"],
        "rejected": report["rejectedCount"],
        "edges": len(edges),
    }, sort_keys=True))
    return 0 if final_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
