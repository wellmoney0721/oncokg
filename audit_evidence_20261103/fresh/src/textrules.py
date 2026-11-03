"""Surface-form cleaning rules.

Every rule is named and returns the name when it fires, so a resolution can be
explained after the fact ("this matched only after the salt form was stripped").
That traceability is the point: an unexplainable match cannot be reviewed, and an
unreviewable pipeline cannot be trusted with reference data.
"""
from __future__ import annotations

import re
import unicodedata

# --------------------------------------------------------------------------- #
# vocabulary of noise
# --------------------------------------------------------------------------- #

# Dose / schedule fragments: "100 mg", "30mg/m2", "5 mg/kg", "q3w", "BID"
RE_DOSE = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:mg|g|mcg|µg|ug|ng|iu|u|ml|l)\s*(?:/\s*(?:m2|m\^2|m²|kg|day|d|wk|week))?\b",
    re.I,
)
RE_PERCENT = re.compile(r"\b\d+(?:[.,]\d+)?\s*%")
RE_SCHEDULE = re.compile(
    r"\b(?:q\d+[dwh]|q\.?\s?[dwh]\.?|b\.?i\.?d\.?|t\.?i\.?d\.?|q\.?i\.?d\.?|"
    r"qd|bid|tid|qid|prn|p\.?o\.?|iv|i\.v\.?|sc|s\.c\.?|im|i\.m\.?|"
    r"once\s+daily|twice\s+daily|single\s+dose|loading\s+dose)\b",
    re.I,
)
RE_CYCLE = re.compile(r"\b(?:cycle|cohort|arm|dose\s*level|part|group)\s*[-\s]?[0-9ivxab]+\b", re.I)

FORMULATIONS = [
    "film-coated tablets", "film coated tablets", "enteric-coated",
    "capsules", "capsule", "tablets", "tablet", "injection", "infusion",
    "solution", "suspension", "powder", "lyophilized", "ointment", "gel",
    "cream", "patch", "aerosol", "inhalation", "sustained release",
    "extended release", "oral", "intravenous", "subcutaneous", "intramuscular",
    "intrathecal", "topical", "sterile", "concentrate", "vial", "syringe",
    "prefilled", "liposomal", "liposome", "nanoparticle", "albumin-bound",
]

SALTS = [
    "hydrochloride", "hydrobromide", "hcl", "mesylate", "mesilate", "maleate",
    "dimaleate", "tosylate", "tosilate", "besylate", "besilate", "sulfate",
    "sulphate", "sodium", "potassium", "calcium", "magnesium", "citrate",
    "fumarate", "succinate", "phosphate", "diphosphate", "tartrate",
    "bitartrate", "acetate", "trifluoroacetate", "lactate", "malate",
    "oxalate", "nitrate", "carbonate", "chloride", "bromide", "iodide",
    "monohydrate", "dihydrate", "trihydrate", "anhydrous", "hemihydrate",
    "ethanolate", "solvate", "free base", "base",
]

REGIMEN_WORDS = [
    "monotherapy", "mono therapy", "maintenance", "induction", "consolidation",
    "preoperative", "postoperative", "perioperative", "neoadjuvant", "adjuvant",
    "concurrent", "sequential", "first-line", "first line", "second-line",
    "second line", "salvage", "re-challenge", "rechallenge", "continuation",
    "treatment", "therapy", "regimen", "administration", "dosing",
]

# Strings that are a *category*, not an identifiable substance. Matching these to
# a specific molecule would be a fabricated fact, so they are rejected outright.
CLASS_TERMS = {
    "chemotherapy", "concurrent chemotherapy", "platinum based chemotherapy",
    "platinum-based chemotherapy", "platinum doublet", "doublet chemotherapy",
    "standard chemotherapy", "systemic chemotherapy", "combination chemotherapy",
    "standard of care", "soc", "standard treatment", "best supportive care",
    "supportive care", "observation", "no intervention", "control",
    "radiotherapy", "radiation therapy", "chemoradiotherapy", "surgery",
    "immunotherapy", "targeted therapy", "anti-pd-1 monoclonal antibody",
    "anti-pd-1 antibody", "anti-pd-l1 antibody", "pd-1 inhibitor",
    "pd-l1 inhibitor", "egfr-tki", "egfr tki", "tki", "tyrosine kinase inhibitor",
    "checkpoint inhibitor", "immune checkpoint inhibitor", "antibiotics",
    "vitamin", "normal saline", "saline", "vehicle", "comparator",
    "active comparator", "investigational product", "study drug", "study treatment",
    "placebo", "matching placebo", "placebo comparator",
    # added after an adversarial review found these falling through to
    # UNRESOLVED with no guard and no reason code
    "platinum", "platinum doublet chemotherapy", "platinum-doublet chemotherapy",
    "platinum agent", "platinum compound", "platinum chemotherapy",
    "anti-pd-1", "anti-pd-l1", "anti-ctla-4", "anti-vegf", "anti-her2",
    "pd-1 blockade", "pd-l1 blockade", "pd-1/pd-l1 inhibitor",
    "vegf inhibitor", "vegfr inhibitor", "egfr inhibitor", "alk inhibitor",
    "ros1 inhibitor", "met inhibitor", "kras inhibitor", "braf inhibitor",
    "mek inhibitor", "parp inhibitor", "cdk4/6 inhibitor", "her2 inhibitor",
    "antibody-drug conjugate", "antibody drug conjugate", "adc",
    "bispecific antibody", "monoclonal antibody", "car-t", "car-t cells",
    "car-t cell therapy", "car t cell therapy", "cell therapy", "gene therapy",
    "oncolytic virus", "cancer vaccine", "dendritic cell vaccine",
    "stereotactic body radiotherapy", "sbrt", "radiation", "irradiation",
    "thoracic radiotherapy", "best available therapy", "physician's choice",
    "investigator's choice", "standard", "targeted",
}

# A category pattern, rather than an exact category string. A head noun like
# "inhibitor" or "blockade" qualified by a gene or pathway is a class, whatever
# the qualifier is, so the exact-membership set above can never be complete.
RE_CLASS_PATTERN = re.compile(
    r"^(?:[A-Za-z0-9\-/\s]{2,40}?)\s*"
    r"(?:inhibitors?|blockades?|antagonists?|agonists?|modulators?|"
    r"chemotherapy|chemotherapies|immunotherapy|immunotherapies|"
    r"radiotherapy|regimens?|doublets?|triplets?|backbones?|"
    r"antibod(?:y|ies)|conjugates?|vaccines?|inhibition)$",
    re.I,
)

# Words that make the pattern above a *product* rather than a class: a named
# molecule qualified by a form word is still that molecule.
RE_CLASS_PATTERN_EXEMPT = re.compile(
    r"\b(?:mab|nib|tinib|ciclib|parib|zomib|sertib|degib|rafenib)\b", re.I)


def is_class_like(text: str) -> bool:
    """True for a category description that no single molecule can satisfy."""
    t = (text or "").strip()
    if not t or RE_CLASS_PATTERN_EXEMPT.search(t):
        return False
    return bool(RE_CLASS_PATTERN.match(t))


# A biosimilar, a nanoparticle/liposomal/pegylated reformulation, or a
# sponsor-suffixed version is a separate regulatory product from the
# originator. The molecule name is the same; the asset is not.
RE_DISTINCT_PRODUCT = re.compile(
    r"\bbio[\s\-]?similar\b"
    r"|\bbio[\s\-]?betters?\b"
    r"|\bfollow[\s\-]?on\s+biologic\b"
    r"|\bnab[\s\-]"
    r"|\bnanoparticle\s+albumin[\s\-]?bound\b"
    r"|\balbumin[\s\-]?bound\b"
    r"|\bliposomal\b|\bpegylated\b|\bpeg(?:ylated)?[\s\-]r?h?[a-z]{1,6}\b"
    r"|\bgeneric\s+version\b"
    r"|\b(?:injection|solution|product)\s+of\s+[a-z]+mab\b",
    re.I,
)

# "Bevacizumab-Pfizer", "Trastuzumab-dkst": a hyphenated sponsor or FDA
# four-letter biosimilar suffix on an INN stem.
RE_BIOSIMILAR_SUFFIX = re.compile(
    r"^[A-Za-z]{6,}(?:mab|cept|tinib|ase)\s*[\-–]\s*[A-Za-z]{2,12}$", re.I)


def is_distinct_product(text: str) -> bool:
    """True when the string names a product that is not the originator."""
    t = (text or "").strip()
    if not t:
        return False
    if RE_DISTINCT_PRODUCT.search(t):
        return True
    return bool(RE_BIOSIMILAR_SUFFIX.match(t))

# A placebo arm must never create a "this company administered this drug" edge.
RE_PLACEBO = re.compile(r"\bplacebo\b|\bsham\b|\bvehicle\s+control\b", re.I)

# Combination separators, longest first so "combined with" wins over "with".
RE_COMBO = re.compile(
    r"\s*(?:\+|&|,|、|，|/(?=\s*[A-Za-z])|\bcombined\s+with\b|"
    r"\bin\s+combination\s+with\b|\bcombination\s+with\b|\bplus\b|\band\b|\bor\b|"
    r"\bfollowed\s+by\b)\s*",
    re.I,
)

RE_PAREN = re.compile(r"\(([^()]*)\)|\[([^\[\]]*)\]")

# Development codes ("AZD9291", "BMS-986504", "PF-07224826", "TSC-204-A0201").
# One character apart is a different molecule, so these must never be matched
# approximately -- the usual string-similarity intuition is wrong here.
RE_DEV_CODE = re.compile(
    r"^[A-Za-z]{1,5}[\s\-]?\d{2,8}(?:[\s\-][A-Za-z0-9]{1,8})*$")

# Trailing lot/format suffixes that do not change the substance: "BMS-936558-01"
RE_DEV_CODE_SUFFIX = re.compile(r"^(?P<core>[A-Za-z]{1,5}[\s\-]?\d{3,8})[\s\-]0?\d{1,2}$")
RE_MULTISPACE = re.compile(r"\s+")
RE_PUNCT_EDGE = re.compile(r"^[\s\-–—,;:.、，。]+|[\s\-–—,;:.、，。]+$")


# Isotope labels on radiotracers: 18F, 68Ga, 99mTc, 177Lu, 64Cu, 89Zr, 131I.
# These look exactly like development codes but name an isotope, not a molecule,
# and the substance they label is usually not in a therapeutic vocabulary at all.
RE_ISOTOPE = re.compile(r"^\[?(\d{1,3}m?)[\s\-]?([A-Za-z]{1,2})\]?$")
ISOTOPE_ELEMENTS = {
    "f", "c", "n", "o", "ga", "cu", "zr", "i", "lu", "tc", "in", "y", "at",
    "ac", "pb", "re", "sm", "sr", "ra", "rb", "br", "h", "p", "s",
}


def is_isotope_label(text: str) -> bool:
    m = RE_ISOTOPE.match((text or "").strip())
    return bool(m and m.group(2).lower() in ISOTOPE_ELEMENTS)


# "[18F]F-AraG", "68Ga-DOTATATE": an isotope prefix marks the whole string as a
# radiolabelled tracer, whose unlabelled moiety is not the administered drug.
RE_RADIOTRACER = re.compile(
    r"(?:^|[\s\(\[])\[?\d{1,3}m?[\s\-]?[A-Za-z]{1,2}\]?\s*[-–]\s*\w", re.I)


def is_radiotracer(text: str) -> bool:
    t = (text or "").strip()
    m = RE_RADIOTRACER.search(t)
    if not m:
        return False
    head = re.match(r"^[\s\(\[]*\[?(\d{1,3})m?[\s\-]?([A-Za-z]{1,2})\]?", t)
    return bool(head and head.group(2).lower() in ISOTOPE_ELEMENTS)


def is_dev_code(text: str) -> bool:
    """True for alphanumeric development codes, where fuzzy matching is unsafe."""
    t = (text or "").strip()
    return bool(RE_DEV_CODE.match(t))


def dev_code_core(text: str) -> str | None:
    """Strip a trailing lot/format number: 'BMS-936558-01' -> 'BMS-936558'."""
    m = RE_DEV_CODE_SUFFIX.match((text or "").strip())
    return m.group("core") if m else None


def _strip_words(text: str, words: list[str]) -> tuple[str, bool]:
    fired = False
    for w in sorted(words, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(w)}\b", re.I)
        if pattern.search(text):
            text = pattern.sub(" ", text)
            fired = True
    return text, fired


def canonical_key(text: str) -> str:
    """Aggressive key used for dictionary lookup (never shown to a user)."""
    t = unicodedata.normalize("NFKD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = t.replace("’", "'").replace("‐", "-").replace("–", "-").replace("—", "-")
    t = re.sub(r"[^a-z0-9]+", "", t)
    return t


def clean_surface(raw: str) -> dict:
    """Clean one intervention string.

    Returns the cleaned text, the parenthetical fragments pulled out as extra
    lookup candidates, and the list of rules that fired.
    """
    rules: list[str] = []
    text = (raw or "").strip()

    parentheticals = [part.strip()
                      for groups in RE_PAREN.findall(text)
                      for part in groups if part and part.strip()]
    if parentheticals:
        rules.append("extract_parenthetical")
        text = RE_PAREN.sub(" ", text)

    for name, rx in (
        ("strip_dose", RE_DOSE),
        ("strip_percent", RE_PERCENT),
        ("strip_schedule", RE_SCHEDULE),
        ("strip_cycle", RE_CYCLE),
    ):
        if rx.search(text):
            text = rx.sub(" ", text)
            rules.append(name)

    text, fired = _strip_words(text, FORMULATIONS)
    if fired:
        rules.append("strip_formulation")
    text, fired = _strip_words(text, REGIMEN_WORDS)
    if fired:
        rules.append("strip_regimen_word")

    text = RE_MULTISPACE.sub(" ", text)
    text = RE_PUNCT_EDGE.sub("", text)

    return {"cleaned": text, "parentheticals": parentheticals, "rules": rules}


def strip_salt(text: str) -> tuple[str, bool]:
    out, fired = _strip_words(text, SALTS)
    out = RE_PUNCT_EDGE.sub("", RE_MULTISPACE.sub(" ", out))
    return out, fired


def split_combination(text: str) -> list[str]:
    """Split a combination string into component substances.

    Conservative: a split that produces an empty or 1-character part is discarded
    and the original string is kept whole, because an over-eager split invents
    substances that were never in the record.
    """
    parts = [p.strip() for p in RE_COMBO.split(text) if p and p.strip()]
    parts = [p for p in parts if len(p) > 1]
    if len(parts) <= 1:
        return [text]
    return parts


def is_placebo(text: str) -> bool:
    return bool(RE_PLACEBO.search(text or ""))


# "placebo for X", "placebo to match X", "matching placebo" -- X is the drug the
# placebo imitates, so X was NOT administered in this arm.
RE_PLACEBO_REFERENCE = re.compile(
    r"\bplacebo\b\s*(?:for|to\s+match(?:ed)?|matching|of|comparator\s+for)\b|"
    r"\b(?:match(?:ing|ed)?|mimic(?:king)?)\s+placebo\b",
    re.I,
)


def has_placebo_reference_marker(text: str) -> bool:
    return bool(RE_PLACEBO_REFERENCE.search(text or ""))


def is_class_term(text: str) -> bool:
    key = RE_PUNCT_EDGE.sub("", RE_MULTISPACE.sub(" ", (text or "").lower().strip()))
    if key in CLASS_TERMS:
        return True
    return canonical_key(key) in {canonical_key(c) for c in CLASS_TERMS}
