"""Sentence-level claim check for a generated answer.

The name-and-number check in query.py catches invented drugs and invented
figures. It cannot catch a false statement built from true tokens:
"AstraZeneca has discontinued osimertinib", "osimertinib does not act on EGFR",
"osimertinib is safe for all patients". This module reads each sentence the way
a reviewer would ask of it: what does it claim, and which retrieved edge says so?

The rule is an allowlist, not a blocklist. The graph can only support three kinds
of relation (a drug acts on a target, a trial evaluates a drug, an organisation
sponsors trials of a drug) and the facts printed in the evidence statements
(phase, status, counts, drug type). A sentence passes only when

  * every relation it states holds, edge for edge, between the same entities in
    the retrieved evidence;
  * every remaining content word is either grammar from a short fixed list or
    appears in an evidence statement about one of the sentence's own entities.

Anything else is reported, with the reason. That makes the check strict on
purpose: a true clinical fact the graph does not hold ("osimertinib is
approved for EGFR-mutant NSCLC" if no approval is in the evidence) is reported
as unverifiable, because the graph cannot vouch for it. A reviewer then decides.

What it still cannot do: it reads words, not meaning. A sentence that reuses the
evidence's own words in a different arrangement within one entity's statement
("the trial is active, not recruiting" vs "not active") is judged on vocabulary;
negation words are always reported, which removes the worst case of this.
"""
from __future__ import annotations

import re

# relation verbs the graph can vouch for, by the relation that would support them
RELATION_WORDS = {
    "ACTS_ON": {"act", "acts", "acting", "target", "targets", "targeting", "targeted",
                "inhibit", "inhibits", "inhibiting", "inhibited", "inhibitor", "inhibitors",
                "block", "blocks", "blocking", "bind", "binds", "binding"},
    "EVALUATES": {"evaluate", "evaluates", "evaluated", "evaluating", "test", "tests",
                  "tested", "testing", "study", "studies", "studied", "studying",
                  "investigate", "investigates", "investigated", "investigating",
                  "assess", "assesses", "assessed", "assessing"},
    "SPONSORS_TRIAL_OF": {"sponsor", "sponsors", "sponsored", "sponsoring",
                          "run", "runs", "running", "conduct", "conducts",
                          "conducted", "conducting"},
}
VERB_TO_REL = {w: rel for rel, ws in RELATION_WORDS.items() for w in ws}

# words that change the meaning of whatever they touch; the graph stores only
# positive edges, so it can never confirm an absence, a ranking or a guess
NEGATION = {"not", "no", "never", "none", "neither", "nor", "without", "cannot",
            "lack", "lacks", "lacking", "absent", "fail", "fails", "failed", "n't"}
COMPARISON = {"more", "less", "fewer", "most", "least", "best", "worst", "better",
              "worse", "superior", "inferior", "than", "only", "first", "largest",
              "smallest", "leading", "top", "main", "major", "primary"}
HEDGE = {"may", "might", "could", "likely", "possibly", "probably", "suggest",
         "suggests", "appears", "appear", "seems", "seem", "expected", "potential",
         "potentially", "promising"}
# the graph holds sponsorship; whether a sponsor develops a drug is a different
# claim that a cooperative group sponsoring a generic contradicts
DEVELOP = {"develop", "develops", "developing", "developed", "developer",
           "developers", "owns", "own", "owned", "markets", "market", "marketed",
           "makes", "made", "manufactures", "manufactured"}

# grammar and domain words that carry no claim of their own
FUNCTION = set("""
a an the and or of in on at to for by with from as into within across per
is are was were be been being has have had it its this that these those there
which who whom whose what where when also both each all any some several various
including include includes included such following listed list here
nsclc non small cell lung cancer carcinoma tumour tumor disease
trial trials study clinical phase phases stage stages max maximum
drug drugs agent agents molecule molecules compound compounds therapy therapies
treatment treatments substance substances medicine medicines
organisation organisations organization organizations company companies
sponsor sponsors lead lead-sponsor sponsorship
graph evidence record records data according source sources retrieved
known reported shown show shows mechanism mechanisms profile findings scope
edge edges does do did will would can should has have had
""".split())

STEM_SUPPORT = {"approved": "approval", "approve": "approval", "approves": "approval",
                "recruits": "recruiting", "recruit": "recruiting",
                "terminates": "terminated", "withdrawn": "withdrawn",
                "completes": "completed", "complete": "completed"}

RE_NCT = re.compile(r"\bNCT\d{8}\b", re.I)
RE_CITE = re.compile(r"\[[^\]]*\]")
RE_NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?![\w])")
RE_PHASE = re.compile(r"\bphase\s*(?:(\d)(?:\s*/\s*(\d))?|(i{1,3})\b)", re.I)
ROMAN = {"i": "1", "ii": "2", "iii": "3"}


def _norm(s: str) -> str:
    return re.sub(r"[\s_\-]+", "", s.lower())


def _has(label: str, low: str) -> bool:
    """Whole-word containment: "ALK" must not match "alkylating"."""
    return re.search(rf"(?<![a-z0-9]){re.escape(label.lower())}(?![a-z0-9])", low) is not None


RE_WORD = re.compile(r"[a-z]+(?:_[a-z]+)*(?:'[a-z]+)?|n't")


def _units(text: str) -> list[tuple[int, str]]:
    """(line number, fragment). Fragments of one line share a subject."""
    out = []
    for i, line in enumerate(RE_CITE.sub(" ", text).splitlines()):
        for p in re.split(r"(?<=[.!?;])\s+|\s+-\s+(?=[A-Z])", line):
            p = p.strip(" -•*\t")
            if re.search(r"[A-Za-z]", p):
                out.append((i, p))
    return out


def check_claims(text: str, evidence: list, linker) -> list[dict]:
    """Return one finding per unsupported claim. `linker(sentence)` -> entities."""
    statements = [(e.relation, (e.statement or "").lower(), _norm(e.statement or ""))
                  for e in evidence]
    findings: list[dict] = []
    prev_line, prev_ents = None, []

    for line_no, sent in _units(text):
        # A registry id is a trial, never a drug alias, whatever the dictionary says.
        ents = [e for e in linker(RE_NCT.sub(" ", sent))
                if e.get("type") not in ("Refused", "Disease")]
        for nct in RE_NCT.findall(sent):
            ents.append({"type": "Trial", "label": nct.upper(), "matched_text": nct})
        if ents:
            prev_line, prev_ents = line_no, ents
        elif line_no == prev_line:
            ents = prev_ents          # "...; 0 NSCLC trials" still means that drug

        # A named trial is the most specific subject: its phase and status are
        # its own, not those of another trial of the same drug.
        trials = [e for e in ents if e["type"] == "Trial"]
        labels = {e["label"].lower() for e in (trials or ents)}
        about = [s for s in statements if any(_has(l, s[1]) for l in labels)]
        about_tokens: set[str] = set()
        for s in about:
            about_tokens |= set(RE_WORD.findall(s[1]))
        about_phrases = " " + re.sub(r"[^a-z0-9]+", " ",
                                     " ".join(s[1] for s in about).replace("_", " ")) + " "

        def flag(kind, value, why):
            findings.append({"kind": kind, "value": value, "sentence": sent, "why": why})

        def quoted(w: str, words: list[str], i: int) -> bool:
            """The word sits in a phrase an evidence statement about these entities uses."""
            grams = []
            if i + 1 < len(words):
                grams.append(f"{w} {words[i + 1]}")
            if i > 0:
                grams.append(f"{words[i - 1]} {w}")
            return any(f" {g.replace('_', ' ')} " in about_phrases for g in grams)

        masked = sent
        for e in sorted(ents, key=lambda e: -len(e.get("matched_text") or "")):
            mt = e.get("matched_text")
            if mt:
                masked = re.sub(re.escape(mt), " ", masked, flags=re.I)
        masked = RE_NCT.sub(" ", masked)
        words = RE_WORD.findall(masked.lower().replace("’", "'"))

        # 1. relations: every pair the sentence names must hold in the evidence
        rels = {VERB_TO_REL[w] for w in words if w in VERB_TO_REL}
        by_type: dict[str, list[str]] = {}
        for e in ents:
            by_type.setdefault(e["type"], []).append(e["label"])
        pairs_for = {"ACTS_ON": ("Drug", "Target"), "EVALUATES": ("Trial", "Drug"),
                     "SPONSORS_TRIAL_OF": ("Company", "Drug")}
        for rel in sorted(rels):
            a, b = pairs_for[rel]
            if rel == "EVALUATES" and "Trial" not in by_type:
                # "X is evaluated in NSCLC trials": a retrieved statement must put
                # X in trials (a trial edge, or a sponsorship of trials of X)
                for d in by_type.get("Drug", []):
                    if not any(r in ("EVALUATES", "SPONSORS_TRIAL_OF") and _has(d, low)
                               for r, low, _ in statements):
                        flag("relation", f"{d} evaluated in trials",
                             "no retrieved trial evaluates this drug")
                continue
            for x in by_type.get(a, []):
                for y in by_type.get(b, []):
                    if not any(r == rel and _has(x, low) and _has(y, low)
                               for r, low, _ in statements):
                        flag("relation", f"{x} — {rel.lower().replace('_', ' ')} — {y}",
                             "no retrieved edge links these two entities this way")

        # 2. words the graph can never vouch for, unless quoting the evidence
        special = [(NEGATION, "negation", "the graph stores only relations that exist; "
                    "it cannot confirm an absence or a failure"),
                   (COMPARISON, "comparison", "a ranking or comparison is not a "
                    "relation the graph holds"),
                   (HEDGE, "speculation", "a guess about what may be true is not in "
                    "the evidence"),
                   (DEVELOP, "development_claim", "the graph records trial sponsorship, "
                    "which is not evidence of developing, owning or marketing a drug")]
        for i, w in enumerate(words):
            for vocab, kind, why in special:
                if (w in vocab or (kind == "negation" and w.endswith("n't"))) \
                        and not quoted(w, words, i):
                    flag(kind, w, why)

        # 3. phases attach to an entity: "phase 3" must be that entity's phase
        for m in RE_PHASE.finditer(sent):
            ph = [p for p in (m.group(1), m.group(2)) if p] or [ROMAN[m.group(3).lower()]]
            if not any(all(f"phase{p}" in s[2] for p in ph) for s in about):
                flag("phase", m.group(0), "no evidence statement about this "
                                          "sentence's entities gives that phase")

        # 4. a count of trials attaches to an entity too
        for m in re.finditer(r"(\d[\d,]*)\s+(?:\w+\s+){0,2}trials?\b", sent, re.I):
            if re.search(r"phase\s*$", sent[:m.start()], re.I):
                continue
            n = m.group(1).replace(",", "")
            pat = rf"(?<![\d.]){re.escape(n)}\s+(?:\S+\s+){{0,2}}trial"
            if not any(re.search(pat, s[1].replace(",", "")) for s in about):
                flag("count", m.group(0), "no evidence statement about this "
                                          "sentence's entities gives that count")

        # 5. every other content word must be grammar or the entity's own evidence
        claimed = NEGATION | COMPARISON | HEDGE | DEVELOP | set(VERB_TO_REL)
        for w in sorted(set(words)):
            if w in claimed or w.endswith("n't") or w in FUNCTION or len(w) < 2:
                continue
            if STEM_SUPPORT.get(w, w) in about_tokens or w in about_tokens:
                continue
            flag("wording", w, "this word makes a claim no evidence statement about "
                               "the sentence's entities supports")
    return findings
