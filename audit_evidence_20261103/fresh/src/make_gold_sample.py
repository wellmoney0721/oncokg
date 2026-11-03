"""Draw a stratified sample of resolutions for manual scoring.

Sampling is stratified by tier rather than uniform, because the tiers that carry
the most risk (fuzzy, segmented, blocked) are also the rarest. A uniform sample
would be dominated by exact matches and would say almost nothing about where the
pipeline actually fails.
"""
from __future__ import annotations

import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

QUOTA = {
    "EXACT": 40,
    "ALIAS": 30,
    "CONTAINED_ALIAS": 30,
    "FUZZY_AUTO": 50,          # take all
    "FUZZY_REVIEW": 50,        # take all
    "PARENTHETICAL": 15,
    "SALT_STRIPPED": 50,       # take all
    "CLEANED": 50,             # take all
    "AMBIGUOUS": 12,
    "BLOCKED_PLACEBO": 8,
    "BLOCKED_CLASS_TERM": 8,
    "BLOCKED_TARGET_TERM": 8,
    "UNRESOLVED": 25,
}
SEED_DEV = 20261103
SEED_TEST = 777104
SEED_POSTFIX = 31415926


def main() -> None:
    """Draw either the development sample or the held-out test sample.

    The development sample was inspected while the rules were being written, so
    any number computed on it is optimistic by construction. The test sample is
    drawn with a different seed, with every development row excluded, and is
    scored only after the rules are frozen.
    """
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    if mode not in ("dev", "test", "postfix"):
        sys.exit("usage: make_gold_sample.py [dev|test|postfix]")
    seed = {"dev": SEED_DEV, "test": SEED_TEST, "postfix": SEED_POSTFIX}[mode]
    out_name = {"dev": "gold_dev.csv", "test": "gold_test.csv",
                "postfix": "gold_postfix.csv"}[mode]
    if mode == "postfix":
        QUOTA.update({"EXACT": 10, "ALIAS": 10, "CONTAINED_ALIAS": 15,
                      "PARENTHETICAL": 50, "UNRESOLVED": 10,
                      "BLOCKED_CLASS_TERM": 6, "BLOCKED_PLACEBO": 4,
                      "AMBIGUOUS": 0, "BLOCKED_TARGET_TERM": 0,
                      "FUZZY_AUTO": 0, "FUZZY_REVIEW": 0,
                      "SALT_STRIPPED": 0, "CLEANED": 0})

    excluded: set = set()
    if mode in ("test", "postfix"):
        prior = ["gold_dev.csv"] + (["gold_test.csv"] if mode == "postfix" else [])
        for name in prior:
            path_prior = C.REPORTS / name
            if path_prior.exists():
                with path_prior.open(encoding="utf-8") as fh:
                    for r in csv.DictReader(fh):
                        excluded.add((r["raw"], r["component"], r["drug_id"] or None))
        print(f"excluding {len(excluded)} previously sampled rows")
    d = json.loads((C.PROCESSED / "resolved.json").read_text(encoding="utf-8"))
    drugs = d["dictionary"]["drugs"]

    by_tier: dict[str, dict] = defaultdict(dict)
    for t in d["trials"]:
        for iv in t["interventions"]:
            for c in iv["components"]:
                key = (iv["raw"], c["component"], c.get("drug_id"))
                by_tier[c["tier"]].setdefault(key, {
                    "tier": c["tier"],
                    "raw": iv["raw"],
                    "component": c["component"],
                    "drug_id": c.get("drug_id"),
                    "resolved_name": drugs[c["drug_id"]]["name"] if c.get("drug_id") else "",
                    "score": c.get("score") or "",
                    "rules": "|".join(c.get("rules") or []),
                    "note": c.get("note", ""),
                    "example_nct": t["nct_id"],
                })

    rng = random.Random(seed)
    rows = []
    for tier, items in sorted(by_tier.items()):
        pool = [v for k, v in items.items() if k not in excluded]
        n = min(QUOTA.get(tier, 10), len(pool))
        rows.extend(rng.sample(pool, n))

    rows.sort(key=lambda r: (r["tier"], r["raw"].lower()))
    for i, r in enumerate(rows, 1):
        r["id"] = i
        r["verdict"] = ""        # correct | incorrect  (filled in by a reviewer)
        r["reviewer_note"] = ""

    path = C.REPORTS / out_name
    cols = ["id", "tier", "raw", "component", "drug_id", "resolved_name",
            "score", "rules", "note", "example_nct", "verdict", "reviewer_note"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"{len(rows)} rows -> {path.relative_to(C.ROOT)}")
    for tier, items in sorted(by_tier.items()):
        n = sum(1 for r in rows if r["tier"] == tier)
        print(f"  {tier:22s} sampled {n:3d} / {len(items)} unique")


if __name__ == "__main__":
    main()
