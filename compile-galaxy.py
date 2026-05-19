#!/usr/bin/env python3
"""compile-galaxy.py — Build galaxy.json from INTEL/<scope>/INTEL.md hierarchy.

Run by GH Actions on every push that touches INTEL/**. Walks the INTEL/
directory, derives scope IDs from directory paths, extracts axiom slugs from
## headings, and emits galaxy.json with nodes + edges.

The compiled galaxy.json is fetched by the CF worker (api.canonic.org) via
GitHub raw URL and cached in KV as galaxy:user:<user_id> with 5-min TTL.
No CF secrets required — GitHub is the source of truth.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re

INTEL_DIR = pathlib.Path('INTEL')
OUT = pathlib.Path('galaxy.json')


def compile_galaxy() -> dict:
    nodes: list[dict] = []
    edges: list[dict] = []
    seen_scopes: set[str] = set()

    def ensure_scope_ancestors(scope: str) -> None:
        parts = scope.split('/')
        for i in range(len(parts)):
            anc = '/'.join(parts[: i + 1])
            if anc in seen_scopes:
                continue
            seen_scopes.add(anc)
            parent = '/'.join(parts[:i]) if i > 0 else None
            nodes.append({
                'id': anc,
                'label': parts[i],
                'kind': 'SCOPE',
                'parent': parent,
                'has_intel': False,
                'children': 0,
                'axiom_count': 0,
            })
            if parent:
                edges.append({'kind': 'PARENT', 'from': parent, 'to': anc})

    if INTEL_DIR.exists():
        for intel_file in sorted(INTEL_DIR.rglob('INTEL.md')):
            rel = intel_file.parent.relative_to(INTEL_DIR)
            scope = str(rel).replace('\\', '/')
            if not scope or scope == '.':
                continue

            ensure_scope_ancestors(scope)

            content = intel_file.read_text(encoding='utf-8')
            axiom_slugs = re.findall(r'^## (.+)$', content, re.MULTILINE)

            # Mark the leaf scope as having INTEL
            for n in nodes:
                if n['id'] == scope:
                    n['has_intel'] = True
                    n['axiom_count'] = len(axiom_slugs)
                    break

            # Emit axiom nodes
            for slug in axiom_slugs:
                slug = slug.strip()
                axiom_id = f'axiom:{scope}/{slug}'
                nodes.append({
                    'id': axiom_id,
                    'label': slug,
                    'kind': 'AXIOM',
                    'parent': scope,
                    'has_intel': False,
                    'children': 0,
                })
                edges.append({'kind': 'PARENT', 'from': scope, 'to': axiom_id})

    # Update children counts
    child_counts: dict[str, int] = {}
    for n in nodes:
        if n.get('parent'):
            child_counts[n['parent']] = child_counts.get(n['parent'], 0) + 1
    for n in nodes:
        n['children'] = child_counts.get(n['id'], 0)

    return {
        'nodes': nodes,
        'edges': edges,
        'generated': datetime.datetime.utcnow().isoformat() + 'Z',
        'stats': {
            'total': len(nodes),
            'intel_coverage': sum(1 for n in nodes if n.get('has_intel')),
        },
    }


if __name__ == '__main__':
    galaxy = compile_galaxy()
    OUT.write_text(json.dumps(galaxy, indent=2), encoding='utf-8')
    print(f'Compiled {galaxy["stats"]["total"]} nodes, {len(galaxy["edges"])} edges → {OUT}')
