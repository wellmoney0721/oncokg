"""Automated quality control over the resolved records and the dictionary.

Findings are not assertions that the source is wrong. They are *claims that a
curator should look at*, each with the evidence attached and a severity, because
a quality system that cannot be argued with is a quality system nobody trusts.

Three families:
  dictionary   defects in the reference vocabulary itself
  record       defects in how a registry record was parsed or resolved
  graph        defects that only appear once records are joined together
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import normalize as N
import textrules as T

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def record_checks(resolved: dict) -> list[dict]:
    findings: list[dict] = []
    drugs = resolved["dictionary"]["drugs"]

    unresolved_counter: Counter = Counter()
    unresolved_example: dict[str, str] = {}

    for t in resolved["trials"]:
        nct = t["nct_id"]

        # (a) part of an intervention string was understood and part was not
        for iv in t["interventions"]:
            resolved_here = [c for c in iv["components"]
                             if c["tier"] in N.ACCEPTED_TIERS]
            residue = [c for c in iv["components"]
                       if "segmentation_residue" in (c.get("rules") or [])]
            # only a residue that *looks like a substance* matters; leftover
            # prose ("after randomization") is noise and reporting it would bury
            # the real cases
            index = resolved["dictionary"]["index"]
            suspicious = []
            for c in residue:
                for tok in str(c["component"]).split():
                    if T.is_dev_code(tok) or T.canonical_key(tok) in index:
                        suspicious.append(tok)
            if resolved_here and suspicious:
                findings.append({
                    "family": "record", "type": "incomplete_intervention_parse",
                    "severity": "high", "nct_id": nct,
                    "surface": iv["raw"],
                    "resolved_to": [drugs[c["drug_id"]]["name"] for c in resolved_here
                                    if c.get("drug_id")],
                    "not_accounted_for": sorted(set(suspicious)),
                    "why": "the record names something the parse could not account for, "
                           "so any exposure count built on it may be understated",
                })
            for c in iv["components"]:
                if c["tier"] == N.TIER_UNRESOLVED and c["component"]:
                    unresolved_counter[c["component"]] += 1
                    unresolved_example.setdefault(c["component"], nct)

        # (b) the trial resolved to no substance at all
        resolved_any = any(c["tier"] in N.ACCEPTED_TIERS
                           for iv in t["interventions"] for c in iv["components"])
        has_drug_arm = bool(t["interventions"])
        if has_drug_arm and not resolved_any:
            findings.append({
                "family": "record", "type": "no_substance_resolved",
                "severity": "medium", "nct_id": nct,
                "surfaces": [iv["raw"] for iv in t["interventions"]][:5],
                "why": "the trial has drug arms but none could be tied to a known "
                       "molecule, so it is invisible to any drug-centred question",
            })

        # (c) the condition query returned a trial outside the disease scope
        if t["conditions"] and all(c["disease_id"] is None for c in t["conditions"]):
            findings.append({
                "family": "record", "type": "out_of_scope_trial",
                "severity": "low", "nct_id": nct,
                "conditions": [c["raw"] for c in t["conditions"]][:5],
                "why": "retrieved by the NSCLC condition query but none of its stated "
                       "conditions normalise to NSCLC; a precision problem in the query, "
                       "not in the record",
            })

        # (d) structural gaps that affect downstream aggregation
        missing = [f for f in ("phases", "start_date", "enrollment") if not t.get(f)]
        if missing:
            findings.append({
                "family": "record", "type": "missing_structural_field",
                "severity": "low", "nct_id": nct, "missing": missing,
                "why": "absent fields silently bias any time or size aggregation",
            })

    # (e) recurring unresolved surfaces are a vocabulary gap, not noise
    for surface, n in unresolved_counter.most_common():
        if n < 3:
            break
        findings.append({
            "family": "record", "type": "recurrent_unresolved_surface",
            "severity": "medium", "surface": surface, "occurrences": n,
            "example_nct": unresolved_example[surface],
            "why": "a string this frequent is a missing dictionary entry, and is "
                   "the highest-value place to extend coverage",
        })
    return findings


def graph_checks(resolved: dict) -> list[dict]:
    findings: list[dict] = []

    # (a) company normalisation that merged names which may not be one company
    by_key: dict[str, set] = defaultdict(set)
    for raw, c in resolved["companies"].items():
        by_key[c["key"]].add(raw)
    for key, names in by_key.items():
        if len(names) > 1:
            findings.append({
                "family": "graph", "type": "company_names_merged",
                "severity": "low", "canonical_key": key,
                "merged_names": sorted(names),
                "why": "reported so a reviewer can confirm these are one organisation; "
                       "legal-suffix stripping cannot tell a subsidiary from a namesake",
            })

    # (b) a drug reaching a later stage in one trial than the reference says
    stage_rank = {"PHASE1": 1, "PHASE2": 2, "PHASE3": 3, "PHASE4": 4}
    ref_rank = {"PHASE_1": 1, "PHASE_2": 2, "PHASE_3": 3, "PHASE_4": 4,
                "APPROVAL": 5, "APPROVED": 5}
    drugs = resolved["dictionary"]["drugs"]
    best: dict[str, tuple] = {}
    for t in resolved["trials"]:
        tr = max((stage_rank.get(p, 0) for p in t["phases"]), default=0)
        for iv in t["interventions"]:
            for c in iv["components"]:
                if c["tier"] in N.ACCEPTED_TIERS and c.get("drug_id"):
                    cur = best.get(c["drug_id"])
                    if cur is None or tr > cur[0]:
                        best[c["drug_id"]] = (tr, t["nct_id"])
    for did, (tr, nct) in best.items():
        ref = ref_rank.get(drugs[did].get("max_phase_in_nsclc") or "", 0)
        if tr and ref and tr > ref:
            findings.append({
                "family": "graph", "type": "stage_disagrees_with_reference",
                "severity": "medium", "drug_id": did, "drug_name": drugs[did]["name"],
                "trial_phase": tr, "reference_phase_in_nsclc": drugs[did]["max_phase_in_nsclc"],
                "evidence_nct": nct,
                "why": "the registry shows a later phase than the curated reference; "
                       "either the reference lags or the trial was mis-resolved",
            })
    return findings


def main() -> None:
    resolved = json.loads((C.PROCESSED / "resolved.json").read_text(encoding="utf-8"))

    dictionary = [dict(f, family="dictionary") for f in resolved["dictionary_findings"]]
    duplicates = [dict(f, family="dictionary") for f in resolved["duplicate_findings"]]
    records = record_checks(resolved)
    graph = graph_checks(resolved)

    all_findings = dictionary + duplicates + records + graph
    all_findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.get("severity", "low"), 3),
                                     f.get("type", "")))

    summary: dict = defaultdict(lambda: defaultdict(int))
    for f in all_findings:
        summary[f["family"]][f["type"]] += 1

    report = {
        "generated_from": resolved["_built_from"],
        "totals": {
            "findings": len(all_findings),
            "by_severity": dict(Counter(f.get("severity", "low") for f in all_findings)),
            "by_family": {k: dict(v) for k, v in summary.items()},
        },
        "findings": all_findings,
    }
    path = C.REPORTS / "quality_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(all_findings)} findings -> {path.relative_to(C.ROOT)}")
    for fam, types in summary.items():
        print(f"\n[{fam}]")
        for t, n in sorted(types.items(), key=lambda x: -x[1]):
            print(f"  {n:6d}  {t}")


if __name__ == "__main__":
    main()
