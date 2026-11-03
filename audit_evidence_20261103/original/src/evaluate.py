"""Turn the labelled sample into numbers that survive a hostile question.

Two things are measured separately, because conflating them is how pipelines
come to look better than they are:

  precision  of the matches the pipeline accepts automatically
  coverage   how much of the real-world text it manages to resolve at all

A pipeline can always buy coverage by lowering its threshold. Reporting both,
with the sampling error attached, makes that trade visible instead of hidden.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import normalize as N

ACCEPTING = ["EXACT", "ALIAS", "CLEANED", "SALT_STRIPPED",
             "PARENTHETICAL", "CONTAINED_ALIAS", "FUZZY_AUTO"]
WITHHOLDING = ["FUZZY_REVIEW", "AMBIGUOUS", "BLOCKED_PLACEBO",
               "BLOCKED_CLASS_TERM", "BLOCKED_TARGET_TERM", "UNRESOLVED"]


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def main() -> None:
    resolved = json.loads((C.PROCESSED / "resolved.json").read_text(encoding="utf-8"))
    which = sys.argv[1] if len(sys.argv) > 1 else "test"
    primary = C.REPORTS / {"test": "gold_test.csv", "dev": "gold_dev.csv",
                           "postfix": "gold_postfix.csv"}[which]
    rows = list(csv.DictReader(primary.open(encoding="utf-8")))
    if any(not r["verdict"] for r in rows):
        sys.exit(f"{primary.name} still has unlabelled rows")

    # tiers whose every distinct value was consumed by the development sample
    # cannot be re-sampled independently; their rate is carried over and marked.
    fallback: dict[str, list] = defaultdict(list)
    dev_path = C.REPORTS / "gold_dev.csv"
    if which in ("test", "postfix") and dev_path.exists():
        for r in csv.DictReader(dev_path.open(encoding="utf-8")):
            if r["verdict"]:
                fallback[r["tier"]].append(r["verdict"] == "correct")

    # population: distinct (surface, component, resolution) triples per tier
    population: dict[str, set] = defaultdict(set)
    occurrences: dict[str, int] = defaultdict(int)
    for t in resolved["trials"]:
        for iv in t["interventions"]:
            for c in iv["components"]:
                population[c["tier"]].add((iv["raw"], c["component"], c.get("drug_id")))
                occurrences[c["tier"]] += 1
    population = {k: len(v) for k, v in population.items()}

    sampled: dict[str, list] = defaultdict(list)
    for r in rows:
        sampled[r["tier"]].append(r["verdict"] == "correct")

    carried = []
    for tier, verdicts in fallback.items():
        if tier not in sampled:
            sampled[tier] = verdicts
            carried.append(tier)

    per_tier = {}
    for tier, verdicts in sampled.items():
        n, k = len(verdicts), sum(verdicts)
        lo, hi = wilson(k, n)
        per_tier[tier] = {
            "sampled": n, "correct": k, "rate": k / n,
            "ci95": [round(lo, 4), round(hi, 4)],
            "population_unique": population.get(tier, 0),
            "population_occurrences": occurrences.get(tier, 0),
            "source": "development sample (no independent test rows available)"
                      if tier in carried else f"{which} sample",
        }

    # Stratified estimate over the tiers that actually assert an edge.
    #
    # The sample is drawn by a disproportionate per-tier quota, so the raw
    # sample mean is NOT an estimate of pipeline precision -- reweighting is
    # required, not optional. But the reweighting is also what makes the
    # number look better than the raw rows, so both are reported side by side
    # and neither is called "the" precision without its denominator.
    #
    # The interval is built from per-tier Wilson bounds rather than a normal
    # approximation. An earlier version used a Wald interval on the stratified
    # mean; because 88% of the weight sits in tiers that scored 100%, the
    # binomial variance term was exactly zero for those tiers and the interval
    # collapsed to a width that no sample of this size can support. A tier with
    # 40/40 correct is not known to be 100% accurate; its Wilson lower bound is
    # 91.2%, and propagating those bounds is the honest statement.
    num = den = 0.0
    lo_num = hi_num = 0.0
    for tier in ACCEPTING:
        st = per_tier.get(tier)
        if not st or st["population_unique"] == 0:
            continue
        w = st["population_unique"]
        num += w * st["rate"]
        den += w
        lo_num += w * st["ci95"][0]
        hi_num += w * st["ci95"][1]
    precision = num / den if den else 0.0
    precision_lo = lo_num / den if den else 0.0
    precision_hi = hi_num / den if den else 0.0

    # the unweighted truth about the rows a human actually read
    acc_rows = [r for r in rows if r["tier"] in ACCEPTING]
    acc_k = sum(1 for r in acc_rows if r["verdict"] == "correct")
    acc_n = len(acc_rows)
    raw_lo, raw_hi = wilson(acc_k, acc_n)

    accepted_occ = sum(occurrences.get(t, 0) for t in ACCEPTING)
    total_occ = sum(occurrences.values())
    substance_occ = total_occ - sum(occurrences.get(t, 0) for t in
                                    ("BLOCKED_PLACEBO", "BLOCKED_CLASS_TERM",
                                     "BLOCKED_TARGET_TERM"))

    report = {
        "evaluated_on": primary.name,
        "gold_sample_size": len(rows),
        "tiers_carried_from_dev": carried,
        "per_tier": per_tier,
        "accepted_precision": {
            "estimate": round(precision, 4),
            "ci95": [round(precision_lo, 4), round(precision_hi, 4)],
            "method": ("stratified estimate weighted by distinct resolutions "
                       "per tier; interval propagated from per-tier Wilson "
                       "bounds, not a normal approximation"),
            "weighted_over_tiers": [t for t in ACCEPTING
                                    if per_tier.get(t, {}).get("population_unique")],
            "caveat": ("the sample is drawn by a disproportionate per-tier "
                       "quota, so this reweighting is required; it is also "
                       "what makes the figure higher than the raw rows, so "
                       "read it next to raw_sample_precision below"),
        },
        "raw_sample_precision": {
            "accepted_rows_scored": acc_n,
            "accepted_rows_correct": acc_k,
            "rate": round(acc_k / acc_n, 4) if acc_n else None,
            "ci95": [round(raw_lo, 4), round(raw_hi, 4)],
            "note": ("the unweighted result over the rows a human actually "
                     f"read. {acc_n} of the {len(rows)} rows in this sample "
                     "sit in an accepting tier; the rest are refusals and "
                     "are scored separately. The sample size is "
                     f"{len(rows)}, the precision denominator is {acc_n} -- "
                     "these are different numbers and quoting the first as "
                     "the second overstates the evidence"),
        },
        "coverage": {
            "component_occurrences_total": total_occ,
            "component_occurrences_excluding_blocked": substance_occ,
            "accepted_occurrences": accepted_occ,
            "resolved_rate_of_substance_like": round(accepted_occ / substance_occ, 4),
            "resolved_rate_of_all": round(accepted_occ / total_occ, 4),
        },
        "withheld_tier_quality": {
            "FUZZY_REVIEW_would_have_been_correct": per_tier.get("FUZZY_REVIEW", {}).get("rate"),
            "reading": "most proposals held for review are wrong, which is the "
                       "evidence that the automatic threshold is not set too low",
        },
        "limitations": [
            "labels assigned by one reviewer (the pipeline author); no second annotator",
            "FUZZY_AUTO, SALT_STRIPPED and CLEANED have so few distinct values that the "
            "development sample consumed all of them; their rates are carried over and "
            "are therefore optimistic, since the rules were tuned on exactly those rows",
            "reference vocabulary is scoped to NSCLC drug candidates, so a correct "
            "refusal to resolve an out-of-scope drug counts as missing coverage, not "
            "as an error",
            "sampling is stratified by tier, so tier-level rates are far more "
            "precise than the rare tiers' raw counts suggest, but tiers with very "
            "few distinct values still carry wide intervals",
        ],
    }

    out_name = {"test": "evaluation_frozen_test.json", "dev": "evaluation_dev.json",
                "postfix": "evaluation_postfix.json"}[which]
    (C.REPORTS / out_name).write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== resolution quality ===")
    print(f"{'tier':22s} {'n':>4s} {'ok':>4s} {'rate':>7s}  {'95% CI':>16s} "
          f"{'uniq':>6s} {'occ':>6s}")
    for tier in ACCEPTING + WITHHOLDING:
        st = per_tier.get(tier)
        if not st:
            continue
        lo, hi = st["ci95"]
        print(f"{tier:22s} {st['sampled']:4d} {st['correct']:4d} "
              f"{st['rate']*100:6.1f}%  [{lo*100:5.1f}%,{hi*100:5.1f}%] "
              f"{st['population_unique']:6d} {st['population_occurrences']:6d}")
    ap = report["accepted_precision"]
    cv = report["coverage"]
    print(f"\naccepted-match precision : {ap['estimate']*100:.1f}% "
          f"(95% CI {ap['ci95'][0]*100:.1f}-{ap['ci95'][1]*100:.1f}%)")
    print(f"coverage of substance-like strings: "
          f"{cv['resolved_rate_of_substance_like']*100:.1f}% "
          f"({cv['accepted_occurrences']}/{cv['component_occurrences_excluding_blocked']})")
    print(f"\n-> {(C.REPORTS / out_name).relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
