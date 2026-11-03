"""Measure what dictionary curation actually buys, by resolving twice.

The README used to claim curation cut ambiguous resolutions "from 2,008 to 66".
The after-figure came from the pipeline; the before-figure came from a console
line in a session that no longer exists, and nothing in the repository could
reproduce it. An independent audit flagged it as unverifiable, which it was.

So it is measured instead of remembered: the same corpus is resolved twice,
once against the raw dictionary as the reference data supplies it and once
against the curated one, and the two tier distributions are written to
reports/curation_effect.json. Every curation figure quoted anywhere else in
this project reads from that file.

    python src/curation_effect.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import normalize as N
import textrules as T


def resolve_corpus(dic: dict, trials: list, target_keys: set) -> Counter:
    index_keys = list(dic["index"].keys())
    tiers: Counter = Counter()
    for t in trials:
        proto = t.get("protocolSection", {})
        arms = proto.get("armsInterventionsModule", {}) or {}
        for iv in (arms.get("interventions") or []):
            name = iv.get("name")
            if not name:
                continue
            res = N.resolve_drug_string(name, dic, index_keys, target_keys)
            for comp in res["components"]:
                tiers[comp["tier"]] += 1
    return tiers


def main() -> None:
    drug_rows, _, _ = N._load("drugs")
    target_rows, _, _ = N._load("targets")
    trials, _, _ = N._load("trials")

    target_keys = set()
    for r in target_rows:
        t = r["target"]
        for label in [t.get("approvedSymbol"), t.get("approvedName")]:
            if label:
                target_keys.add(T.canonical_key(label))
        for grp in ("synonyms", "symbolSynonyms", "nameSynonyms", "obsoleteSymbols"):
            for a in (t.get(grp) or []):
                if a.get("label"):
                    target_keys.add(T.canonical_key(a["label"]))

    print("pass 1: raw dictionary, exactly as the reference data supplies it")
    raw = N.build_drug_dictionary(drug_rows)
    raw.pop("build_findings", None)
    raw_keys_ambiguous = sum(1 for v in raw["index"].values()
                             if len({e["drug_id"] for e in v}) > 1)
    before = resolve_corpus(raw, trials, target_keys - set(raw["index"]))

    print("pass 2: curated dictionary")
    cur = N.build_drug_dictionary(drug_rows)
    findings = cur.pop("build_findings") + N.curate_dictionary(cur)
    cur_keys_ambiguous = sum(1 for v in cur["index"].values()
                             if len({e["drug_id"] for e in v}) > 1)
    after = resolve_corpus(cur, trials, target_keys - set(cur["index"]))

    by_type: Counter = Counter(f["type"] for f in findings)
    tiers = sorted(set(before) | set(after))
    report = {
        "what_this_measures": (
            "the same corpus resolved twice -- once against the dictionary as "
            "the reference data supplies it, once after curation -- so the "
            "effect of curation is a measurement rather than a recollection"),
        "why_absolute_counts_differ_from_the_pipeline": (
            "this pass resolves every intervention in the raw snapshot, while "
            "the pipeline first drops out-of-scope trials, so the absolute "
            "totals here run slightly higher than reports/evaluation_*.json. "
            "Both arms of this comparison use the identical corpus, so the "
            "before/after delta is unaffected"),
        "lookup_keys_ambiguous": {
            "before": raw_keys_ambiguous, "after": cur_keys_ambiguous},
        "resolutions_by_tier": {
            t: {"before": before.get(t, 0), "after": after.get(t, 0),
                "delta": after.get(t, 0) - before.get(t, 0)} for t in tiers},
        "headline": {
            "ambiguous_before": before.get(N.TIER_AMBIGUOUS, 0),
            "ambiguous_after": after.get(N.TIER_AMBIGUOUS, 0),
            "exact_before": before.get(N.TIER_EXACT, 0),
            "exact_after": after.get(N.TIER_EXACT, 0),
        },
        "curation_findings_by_type": dict(by_type),
    }
    out = C.REPORTS / "curation_effect.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    h = report["headline"]
    print(f"\n  ambiguous resolutions : {h['ambiguous_before']} -> {h['ambiguous_after']}")
    print(f"  exact resolutions     : {h['exact_before']} -> {h['exact_after']}")
    print(f"  ambiguous lookup keys : {raw_keys_ambiguous} -> {cur_keys_ambiguous}")
    print(f"\n-> {out.relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
