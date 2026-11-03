"""Synonym dictionary + entity resolution.

Three resolution problems, one shared philosophy:

  drug      messy intervention text  -> ChEMBL molecule
  disease   messy condition text     -> MONDO disease
  company   messy sponsor text       -> canonical organisation

The philosophy: **an unresolved record is cheaper than a wrong one.** Every
resolution carries a tier and a reason code, and anything below the automatic
threshold is routed to review instead of being silently accepted. Precision is
reported separately from coverage so the two are never traded against each other
by accident.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rapidfuzz import fuzz, process

import config as C
import textrules as T

# --------------------------------------------------------------------------- #
# tiers
# --------------------------------------------------------------------------- #
# Brand names that ChEMBL lists as synonyms of a molecule but that identify a
# *different* product from the one the molecule record describes. Keeping them
# in the index is how "Abraxane" becomes solvent-based paclitaxel: same active
# moiety, different formulation, different approval, different trial arm.
# Each entry carries the reason it was removed, and the removal is reported as
# a dictionary finding rather than applied silently.
DISTINCT_PRODUCT_ALIASES = {
    "abraxane": ("Abraxane is nab-paclitaxel (albumin-bound), a separate "
                 "product from solvent-based paclitaxel with its own approval "
                 "and its own trial arms"),
    "nabpaclitaxel": ("nab-paclitaxel is a distinct albumin-bound product, "
                      "routinely compared head-to-head against paclitaxel"),
    "abraxis": ("Abraxis/Abraxane branding refers to the albumin-bound "
                "formulation, not the parent molecule"),
    "doxil": ("Doxil is liposomal doxorubicin, a distinct product with a "
              "different toxicity profile from conventional doxorubicin"),
    "caelyx": ("Caelyx is liposomal doxorubicin, not conventional "
               "doxorubicin"),
    "onivyde": ("Onivyde is liposomal irinotecan, a distinct product"),
    "depocyt": ("DepoCyt is liposomal cytarabine, a distinct product"),
}

TIER_EXACT = "EXACT"                 # preferred name matched verbatim
TIER_ALIAS = "ALIAS"                 # a registered synonym or trade name matched
TIER_CLEANED = "CLEANED"             # matched after dose/formulation cleaning
TIER_SALT = "SALT_STRIPPED"          # matched after removing a salt form
TIER_PAREN = "PARENTHETICAL"         # matched on the code name inside brackets
TIER_FUZZY = "FUZZY_AUTO"            # accepted automatically above threshold
TIER_REVIEW = "FUZZY_REVIEW"         # plausible, held back for human review
TIER_CONTAINED = "CONTAINED_ALIAS"   # a dictionary term sits inside a longer phrase
TIER_AMBIGUOUS = "AMBIGUOUS"         # one surface form, several molecules
TIER_BLOCKED_PLACEBO = "BLOCKED_PLACEBO"
TIER_BLOCKED_CLASS = "BLOCKED_CLASS_TERM"
TIER_BLOCKED_TARGET = "BLOCKED_TARGET_TERM"
TIER_BLOCKED_DISTINCT_PRODUCT = "BLOCKED_DISTINCT_PRODUCT"
TIER_BLOCKED_NEGATED = "BLOCKED_NEGATED"   # "No pembrolizumab": an absence, not an exposure
TIER_UNRESOLVED = "UNRESOLVED"

ACCEPTED_TIERS = {TIER_EXACT, TIER_ALIAS, TIER_CLEANED, TIER_SALT,
                  TIER_PAREN, TIER_FUZZY, TIER_CONTAINED}
MIN_CONTAINED_LEN = 7

FUZZY_AUTO_THRESHOLD = 93
FUZZY_REVIEW_THRESHOLD = 86
MIN_FUZZY_LEN = 5


def _load(name: str):
    doc = json.loads((C.RAW / f"{name}.json").read_text(encoding="utf-8"))
    return doc["data"], doc["_fetched_at"], doc["_source"]


# --------------------------------------------------------------------------- #
# drug dictionary
# --------------------------------------------------------------------------- #
def build_drug_dictionary(drug_rows: list[dict]) -> dict:
    """alias key -> list of {drug_id, alias, alias_type}

    A key pointing at more than one molecule is an *ambiguous* alias. Those are
    kept, not discarded: the graph needs to know the ambiguity exists so it can
    refuse to guess.
    """
    index: dict[str, list[dict]] = defaultdict(list)
    drugs: dict[str, dict] = {}
    build_findings: list[dict] = []

    for row in drug_rows:
        d = row.get("drug") or {}
        did = d.get("id")
        if not did:
            continue
        if did not in drugs:
            moa_targets, moa_desc = [], []
            moa = d.get("mechanismsOfAction") or {}
            for m in (moa.get("rows") or []):
                if m.get("mechanismOfAction"):
                    moa_desc.append(m["mechanismOfAction"])
                for t in (m.get("targets") or []):
                    if t.get("id"):
                        moa_targets.append({"target_id": t["id"],
                                            "symbol": t.get("approvedSymbol"),
                                            "action_type": m.get("actionType")})
            drugs[did] = {
                "drug_id": did,
                "name": d.get("name"),
                "drug_type": d.get("drugType"),
                "max_phase_overall": d.get("maximumClinicalStage"),
                "max_phase_in_nsclc": row.get("maxClinicalStage"),
                "parent_molecule": (d.get("parentMolecule") or {}).get("id"),
                "mechanisms": moa_desc,
                "moa_targets": moa_targets,
                "aliases": [],
            }

        seen_alias = set()

        def add(label: str, alias_type: str, source: str | None = None):
            if not label:
                return
            own = drugs[did]["name"] or ""
            if (T.canonical_key(label) in DISTINCT_PRODUCT_ALIASES
                    or (T.is_distinct_product(label) and not T.is_distinct_product(own)
                        and not re.search(r"peg|liposom|albumin|nanopart", own, re.I))):
                build_findings.append({
                    "type": "distinct_product_alias",
                    "severity": "high",
                    "alias": label,
                    "affected_drugs": [did],
                    "affected_drug_name": drugs[did]["name"],
                    "action": "alias dropped before indexing",
                    "why": DISTINCT_PRODUCT_ALIASES.get(
                        T.canonical_key(label),
                        "a biosimilar or reformulated product named by the alias "
                        "is not the originator molecule"),
                })
                return
            if T.is_placebo(label):
                build_findings.append({
                    "type": "placebo_string_in_synonym_list",
                    "severity": "high",
                    "alias": label,
                    "affected_drugs": [did],
                    "affected_drug_name": drugs[did]["name"],
                    "action": "alias dropped before indexing",
                    "why": "a placebo label describes an arm, not the substance; "
                           "indexing it would turn control arms into exposures",
                })
                return
            key = T.canonical_key(label)
            if not key or (key, alias_type) in seen_alias:
                return
            seen_alias.add((key, alias_type))
            drugs[did]["aliases"].append({"alias": label, "type": alias_type,
                                          "source": source})
            if not any(e["drug_id"] == did for e in index[key]):
                index[key].append({"drug_id": did, "alias": label,
                                   "alias_type": alias_type, "source": source})

        add(d.get("name"), "preferred_name")
        for s in (d.get("synonyms") or []):
            add(s.get("label"), "synonym", s.get("source"))
        for t in (d.get("tradeNames") or []):
            add(t.get("label"), "trade_name")

    return {"index": dict(index), "drugs": drugs, "build_findings": build_findings}


# --------------------------------------------------------------------------- #
# dictionary curation
# --------------------------------------------------------------------------- #
RE_CLASS_LIKE = re.compile(
    r"^(?:anti[\s\-]?)|(?:\b(?:blockade|inhibitor|inhibitors|antibody|antibodies|"
    r"agonist|antagonist|therapy|chemotherapy|blocker)\b)", re.I)


def curate_dictionary(dic: dict) -> list[dict]:
    """Resolve dictionary-level defects before any record is matched against it.

    A reference vocabulary is not automatically trustworthy. These rules are
    applied in a fixed order and each one records what it changed, so the whole
    curation pass is reviewable and reversible.
    """
    index, drugs = dic["index"], dic["drugs"]
    findings: list[dict] = []

    preferred: dict[str, set] = defaultdict(set)
    for key, entries in index.items():
        for e in entries:
            if e["alias_type"] == "preferred_name":
                preferred[key].add(e["drug_id"])

    # (0) a class descriptor listed against a single molecule never becomes
    # ambiguous, so the ambiguity-driven rules below would never see it. It is
    # just as wrong there: "pd-l1 blockade" names a mechanism, not a product.
    for key in list(index.keys()):
        entries = index[key]
        if any(e["alias_type"] == "preferred_name" for e in entries):
            continue
        label = entries[0]["alias"]
        if RE_CLASS_LIKE.search(label) or T.is_class_term(label):
            findings.append({
                "type": "class_term_as_synonym",
                "severity": "high",
                "alias": label,
                "affected_drugs": sorted({e["drug_id"] for e in entries}),
                "action": "alias removed from lookup index; treated as a class term",
                "why": "a mechanism or class descriptor cannot identify a product, "
                       "even when only one record lists it",
            })
            del index[key]

    # (0b) Synonyms whose source is AACT are not curated identifiers. They are
    # intervention strings from trial records that were linked to a molecule,
    # so they carry whatever else the arm contained: TOBRAMYCIN is listed under
    # DEXAMETHASONE (from the eye-drop combination), CARBOPLATIN under
    # CISPLATIN, DOCETAXEL under PACLITAXEL, CHOP under PREDNISONE, and the
    # bare word "mab" under PEMBROLIZUMAB. Three kinds are removed:
    #   - a different active ingredient: the alias is shaped like an INN and
    #     shares no stem with the molecule's own name
    #   - a regimen acronym ("chop", "gemcis", "ac", "ep"), or a short
    #     abbreviation that does not single out one molecule ("lv", "fa", "ici").
    #     A three-letter abbreviation bound to one molecule ("ptx") is kept.
    #   - a distinct product (biosimilar, liposomal or albumin-bound form)
    # ChEMBL-sourced synonyms are left alone.
    for key in list(index.keys()):
        entries = index[key]
        keep = []
        for e in entries:
            if e["alias_type"] == "preferred_name":
                keep.append(e)
                continue
            if e.get("source") != "AACT":
                # curated synonyms are trusted, except that a regimen acronym
                # is never one drug whoever lists it ("ICE" under IFOSFAMIDE)
                if T.canonical_key(e["alias"]) not in REGIMEN_ACRONYMS:
                    keep.append(e)
                    continue
                reason = "regimen"
            else:
                reason = None
            if reason is None:
                reason = _foreign_registry_alias(e["alias"], drugs[e["drug_id"]])
                if (reason is None and len(key) <= 3 and not T.is_dev_code(e["alias"])
                        and _ambiguous_short_alias(e["alias"], index)):
                    reason = "abbreviation"
            if reason is None:
                keep.append(e)
                continue
            findings.append({
                "type": "registry_alias_removed",
                "severity": "high" if reason == "different_ingredient" else "medium",
                "alias": e["alias"],
                "reason": reason,
                "affected_drugs": [e["drug_id"]],
                "affected_drug_name": drugs[e["drug_id"]]["name"],
                "action": "alias removed from lookup index",
                "why": {"different_ingredient":
                            "the alias names another active ingredient, so "
                            "matching on it records an exposure to the wrong drug",
                        "abbreviation":
                            "an abbreviation of two letters, or three letters "
                            "shared by several molecules, cannot identify one",
                        "regimen":
                            "a regimen acronym names several drugs; listed "
                            "under one of them it records only that one",
                        "distinct_product":
                            "a biosimilar or reformulated product is not the "
                            "originator molecule"}[reason],
            })
        if keep:
            index[key] = keep
        else:
            del index[key]

    for key in list(index.keys()):
        entries = index[key]
        ids = {e["drug_id"] for e in entries}
        if len(ids) < 2:
            continue
        label = entries[0]["alias"]

        # (1) a class descriptor that upstream curation stored as a synonym
        if RE_CLASS_LIKE.search(label) or T.is_class_term(label) or (
            len(ids) >= 3 and key not in preferred
        ):
            findings.append({
                "type": "class_term_as_synonym",
                "severity": "high",
                "alias": label,
                "affected_drugs": sorted(ids),
                "action": "alias removed from lookup index; treated as a class term",
                "why": "a class descriptor cannot identify a single molecule, so "
                       "matching on it would fabricate a specific exposure",
            })
            del index[key]
            continue

        # (2) the alias is another molecule's own preferred name
        if key in preferred and len(preferred[key]) == 1:
            winner = next(iter(preferred[key]))
            losers = sorted(ids - {winner})
            findings.append({
                "type": "cross_drug_synonym",
                "severity": "high",
                "alias": label,
                "resolved_to": winner,
                "resolved_to_name": drugs[winner]["name"],
                "wrongly_listing_drugs": [
                    {"drug_id": l, "name": drugs[l]["name"]} for l in losers],
                "action": "alias bound to the molecule whose preferred name it is",
                "why": "a preferred name outranks a synonym; the other records "
                       "carry a suspected upstream curation error",
            })
            index[key] = [e for e in entries if e["drug_id"] == winner]
            continue

        # (3) salt / parent-child forms of the same substance
        parents = {drugs[i].get("parent_molecule") for i in ids if drugs[i].get("parent_molecule")}
        roots = ids & parents if parents else set()
        if len(roots) == 1 and ids <= (roots | {i for i in ids
                                                if drugs[i].get("parent_molecule") in roots}):
            root = next(iter(roots))
            findings.append({
                "type": "parent_child_collapse",
                "severity": "low",
                "alias": label,
                "resolved_to": root,
                "resolved_to_name": drugs[root]["name"],
                "collapsed": sorted(ids - {root}),
                "action": "alias bound to the parent molecule",
                "why": "salt and child forms of one substance are not distinct entities here",
            })
            index[key] = [e for e in entries if e["drug_id"] == root]
            continue

        findings.append({
            "type": "genuinely_ambiguous_alias",
            "severity": "medium",
            "alias": label,
            "candidates": [{"drug_id": i, "name": drugs[i]["name"]} for i in sorted(ids)],
            "action": "kept ambiguous; records matching it are routed to review",
            "why": "no rule can separate these without evidence outside the record",
        })

    return findings


RE_INN_SHAPE = re.compile(
    r"^[a-z]{4,}(?:mab|cept|nib|tinib|parib|ciclib|lisib|platin|taxel|rubicin|"
    r"mycin|micin|cycline|fosfamide|trexate|citabine|abine|tecan|zomib|degib|"
    r"rafenib|limus|mustine|olone|asone|isone|semide|prazole|"
    r"setron|pitant|ronate|grastim)$")


# Regimen acronyms name several drugs at once. Listed under one member they
# turn "CHOP" into prednisone and "GemCis" into cisplatin.
REGIMEN_ACRONYMS = {
    "chop", "rchop", "chope", "cvp", "folfox", "folfiri", "folfirinox",
    "xelox", "capox", "gemcis", "gemcarbo", "gemox", "abvd", "beacopp", "mvac",
    "ddmvac", "pfregimen", "tcbh", "tcb", "ecf", "eox", "flot", "icecure",
    "vac", "vip", "pcv", "tpf", "dcf", "gp", "gc", "tc", "cp", "pc", "ep",
    "ac", "ec", "fec", "cmf", "rd", "vrd", "vd", "mp", "dm", "ice", "rice",
    "mice", "epoch", "repoch", "dhap", "eshap", "gdp", "beam", "cav", "cvd",
}


def _same_entity_key(key: str) -> str:
    """The key a name lands on after same-entity merging."""
    for k, same in CURATED_SAME_ENTITY.items():
        if key == k:
            return same
    return key


def _ambiguous_short_alias(alias: str, index: dict) -> bool:
    """A short registry alias is kept only when it is a three-letter
    abbreviation that the whole index binds to one molecule ("ptx", "doc").
    Two letters or fewer never identify a substance."""
    key = T.canonical_key(alias)
    if len(key) <= 2:
        return True
    return len({e["drug_id"] for e in index.get(key, [])}) != 1


def _foreign_registry_alias(alias: str, drug: dict) -> str | None:
    """Why a registry-derived synonym cannot stand for this molecule, or None.

    The ingredient test is deliberately narrow. A first version flagged every
    INN-shaped word that did not share a stem with the molecule's name, and so
    removed former names and misspellings that are correct: apatinib under
    RIVOCERANIB (the same molecule renamed), hydroxydaunomycin under
    DOXORUBICIN, interleukin-2 under ALDESLEUKIN, "triplizumab" under
    TORIPALIMAB. A word is kept when the molecule's own curated (ChEMBL)
    synonyms contain it, or when it is a near-spelling of the molecule's name.
    """
    if T.is_distinct_product(alias) or T.canonical_key(alias) in DISTINCT_PRODUCT_ALIASES:
        return "distinct_product"
    if T.canonical_key(alias) in REGIMEN_ACRONYMS:
        return "regimen"
    name_key = T.canonical_key(drug["name"])
    curated_text = " ".join(a["alias"].lower() for a in drug["aliases"]
                            if a.get("source") != "AACT")
    curated_words = set(re.findall(r"[a-z]{5,}", curated_text)) | {name_key}
    words = re.findall(r"[a-z]+", alias.lower())
    # a multi-word name that contains the molecule's own name is that
    # molecule's full name ("nogapendekin alfa inbakicept"), not a foreign one
    if any(w[:5] in name_key for w in words if len(w) >= 5):
        return None
    for w in words:
        if not RE_INN_SHAPE.match(w):
            continue
        if name_key[:5] in w or w in curated_text:
            continue
        # a misspelling of the name or of a curated synonym ("anrotinib")
        if max(fuzz.ratio(w, c) for c in curated_words) >= 80:
            continue
        return "different_ingredient"
    return None


def detect_duplicate_entities(dic: dict) -> list[dict]:
    """Two identifiers that appear to describe one substance.

    Reported, never auto-merged: merging reference identifiers on the strength of
    name overlap alone would destroy information that a curator may need.
    """
    drugs = dic["drugs"]
    by_alias: dict[str, set] = defaultdict(set)
    for did, d in drugs.items():
        for a in d["aliases"]:
            by_alias[T.canonical_key(a["alias"])].add(did)

    pair_support: dict[tuple, set] = defaultdict(set)
    for key, ids in by_alias.items():
        if 2 <= len(ids) <= 3:
            ids = sorted(ids)
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    pair_support[(ids[i], ids[j])].add(key)

    findings = []
    for (a, b), keys in pair_support.items():
        if len(keys) < 3:
            continue
        if drugs[a].get("parent_molecule") == b or drugs[b].get("parent_molecule") == a:
            continue
        findings.append({
            "type": "suspected_duplicate_entity",
            "severity": "medium",
            "drug_a": {"drug_id": a, "name": drugs[a]["name"]},
            "drug_b": {"drug_id": b, "name": drugs[b]["name"]},
            "shared_alias_count": len(keys),
            "shared_aliases": sorted(keys)[:8],
            "action": "flagged for curator review; not merged",
            "why": "identifiers sharing this many aliases usually describe one substance",
        })
    findings.sort(key=lambda f: -f["shared_alias_count"])
    return findings


def _lookup(index: dict, text: str):
    return index.get(T.canonical_key(text), [])


def _fuzzy(index_keys: list[str], key_to_label: dict, text: str):
    key = T.canonical_key(text)
    if len(key) < MIN_FUZZY_LEN:
        return None, 0
    hit = process.extractOne(key, index_keys, scorer=fuzz.WRatio,
                             score_cutoff=FUZZY_REVIEW_THRESHOLD)
    if not hit:
        return None, 0
    best_key, score, _ = hit
    # guard against short-string coincidences: lengths must be comparable
    if abs(len(best_key) - len(key)) > max(3, 0.35 * len(key)):
        return None, 0
    # numeric guard: "interleukin-12" and "interleukin-2" are one character apart
    # and are different molecules. Any disagreement in the digits is decisive.
    if re.findall(r"\d+", key) != re.findall(r"\d+", best_key):
        return None, 0
    return best_key, score


# Dictionary entries that are real molecules but far too generic to be matched
# from inside a longer phrase. "Standard platinum-based chemotherapy" contains
# the token "platinum", but it describes a regimen class, not the element.
GENERIC_FOR_CONTAINED = {
    "platinum", "endostatin", "epothilone", "interleukin", "interferon",
    "vitamin", "vitamine", "oxygen", "water", "glucose", "dextrose",
    "saline", "ethanol", "alcohol", "carbon", "iron", "zinc", "calcium",
    "magnesium", "potassium", "sodium", "phase", "base", "protein",
    "antibody", "vaccine", "cells", "cell",
}

# Tokens that may be left unexplained without indicating a dropped substance.
PARSE_FILLER = {
    "combo", "combination", "with", "group", "arm", "cohort", "dosing",
    "dose", "doses", "schedule", "finding", "triplet", "doublet", "standard",
    "based", "comparator", "control", "experimental", "active", "study",
    "treatment", "therapy", "chemo", "chemotherapy", "alone", "versus",
    "patients", "subjects", "label", "open", "part", "stage", "level",
    "weekly", "daily", "cycle", "cycles", "every", "after", "before",
    "recombinant", "human", "injection", "tablets", "tablet",
}


def _dropped_substances(text: str, matched_window: str, matched_drug: str,
                        index: dict) -> list[str]:
    """Tokens left over by a partial match that look like *another substance*.

    A leftover word only matters if it names something that was administered.
    Testing it against the dictionary -- rather than against an ever-growing
    list of filler words -- keeps the signal sharp: the flag fires for a dropped
    co-administered drug and stays quiet for "Phase", "Arm A" or "single agent".
    """
    used = {w.lower() for w in re.split(r"[\s\-/]+", matched_window) if w}
    out = []
    for tok in re.split(r"[\s\-/,:()]+", text):
        t = tok.strip()
        tl = t.lower()
        if not t or tl in used or tl in PARSE_FILLER:
            continue
        if len(re.sub(r"[^a-z]", "", tl)) < 4 and not T.is_dev_code(t):
            continue
        hits = index.get(T.canonical_key(t))
        if hits and {h["drug_id"] for h in hits} != {matched_drug}:
            out.append(t)
        elif T.is_dev_code(t):
            out.append(t)
    return out


MAX_SEGMENT_WINDOW = 6


def smart_tokens(text: str, index: dict) -> list[str]:
    """Tokenise without destroying development codes.

    'BMS-986504' must stay one token while 'Docetaxel-Carboplatin' must become
    two. The dictionary itself decides: a hyphenated token is only split when it
    is neither a development code nor a term the dictionary already knows.
    """
    out: list[str] = []
    for tok in re.split(r"[\s/;]+", text):
        tok = tok.strip(" ,:()[]")
        if not tok:
            continue
        if "-" in tok and not T.is_dev_code(tok) and T.canonical_key(tok) not in index:
            parts = [p for p in tok.split("-") if p]
            out.extend(parts if len(parts) > 1 else [tok])
        else:
            out.append(tok)
    return out


def segment_aliases(index: dict, text: str):
    """Greedy longest-match segmentation of a phrase against the dictionary.

    'Cisplatin Docetaxel Gefitinib Pemetrexed Vinorelbine Gemcitabine' has no
    separator at all, yet names six substances. Matching only the first one and
    discarding the rest would produce a record that looks complete and is not --
    the most dangerous kind of error, because nothing downstream can detect it.
    """
    tokens = smart_tokens(text, index)
    found: list[dict] = []
    leftover: list[str] = []
    i = 0
    while i < len(tokens):
        matched = False
        # "18F-thymidine": the token after an isotope label is the tracer moiety,
        # not an administered drug, so it must not be matched on its own.
        if i > 0 and T.is_isotope_label(tokens[i - 1]):
            leftover.append(tokens[i])
            i += 1
            continue
        for size in range(min(MAX_SEGMENT_WINDOW, len(tokens) - i), 0, -1):
            window = " ".join(tokens[i:i + size])
            key = T.canonical_key(window)
            if len(key) < MIN_CONTAINED_LEN or key in GENERIC_FOR_CONTAINED:
                continue
            hits = index.get(key)
            if hits and len({h["drug_id"] for h in hits}) == 1:
                found.append({"window": window, "hits": hits})
                i += size
                matched = True
                break
        if not matched:
            leftover.append(tokens[i])
            i += 1
    return found, leftover


def _raw_parts_by_cleaned(raw: str, parts: list[str]) -> dict[str, str]:
    """Map each cleaned combination part back to the raw text it came from."""
    if len(parts) <= 1:
        return {}
    raw_parts = T.split_combination(raw)
    out: dict[str, str] = {}
    for rp in raw_parts:
        cleaned = T.clean_surface(rp)["cleaned"] or rp
        for cp in T.split_combination(cleaned):
            ck = T.canonical_key(cp)
            for p in parts:
                if p not in out and T.canonical_key(p) == ck:
                    out[p] = rp
    return out


def resolve_drug_string(raw: str, dic: dict, index_keys: list[str],
                        target_keys: set | None = None) -> dict:
    """Resolve one intervention string into one or more component resolutions."""
    index = dic["index"]
    out = {"raw": raw, "components": []}

    cleaned_doc = T.clean_surface(raw)
    base = cleaned_doc["cleaned"] or raw
    parts = T.split_combination(base)
    if len(parts) > 1:
        cleaned_doc["rules"].append("split_combination")

    # A placebo-controlled arm is not a drug-free arm. "placebo plus docetaxel"
    # really did administer docetaxel, while "placebo to match ZD6474" did not
    # administer anything. Blocking the whole string is safe for the second case
    # and silently destroys a true exposure in the first, so the two are split:
    # a placebo joined by a combination separator means co-administration, a
    # placebo naming its reference drug does not.
    if T.is_placebo(raw):
        # Only a single-component string is a whole reference arm. In a
        # combination, "cisplatin + placebo to match pembrolizumab" really did
        # give cisplatin; the placebo part is blocked on its own below.
        reference_arm = len(parts) == 1
        if reference_arm:
            out["components"].append({
                "component": raw, "tier": TIER_BLOCKED_PLACEBO, "drug_id": None,
                "score": None, "rules": ["placebo_guard", "placebo_reference_arm"],
                "note": "placebo arm naming its reference drug - no exposure",
            })
            return out
        cleaned_doc["rules"].append("placebo_co_administration_split")

    # drugs a placebo part says it imitates ("placebo to match X" -> X)
    referenced: set[str] = set()
    if T.is_placebo(raw) and T.has_placebo_reference_marker(raw):
        for p in parts:
            if T.is_placebo(p):
                target = T.RE_PLACEBO_REFERENCE.sub(" ", p)
                target = T.RE_PLACEBO.sub(" ", target).strip(" ,;:-")
                if target and target != p:
                    for c in resolve_drug_string(target, dic, index_keys,
                                                 target_keys)["components"]:
                        if c.get("drug_id"):
                            referenced.add(c["drug_id"])

    # Each cleaned part is paired with the uncleaned text it came from. Cleaning
    # removes "liposomal" as a formulation word, so the distinct-product guard
    # on a cleaned part could not see it: "liposomal doxorubicin" was blocked
    # alone and accepted as plain doxorubicin once "and cisplatin" was added.
    # The same pairing keeps a bracketed code attached to its own component.
    raw_of = _raw_parts_by_cleaned(raw, parts)

    for part in parts:
        if T.is_placebo(part):
            out["components"].append({
                "component": part, "tier": TIER_BLOCKED_PLACEBO, "drug_id": None,
                "score": None,
                "rules": list(cleaned_doc["rules"]) + ["placebo_guard"],
                "note": "placebo component of a combination arm",
            })
            continue
        rules = list(cleaned_doc["rules"])
        res = {"component": part, "tier": TIER_UNRESOLVED, "drug_id": None,
               "score": None, "rules": rules, "matched_alias": None,
               "candidates": None}

        # The class check runs on the surface *before* cleaning as well as after.
        # clean_surface strips "therapy" and "treatment" as regimen words, so
        # "Radiation therapy" arrives here as "Radiation" and could never reach
        # its own guard. An adversarial review found three CLASS_TERMS entries
        # that were dead code for exactly this reason.
        raw_part = raw_of.get(part, part) if len(parts) > 1 else raw
        if T.is_negated(raw_part) or T.is_negated(part):
            res["tier"] = TIER_BLOCKED_NEGATED
            res["rules"].append("negation_guard")
            res["note"] = "negated substance: the arm records its absence"
            out["components"].append(res)
            continue
        if (T.is_class_term(part) or T.is_class_term(raw_part)
                or T.is_class_like(part) or T.is_class_like(raw_part)):
            res["tier"] = TIER_BLOCKED_CLASS
            res["rules"].append("class_term_guard")
            res["note"] = "category term, not an identifiable substance"
            out["components"].append(res)
            continue

        # A biosimilar, a differently-formulated product or a sponsor-specific
        # version is a *different* regulatory entity from the originator, even
        # though the molecule name matches. Resolving "Bevacizumab Biosimilar
        # HLX04" to BEVACIZUMAB asserts that Henlius sponsors trials of
        # Genentech's product and makes the actual asset disappear. The
        # vocabulary has no identifier for these, so the honest answer is a
        # refusal with a reason code, not the originator.
        if T.is_distinct_product(raw_part) or T.is_distinct_product(part):
            res["tier"] = TIER_BLOCKED_DISTINCT_PRODUCT
            res["rules"].append("distinct_product_guard")
            res["note"] = ("distinct product (biosimilar or alternative "
                           "formulation); not the originator molecule and not "
                           "in this vocabulary")
            out["components"].append(res)
            continue

        # a radiolabelled tracer is its own entity; its unlabelled moiety is not
        # the administered drug, so no component of it may be matched
        if (T.is_radiotracer(part) or T.is_isotope_label(part)
                or T.is_radiotracer(raw_part)):
            res["tier"] = TIER_BLOCKED_CLASS
            res["rules"].append("radiotracer_guard")
            res["note"] = ("radiolabelled tracer or isotope label, not a "
                           "therapeutic exposure")
            out["components"].append(res)
            continue

        # 1. direct hit on the raw component. An ester form may only match a
        # record whose preferred name it is (the ester's own molecule), never a
        # synonym listed under the parent steroid.
        hits = _lookup(index, part)
        if hits and T.RE_ESTER_FORM.search(part):
            hits = [h for h in hits if h["alias_type"] == "preferred_name"]
        tier = None
        if hits:
            tier = (TIER_EXACT if any(h["alias_type"] == "preferred_name" for h in hits)
                    else TIER_ALIAS)

        # 1b. a target/gene symbol is not a drug ("PD-1", "EGFR")
        if not hits and target_keys and T.canonical_key(part) in target_keys:
            res["tier"] = TIER_BLOCKED_TARGET
            res["note"] = "a target or gene symbol, not an administered substance"
            res["rules"].append("target_symbol_guard")
            out["components"].append(res)
            continue

        # 2. parenthetical code names, e.g. "ZD6474 (ZACTIMA)"
        if not hits:
            own_parens = (cleaned_doc["parentheticals"] if len(parts) == 1
                          else T.clean_surface(raw_part)["parentheticals"])
            for p in own_parens:
                if T.is_isotope_label(p):
                    rules.append("isotope_label_skipped")
                    continue
                hits = _lookup(index, p)
                if hits:
                    tier = TIER_PAREN
                    rules.append("match_on_parenthetical")
                    res["component"] = p
                    break

        # 3. salt-stripped
        if not hits:
            desalted, fired = T.strip_salt(part)
            if fired and desalted:
                hits = _lookup(index, desalted)
                if hits:
                    tier = TIER_SALT
                    rules.append("match_after_salt_strip")

        # 3b. an originator's FDA suffix ("cemiplimab-rwlc")
        if not hits:
            inn = T.strip_fda_suffix(part)
            if inn:
                hits = _lookup(index, inn)
                if hits:
                    tier = TIER_CLEANED
                    rules.append("strip_fda_suffix")

        # 4. development code with a trailing lot/format number
        if not hits:
            core = T.dev_code_core(part)
            if core:
                hits = _lookup(index, core)
                if hits:
                    tier = TIER_CLEANED
                    rules.append("strip_dev_code_suffix")

        # 4b. a phosphate or succinate ester is its own molecule; without a
        # vocabulary entry for it the honest answer is unresolved, not the
        # parent steroid that segmentation or fuzzy matching would find
        if not hits and T.RE_ESTER_FORM.search(part):
            res["rules"].append("ester_form_not_salt")
            res["note"] = ("covalent ester (prodrug) form; not stripped as a "
                           "salt and not in this vocabulary as written")
            out["components"].append(res)
            continue

        # 5. dictionary-driven segmentation of an unseparated phrase
        if not hits:
            found, leftover = segment_aliases(index, part)
            if found:
                emitted_ids = set()
                for f in found:
                    did = f["hits"][0]["drug_id"]
                    if did in emitted_ids:
                        continue
                    emitted_ids.add(did)
                    out["components"].append({
                        "component": f["window"],
                        "tier": TIER_CONTAINED,
                        "drug_id": did,
                        "score": None,
                        "rules": rules + ["segmented_from_phrase"],
                        "matched_alias": f["hits"][0]["alias"],
                        "candidates": None,
                        "note": f"segmented out of {part!r}",
                    })
                residue = [t for t in leftover
                           if T.is_dev_code(t) or len(re.sub(r"[^A-Za-z]", "", t)) >= 5]
                residue = [t for t in residue if t.lower() not in PARSE_FILLER]
                if residue:
                    out["components"].append({
                        "component": " ".join(residue),
                        "tier": TIER_UNRESOLVED,
                        "drug_id": None,
                        "score": None,
                        "rules": rules + ["segmentation_residue"],
                        "matched_alias": None,
                        "candidates": None,
                        "note": "left over after segmentation; reported rather "
                                "than dropped, so the gap stays visible",
                    })
                continue

        # 6. fuzzy -- never for development codes, where one character apart is a
        #    different molecule and string similarity is actively misleading
        if not hits:
            if T.is_dev_code(part):
                res["rules"].append("dev_code_no_fuzzy")
                res["note"] = ("alphanumeric development code: approximate matching "
                               "disabled to avoid binding to a neighbouring code")
            else:
                best_key, score = _fuzzy(index_keys, index, part)
                if best_key:
                    hits = index[best_key]
                    tier = TIER_FUZZY if score >= FUZZY_AUTO_THRESHOLD else TIER_REVIEW
                    res["score"] = round(float(score), 1)
                    rules.append("fuzzy_match")

        if hits:
            distinct = {h["drug_id"] for h in hits}
            if len(distinct) > 1:
                res["tier"] = TIER_AMBIGUOUS
                res["candidates"] = sorted(distinct)
                res["note"] = f"surface form maps to {len(distinct)} molecules"
            else:
                res["tier"] = tier or TIER_ALIAS
                res["drug_id"] = hits[0]["drug_id"]
                res["matched_alias"] = hits[0]["alias"]
        out["components"].append(res)

    # A placebo that names its reference drug blocks that drug wherever else it
    # appears in the string ("Placebo to Match AZD9291, Osimertinib" lists one
    # drug twice), but not a different drug the arm really received.
    if referenced:
        for c in out["components"]:
            if c.get("drug_id") in referenced:
                c.update({"tier": TIER_BLOCKED_PLACEBO, "drug_id": None,
                          "note": "the drug this arm's placebo imitates - no exposure"})
                c.setdefault("rules", []).append("placebo_reference_match")

    return out


# --------------------------------------------------------------------------- #
# disease dictionary
# --------------------------------------------------------------------------- #
def build_disease_dictionary(disease: dict) -> dict:
    aliases = [disease["name"]]
    for s in (disease.get("synonyms") or []):
        if s.get("relation") == "hasExactSynonym":
            aliases.extend(s.get("terms") or [])
    # hand-added surface forms seen in registry free text that MONDO does not
    # carry verbatim. Listed explicitly so the addition is auditable.
    curated = [
        "non small cell lung cancer", "non-small-cell lung cancer",
        "nonsmall cell lung cancer", "non small-cell lung cancer",
        "carcinoma, non-small-cell lung", "nsclc", "non-small cell lung cancer (nsclc)",
        "non-small cell lung cancer nsclc", "lung cancer, non-small cell",
        "non-small cell carcinoma of the lung", "nsclc adenocarcinoma",
        "advanced non-small cell lung cancer", "metastatic non-small cell lung cancer",
        "lung non-small cell carcinoma", "lung neoplasms, non-small cell",
    ]
    index = {}
    for a in aliases:
        index[T.canonical_key(a)] = {"alias": a, "source": "mondo_exact_synonym"}
    for a in curated:
        index.setdefault(T.canonical_key(a), {"alias": a, "source": "curated"})
    return {"disease_id": disease["id"], "name": disease["name"], "index": index}


RE_STAGE_NOISE = re.compile(
    r"\b(?:stage\s*[0ivx]+[ab]?|advanced|metastatic|recurrent|locally\s+advanced|"
    r"unresectable|resectable|relapsed|refractory|early[-\s]stage|newly\s+diagnosed|"
    r"previously\s+treated|untreated|patients?\s+with|subjects?\s+with)\b",
    re.I,
)


def resolve_condition(raw: str, ddic: dict) -> dict:
    key = T.canonical_key(raw)
    if key in ddic["index"]:
        return {"raw": raw, "disease_id": ddic["disease_id"], "tier": TIER_EXACT,
                "rules": [], "score": 100.0}
    stripped = RE_STAGE_NOISE.sub(" ", raw or "")
    stripped = T.RE_MULTISPACE.sub(" ", stripped).strip(" ,;-")
    if T.canonical_key(stripped) in ddic["index"]:
        return {"raw": raw, "disease_id": ddic["disease_id"], "tier": TIER_CLEANED,
                "rules": ["strip_stage_modifier"], "score": 100.0}
    keys = list(ddic["index"].keys())
    hit = process.extractOne(T.canonical_key(stripped or raw), keys,
                             scorer=fuzz.WRatio, score_cutoff=FUZZY_REVIEW_THRESHOLD)
    if hit:
        best, score, _ = hit
        tier = TIER_FUZZY if score >= FUZZY_AUTO_THRESHOLD else TIER_REVIEW
        return {"raw": raw, "disease_id": ddic["disease_id"], "tier": tier,
                "rules": ["strip_stage_modifier", "fuzzy_match"],
                "score": round(float(score), 1)}
    return {"raw": raw, "disease_id": None, "tier": TIER_UNRESOLVED,
            "rules": ["strip_stage_modifier"], "score": None,
            "note": "condition outside the NSCLC scope of this build"}


# --------------------------------------------------------------------------- #
# company normalisation
# --------------------------------------------------------------------------- #
# A legal form is noise wherever it appears: "Merck Sharp & Dohme LLC Rahway NJ"
# and "Merck Sharp & Dohme" are the same sponsor.
CORP_SUFFIXES = [
    "incorporated", "inc", "corporation", "corp", "company", "co", "limited",
    "ltd", "llc", "l.l.c", "plc", "gmbh", "ag", "a/s", "as", "ab", "nv", "n.v",
    "bv", "b.v", "sa", "s.a", "sas", "spa", "s.p.a", "oy", "kk", "k.k",
    "pty", "pte", "srl", "s.r.l", "aps", "holding", "holdings",
]

# A sector word is noise only at the END. Stripped from anywhere it mangles
# the names of academic bodies, which carry the same words structurally:
# "Alliance For Clinical Trials In Oncology" became "Alliance For Clinical
# Trials In", and "Spanish Lung Cancer Group" became "Spanish Lung Cancer".
SECTOR_SUFFIXES = [
    "group", "pharmaceuticals", "pharmaceutical", "pharma", "pharmacueticals",
    "biosciences", "bioscience", "biotech", "biotechnology", "biopharma",
    "biopharmaceuticals", "biopharmaceutical", "therapeutics", "laboratories",
    "laboratory", "labs", "lab", "oncology", "sciences", "science",
    "international", "usa", "us", "global", "worldwide", "r&d",
    "research and development",
]

LEGAL_SUFFIXES = CORP_SUFFIXES + SECTOR_SUFFIXES

# Markers of an academic body, cooperative group or learned society. For these
# the sector word is part of the name, not a suffix on the end of it.
RE_ACADEMIC_BODY = re.compile(
    r"\b(?:alliance|society|societ[ae]|foundation|consortium|cooperative|"
    r"collaborative|intergroup|network|association|federation|college|"
    r"academy|council|institute|institut|university|universit[aey]|hospital|"
    r"hopital|hospitalier|clinic|centre|center|centro|ministry|department|"
    r"fondazione|fundacion|gruppo|grupo|groupe|group|programme|trials?)\b", re.I)

# A name that ends in a connective after a strip is a name we cut into.
RE_DANGLING_TAIL = re.compile(
    r"\b(?:in|for|of|and|on|at|to|the|a|an|de|del|della|du|des|von|van)$", re.I)

# Hand-curated corporate groupings. Deliberately small and explicit: an
# automatic parent-company inference would be guesswork without a licensed
# ownership dataset, and a wrong merge is worse than no merge.
CURATED_PARENTS = {
    "genentech": "Roche",
    "hoffmannlaroche": "Roche",
    "roche": "Roche",
    "chugai": "Roche",
    # The two Mercks are different companies. Merck & Co (Rahway, NJ) trades as
    # MSD outside North America; Merck KGaA (Darmstadt) trades as EMD Serono in
    # North America. Mapping "merck*" to one group merges two competitors, so
    # the Darmstadt names are listed separately and the bare key "merck" is
    # deliberately absent — an unqualified "Merck" is genuinely ambiguous and
    # is left unparented rather than guessed.
    "merckshampdohme": "Merck & Co",
    "merckshapdohme": "Merck & Co",
    "merckshampdohmellc": "Merck & Co",
    "msd": "Merck & Co",
    "mercksharpdohme": "Merck & Co",
    "merckcoinc": "Merck & Co",
    # Schering-Plough is in CURATED_SAME_ENTITY (renamed Merck & Co). The bare
    # key "schering" used to match Bayer Schering Pharma and Schering AG too.
    "prometheusbiosciences": "Merck & Co",
    "merckkgaa": "Merck KGaA",
    "emdserono": "Merck KGaA",
    "merckserono": "Merck KGaA",
    "merckhealthcarekgaa": "Merck KGaA",
    "bristolmyerssquibb": "Bristol Myers Squibb",
    "celgene": "Bristol Myers Squibb",
    "juno": "Bristol Myers Squibb",
    "mirati": "Bristol Myers Squibb",
    "turningpoint": "Bristol Myers Squibb",
    "rayzebio": "Bristol Myers Squibb",
    "astrazeneca": "AstraZeneca",
    "medimmune": "AstraZeneca",
    "acerta": "AstraZeneca",
    "alexion": "AstraZeneca",
    "elilillyand": "Eli Lilly",
    "elililly": "Eli Lilly",
    "lilly": "Eli Lilly",
    "loxo": "Eli Lilly",
    "pfizer": "Pfizer",
    "wyeth": "Pfizer",
    "array": "Pfizer",                    # Array BioPharma; exact match only
    "seagen": "Pfizer",
    "novartis": "Novartis",
    # "sandoz" deliberately absent: Sandoz was spun off as the independent
    # Sandoz Group AG in October 2023 and is no longer a Novartis subsidiary.
    # A corporate map is a dated assertion, not a fact, so it carries a
    # review date and the ones that changed are removed rather than kept.
    "sanofi": "Sanofi",
    "aventis": "Sanofi",
    "genzyme": "Sanofi",
    "takeda": "Takeda",
    "millennium": "Takeda",
    "ariad": "Takeda",
    "boehringeringelheim": "Boehringer Ingelheim",
    "johnsonjohnson": "Johnson & Johnson",
    "janssen": "Johnson & Johnson",
    "glaxosmithkline": "GSK",
    "gsk": "GSK",
    "amgen": "Amgen",
    "bayer": "Bayer",
    "daiichisankyo": "Daiichi Sankyo",
    "daiichi": "Daiichi Sankyo",          # Daiichi Pharmaceutical, merged 2005
    "eisai": "Eisai",
    "beonemedicines": "BeOne Medicines",
    "jiangsuhengrui": "Jiangsu Hengrui",
    "innovent": "Innovent",
    "junshi": "Junshi",
    "yuhan": "Yuhan",
    "hanmi": "Hanmi",
}

# One legal entity under several names. These are applied to the key *before*
# the parent lookup, so the names land on one node instead of one name being
# made the parent of the other. An earlier version put them in CURATED_PARENTS,
# and the graph then asserted "BeOne Medicines PARENT_OF BeiGene" -- a rename
# recorded as an ownership relation. Only renames and plain short forms of the
# same company belong here; a subsidiary, however wholly owned, does not.
CURATED_SAME_ENTITY = {
    "beigene": "beonemedicines",        # renamed BeOne Medicines, 2025
    "beone": "beonemedicines",
    "lilly": "elililly",
    "elilillyand": "elililly",          # "Eli Lilly and Company" after stripping
    "gsk": "glaxosmithkline",
    # Schering-Plough was the legal survivor of the 2009 merger and renamed
    # itself Merck & Co., Inc.; it is that company, not a subsidiary of it
    "scheringplough": "merckco",
    "hoffmannlaroche": "roche",
    "hengrui": "jiangsuhengrui",
}

# Map keys shorter than this are only ever matched exactly. A short key used as
# a prefix catches unrelated firms ("juno" would take any "Juno..." company).
MIN_PREFIX_KEY = 5


# A credential suffix, or a bare two-to-three word personal name, is a person
# rather than an organisation. Organisation names almost always carry a
# structural word; a person's name almost never does.
RE_CREDENTIAL = re.compile(
    r"\b(?:m\.?d\.?|ph\.?d\.?|d\.?o\.?|m\.?b\.?b\.?s\.?|r\.?n\.?|"
    r"pharm\.?d\.?|m\.?sc\.?|prof|dr)\b\.?\s*$", re.I)
ORG_WORDS = {
    "university", "universite", "universidad", "universitat", "universitario",
    "hospital", "hospitalier", "clinic", "clinica", "institute", "institut",
    "instituto", "center", "centre", "centro", "college", "school", "academy",
    "foundation", "trust", "council", "ministry", "department", "division",
    "network", "group", "alliance", "society", "association", "consortium",
    "cooperative", "federation", "organisation", "organization", "agency",
    "board", "authority", "service", "services", "health", "medical",
    "cancer", "oncology", "research", "sciences", "science", "laboratory",
    "laboratories", "pharmaceuticals", "pharma", "biosciences", "therapeutics",
    "inc", "llc", "ltd", "gmbh", "corporation", "company", "co", "limited",
    "national", "international", "regional", "general", "memorial", "royal",
    "state", "city", "county", "affiliated", "teaching", "military", "army",
    "veterans", "childrens", "women", "womens", "st", "saint", "holdings",
    "clinical", "trials", "trial", "worldwide", "global", "partners",
    "solutions", "consulting", "pharma", "bio", "labs", "lab", "care",
    "therapy", "therapies", "diagnostics", "systems", "technologies",
}


def looks_like_person(raw: str) -> bool:
    """True when a sponsor string names an individual, not an organisation."""
    name = (raw or "").strip()
    if not name:
        return False
    if RE_CREDENTIAL.search(name):
        return True
    # Nothing else is claimed. A bare two-word capitalised name is genuinely
    # ambiguous -- "Xiuning Le" is a person and "Shanghai Henlius" is a
    # company, and no rule over the string alone separates them. An earlier
    # version guessed from the shape and typed Accuray, Daiichi Sankyo and
    # Siemens Molecular Imaging as people. Without a source that distinguishes
    # them, the honest output is the default type, so only an explicit
    # credential counts and the rest stay Company with the limitation recorded.
    return False


def normalize_company(raw: str) -> dict:
    name = (raw or "").strip()
    text = re.sub(r"[.,]", " ", name.lower())
    text = T.RE_MULTISPACE.sub(" ", text).strip()
    rules = []
    # A legal form is noise wherever it sits, so those are removed anywhere.
    for suf in sorted(CORP_SUFFIXES, key=len, reverse=True):
        rx = re.compile(rf"\b{re.escape(suf)}\b", re.I)
        if rx.search(text):
            text = rx.sub(" ", text)
            if "strip_legal_suffix" not in rules:
                rules.append("strip_legal_suffix")
    text = T.RE_MULTISPACE.sub(" ", text).strip(" -,&")
    # A sector word is noise on a company name and load-bearing on an academic
    # one: "Hellenic Oncology Research Group" and "Spanish Lung Cancer Group"
    # are the organisation's actual name, and stripping the tail leaves
    # "Hellenic" and "Spanish Lung Cancer". So sector stripping is skipped
    # entirely for names carrying an academic or cooperative-group marker, and
    # any strip that leaves a dangling connective is reverted as evidence that
    # the cut landed inside the name rather than after it.
    if not RE_ACADEMIC_BODY.search(text):
        for _ in range(4):
            for suf in sorted(SECTOR_SUFFIXES, key=len, reverse=True):
                rx = re.compile(rf"(?:^|\s|[,.]){re.escape(suf)}\s*$", re.I)
                if not rx.search(text) or len(text) <= len(suf) + 1:
                    continue
                candidate = rx.sub("", text).strip(" ,.-&")
                if RE_DANGLING_TAIL.search(candidate) or len(candidate) < 3:
                    continue
                text = candidate
                if "strip_sector_suffix" not in rules:
                    rules.append("strip_sector_suffix")
                break
            else:
                break
    text = T.RE_MULTISPACE.sub(" ", text).strip(" -,&")
    # stripping a sector word can leave the connector that introduced it
    # ("Eli Lilly and Company" -> "Eli Lilly and"), so tidy the seam
    text = re.sub(r"\s+\b(?:a|an)\s+\w+$", "", text, flags=re.I)   # "Genzyme a Sanofi"
    text = re.sub(r"\s*\([a-z0-9\-]{2,8}\)\s*$", "", text, flags=re.I)  # trailing acronym
    text = re.sub(r"\s+(?:and|&|a|an|the|of|for)$", "", text, flags=re.I)
    text = T.RE_MULTISPACE.sub(" ", text).strip(" -,&")
    key = T.canonical_key(text)
    if re.search(r"\bmerck\s*(?:&|and)\s*co\b", name, re.I):
        key = "merckco"
        rules.append("curated_same_entity")
    for k, same in sorted(CURATED_SAME_ENTITY.items(), key=lambda kv: -len(kv[0])):
        if key.startswith(same):
            break                       # already the current name
        if key == k or (len(k) >= MIN_PREFIX_KEY and key.startswith(k)):
            key = same + key[len(k):]
            rules.append("curated_same_entity")
            break
    parent = None
    # Exact key first, then the longest map key that is a *prefix of this
    # name* ("mercksharpdohmecorp" -> "mercksharpdohme"). The reverse test --
    # this name being a prefix of a map key -- was removed: "Merck & Co., Inc."
    # reduces to "merck" once the legal suffixes go, "merckkgaa" starts with
    # "merck", and the American company was made a subsidiary of its German
    # competitor. A short name that matches nothing exactly stays unparented.
    match = CURATED_PARENTS.get(key)
    if match is None:
        for k, p in sorted(CURATED_PARENTS.items(), key=lambda kv: -len(kv[0])):
            if len(k) >= MIN_PREFIX_KEY and key.startswith(k):
                match = p
                break
    # a company is not its own parent; the map exists to connect distinct
    # legal entities, not to restate one
    if match is not None and _same_entity_key(T.canonical_key(match)) != key:
        parent = match
        rules.append("curated_parent_map")
    # The organisation keeps its own name. A corporate parent is a *relationship*,
    # not a rename: collapsing MedImmune into "AstraZeneca" produces two nodes
    # with one label, and any lookup by name then silently picks one of them.
    display = " ".join(w.capitalize() if w.islower() else w for w in text.split()) or name
    return {"raw": name, "key": key or T.canonical_key(name),
            "display": display, "parent": parent, "rules": rules}


# --------------------------------------------------------------------------- #
# pipeline
# --------------------------------------------------------------------------- #
def main() -> None:
    disease, disease_fetched, _ = _load("disease")
    drug_rows, drugs_fetched, _ = _load("drugs")
    target_rows, targets_fetched, _ = _load("targets")
    trials, trials_fetched, _ = _load("trials")

    print("building drug dictionary ...")
    dic = build_drug_dictionary(drug_rows)
    n_alias = sum(len(v["aliases"]) for v in dic["drugs"].values())
    raw_ambiguous = sum(1 for v in dic["index"].values()
                        if len({e["drug_id"] for e in v}) > 1)
    print(f"  {len(dic['drugs'])} molecules, {n_alias} aliases, "
          f"{len(dic['index'])} lookup keys, {raw_ambiguous} ambiguous before curation")

    print("curating dictionary ...")
    dict_findings = dic.pop("build_findings") + curate_dictionary(dic)
    dup_findings = detect_duplicate_entities(dic)
    index_keys = list(dic["index"].keys())
    ambiguous = {k: v for k, v in dic["index"].items()
                 if len({e["drug_id"] for e in v}) > 1}
    by_type: dict[str, int] = defaultdict(int)
    for f in dict_findings + dup_findings:
        by_type[f["type"]] += 1
    for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}")
    print(f"  {len(index_keys)} lookup keys after curation, "
          f"{len(ambiguous)} still ambiguous")

    ddic = build_disease_dictionary(disease)
    print(f"  disease dictionary: {len(ddic['index'])} surface forms")

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
    target_keys -= set(dic["index"].keys())   # a term that is also a drug stays a drug
    print(f"  target guard vocabulary: {len(target_keys)} symbols")

    print("resolving trial records ...")
    resolved_trials = []
    drug_cache: dict[str, dict] = {}
    cond_cache: dict[str, dict] = {}
    comp_cache: dict[str, dict] = {}

    for s in trials:
        p = s.get("protocolSection", {})
        nct = p.get("identificationModule", {}).get("nctId")
        if not nct:
            continue
        sc = p.get("sponsorCollaboratorsModule", {}) or {}
        lead = sc.get("leadSponsor") or {}
        collabs = sc.get("collaborators") or []

        def company(entry):
            nm = entry.get("name")
            if not nm:
                return None
            if nm not in comp_cache:
                c = normalize_company(nm)
                c["class"] = entry.get("class")
                comp_cache[nm] = c
            return comp_cache[nm]

        ivs = []
        for iv in (p.get("armsInterventionsModule", {}) or {}).get("interventions", []) or []:
            if iv.get("type") not in ("DRUG", "BIOLOGICAL"):
                continue
            surface = iv.get("name") or ""
            if surface not in drug_cache:
                drug_cache[surface] = resolve_drug_string(surface, dic, index_keys, target_keys)
            r = dict(drug_cache[surface])
            # registry-declared other names are a free, high-quality alias source
            others = []
            for o in (iv.get("otherNames") or []):
                if o not in drug_cache:
                    drug_cache[o] = resolve_drug_string(o, dic, index_keys, target_keys)
                others.append(drug_cache[o])
            r["other_names"] = others
            r["intervention_type"] = iv.get("type")
            ivs.append(r)

        conds = []
        for c in (p.get("conditionsModule", {}) or {}).get("conditions", []) or []:
            if c not in cond_cache:
                cond_cache[c] = resolve_condition(c, ddic)
            conds.append(cond_cache[c])

        resolved_trials.append({
            "nct_id": nct,
            "title": p.get("identificationModule", {}).get("briefTitle"),
            "status": p.get("statusModule", {}).get("overallStatus"),
            "why_stopped": p.get("statusModule", {}).get("whyStopped"),
            "start_date": (p.get("statusModule", {}).get("startDateStruct") or {}).get("date"),
            "phases": (p.get("designModule", {}) or {}).get("phases") or [],
            "enrollment": ((p.get("designModule", {}) or {}).get("enrollmentInfo") or {}).get("count"),
            "lead_sponsor": company(lead),
            "collaborators": [c for c in (company(x) for x in collabs) if c],
            "conditions": conds,
            "interventions": ivs,
        })

    out = {
        "_built_from": {
            "disease": disease_fetched, "drugs": drugs_fetched,
            "targets": targets_fetched, "trials": trials_fetched,
        },
        "disease": ddic,
        "dictionary": dic,
        "dictionary_findings": dict_findings,
        "duplicate_findings": dup_findings,
        "ambiguous_keys": {k: sorted({e["drug_id"] for e in v})
                           for k, v in ambiguous.items()},
        "targets": [
            {"target_id": r["target"]["id"],
             "symbol": r["target"]["approvedSymbol"],
             "name": r["target"]["approvedName"],
             "association_score": r["score"],
             "aliases": sorted({a["label"] for a in
                                (r["target"].get("synonyms") or []) +
                                (r["target"].get("symbolSynonyms") or []) +
                                (r["target"].get("nameSynonyms") or []) if a.get("label")})}
            for r in target_rows
        ],
        "trials": resolved_trials,
        "companies": comp_cache,
    }
    path = C.PROCESSED / "resolved.json"
    path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {path.relative_to(C.ROOT)}")

    # headline counters
    tiers: dict[str, int] = defaultdict(int)
    for t in resolved_trials:
        for iv in t["interventions"]:
            for c in iv["components"]:
                tiers[c["tier"]] += 1
    print("\nintervention component resolution tiers:")
    for k, v in sorted(tiers.items(), key=lambda x: -x[1]):
        print(f"  {v:6d}  {k}")


if __name__ == "__main__":
    main()
