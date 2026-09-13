#!/usr/bin/env python3
"""Compute exact graph/blade connectivity impact of proposed transport edges.

The handoff contains only aggregate component counts, not the complete label ->
component map, so exact before/after movement cannot be reconstructed from the
snapshot alone.  Run this non-mutating analyzer against the live
``evidence/oracle-math.db``.  It treats EQUIVALENCE and IMPLICATION edges as
weak connectivity links, matching connected-component accounting.

With no ``--db`` argument, the module runs a deterministic synthetic selftest so
it remains compatible with the repository's run_selftests.py convention.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path
from typing import Hashable

COMPOSABLE = {"EQUIVALENCE", "IMPLICATION"}
HERE = Path(__file__).resolve().parent
DEFAULT_EDGES = HERE / "verified-edges.jsonl"


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[Hashable, Hashable] = {}
        self.rank: dict[Hashable, int] = {}

    def add(self, x: Hashable) -> None:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x: Hashable) -> Hashable:
        self.add(x)
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: Hashable, b: Hashable) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


def read_edges(path: str | Path) -> list[dict]:
    rows = []
    for lineno, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("type") not in COMPOSABLE:
            continue
        if not isinstance(row.get("from"), str) or not isinstance(row.get("to"), str):
            raise ValueError(f"bad edge endpoints on line {lineno}")
        rows.append(row)
    return rows


def _require_schema(con: sqlite3.Connection) -> None:
    required = {"nodes", "components", "node_blade"}
    present = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    missing = required - present
    if missing:
        raise ValueError(f"database is missing required tables: {sorted(missing)}")


def analyze(db_path: str | Path, edge_path: str | Path, giant_component: int) -> dict:
    edges = read_edges(edge_path)
    con = sqlite3.connect(f"file:{Path(db_path).resolve()}?mode=ro", uri=True)
    try:
        _require_schema(con)
        node_rows = con.execute("SELECT id,label,component FROM nodes").fetchall()
        label_to_component = {str(label): int(component) for _id, label, component in node_rows}
        all_components = {int(component) for _id, _label, component in node_rows}
        if giant_component not in all_components:
            raise ValueError(f"giant component {giant_component} is absent")

        blade_rows = con.execute(
            "SELECT DISTINCT n.id,n.label,n.component "
            "FROM nodes n JOIN node_blade nb ON nb.node=n.id"
        ).fetchall()
        component_sizes = {
            int(c): int(size) for c, size in con.execute("SELECT component,size FROM components")
        }
    finally:
        con.close()

    uf = UnionFind()
    component_token = lambda c: ("component", int(c))
    new_token = lambda label: ("new-node", str(label))
    for c in all_components:
        uf.add(component_token(c))

    endpoint_labels = set()
    existing_endpoint_components = set()
    missing_endpoint_labels = set()
    for edge in edges:
        a_label, b_label = edge["from"], edge["to"]
        endpoint_labels.update((a_label, b_label))
        a = component_token(label_to_component[a_label]) if a_label in label_to_component else new_token(a_label)
        b = component_token(label_to_component[b_label]) if b_label in label_to_component else new_token(b_label)
        if a_label in label_to_component:
            existing_endpoint_components.add(label_to_component[a_label])
        else:
            missing_endpoint_labels.add(a_label)
        if b_label in label_to_component:
            existing_endpoint_components.add(label_to_component[b_label])
        else:
            missing_endpoint_labels.add(b_label)
        uf.union(a, b)

    giant_root = uf.find(component_token(giant_component))
    before_ids = {int(node_id) for node_id, _label, comp in blade_rows if int(comp) == giant_component}
    after_rows = [
        (int(node_id), str(label), int(comp))
        for node_id, label, comp in blade_rows
        if uf.find(component_token(int(comp))) == giant_root
    ]
    after_ids = {node_id for node_id, _label, _comp in after_rows}
    moved_rows = [row for row in after_rows if row[0] not in before_ids]
    moved_by_component = Counter(comp for _id, _label, comp in moved_rows)

    merged_existing_components = sorted(
        c for c in all_components
        if c != giant_component and uf.find(component_token(c)) == giant_root
    )
    touched_blade_rows = [
        (int(node_id), str(label), int(comp))
        for node_id, label, comp in blade_rows
        if int(comp) in existing_endpoint_components
    ]
    new_connected_to_giant = sorted(
        label for label in missing_endpoint_labels
        if uf.find(new_token(label)) == giant_root
    )

    return {
        "kind": "transport-connectivity-impact",
        "exact": True,
        "database": str(Path(db_path).resolve()),
        "edgeFile": str(Path(edge_path).resolve()),
        "giantComponent": giant_component,
        "proposedComposableEdges": len(edges),
        "distinctEndpointLabels": len(endpoint_labels),
        "existingEndpointLabels": len(endpoint_labels - missing_endpoint_labels),
        "newEndpointLabels": len(missing_endpoint_labels),
        "originalBladeBoundNodes": len(blade_rows),
        "bladeNodesInGiantBefore": len(before_ids),
        "bladeNodesInGiantAfter": len(after_ids),
        "bladeNodesMovedIntoGiant": len(after_ids - before_ids),
        "movedByOriginalComponent": dict(sorted(moved_by_component.items())),
        "existingComponentsMergedIntoGiant": merged_existing_components,
        "existingNodesMergedIntoGiant": sum(component_sizes.get(c, 0) for c in merged_existing_components),
        "newTransportNodesConnectedToGiant": new_connected_to_giant,
        "bladeNodesInComponentsTouchedByEdges": len(touched_blade_rows),
        "touchedBladeComponents": sorted({comp for _id, _label, comp in touched_blade_rows}),
        "missingEndpointLabelsSample": sorted(missing_endpoint_labels)[:30],
    }


def _make_fixture(db: Path, edges: Path) -> None:
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE nodes(id INTEGER PRIMARY KEY, label TEXT UNIQUE, ns TEXT, component INTEGER, degree INTEGER DEFAULT 0);
        CREATE TABLE components(component INTEGER PRIMARY KEY, size INTEGER);
        CREATE TABLE node_blade(node INTEGER, blade_id TEXT);
        INSERT INTO nodes(id,label,component) VALUES
          (1,'decl:giant',100),
          (2,'srg:5,2,0,1',200),
          (3,'srg:13,6,2,3',300),
          (4,'unrelated',400);
        INSERT INTO components(component,size) VALUES (100,10),(200,3),(300,4),(400,1);
        INSERT INTO node_blade(node,blade_id) VALUES (2,'b1'),(3,'b2');
        """
    )
    con.commit()
    con.close()
    rows = [
        {"from": "decl:giant", "to": "conference:6", "type": "IMPLICATION"},
        {"from": "conference:6", "to": "srg:5,2,0,1", "type": "EQUIVALENCE"},
        {"from": "srg:5,2,0,1", "to": "srg:13,6,2,3", "type": "EQUIVALENCE"},
        {"from": "ignored", "to": "unrelated", "type": "ANALOGY"},
    ]
    edges.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def selftest() -> tuple[bool, list[tuple[str, bool]]]:
    with tempfile.TemporaryDirectory() as td:
        db, edges = Path(td) / "fixture.db", Path(td) / "edges.jsonl"
        _make_fixture(db, edges)
        r = analyze(db, edges, 100)
    checks = [
        ("two_blades_move", r["bladeNodesMovedIntoGiant"] == 2),
        ("two_components_merge", r["existingComponentsMergedIntoGiant"] == [200, 300]),
        ("analogy_not_composable", 400 not in r["existingComponentsMergedIntoGiant"]),
        ("new_bridge_node_counted", r["newTransportNodesConnectedToGiant"] == ["conference:6"]),
        ("original_blade_count", r["originalBladeBoundNodes"] == 2),
    ]
    return all(ok for _, ok in checks), checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", help="path to live oracle-math.db; omitted => run selftest")
    ap.add_argument("--edges", default=str(DEFAULT_EDGES))
    ap.add_argument("--giant-component", type=int, default=668150)
    ap.add_argument("--output", help="optional JSON output path")
    args = ap.parse_args()

    if not args.db:
        ok, checks = selftest()
        for name, passed in checks:
            print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        print(json.dumps({"ok": ok, "method": "connectivity-impact-selftest", "checks": len(checks)}))
        return 0 if ok else 1

    report = analyze(args.db, args.edges, args.giant_component)
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"blade nodes in giant: {report['bladeNodesInGiantBefore']} -> {report['bladeNodesInGiantAfter']}")
    print(f"blade nodes moved: {report['bladeNodesMovedIntoGiant']}")
    print(f"existing components merged: {len(report['existingComponentsMergedIntoGiant'])}")
    print(json.dumps({"ok": True, "method": "connectivity-impact", "moved": report["bladeNodesMovedIntoGiant"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
