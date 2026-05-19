# CANON

inherits: user-galaxy
content_kind: prose

---

## Axiom
**This is your personal governance graph. Every conversation that matters hardens here.**

Start with one axiom — something you believe is true and worth keeping. LAUDE will help you find them.

## Constraints

```
MUST:     Treat this repo as canonical — LAUDE runtime holds no durable transcript content beyond the 24h D1 cache
MUST:     Land every session-close as a PR (auto-merged when scoped to LEDGER/transcripts/ ∪ INTEL/; human-reviewed when touching CANON.md)
MUST:     Preserve magic-manifest.json signatures — federation identity is Ed25519-anchored
MUST NOT: Auto-merge PRs whose diff touches CANON.md — axiom mutations require human review
MUST NOT: Hand-edit magic-manifest.json — LAUDE's provisioner signs it
```

---

*CANON | user-galaxy*
