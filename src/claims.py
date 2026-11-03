"""Clause-level claim check for a generated answer.

The name-and-number check in query.py catches invented drugs and invented
figures. It cannot catch a false statement built from true tokens:
"AstraZeneca has discontinued osimertinib", "osimertinib does not act on EGFR",
"osimertinib is safe for all patients", "EGFR acts on osimertinib". This module
reads each clause the way a reviewer would: who is it about, what does it say
about them, and which retrieved statement says the same about the same entities?

A clause passes only when all of the following hold.

  * Its relations (acts on / inhibits / activates, evaluates, sponsors) run in the
    stated direction between the stated entities, and an evidence statement of that
    relation names both. Inhibiting or activating must match the stated action.
  * Its phase, status, counts and every other content word appear in an evidence
    statement that names every entity of the clause, so a value cannot be borrowed
    from another trial or drug mentioned in the same sentence or the same evidence.
  * It contains no negation, comparison, hedge or development/ownership claim. The
    graph stores relations that exist, nothing else.

A unit that is a verbatim copy of an evidence statement passes as it stands.
Pronouns ("it", "this drug") and elided subjects ("... and is phase 3") take the
subject of the clause before; with no antecedent they are reported. Text the check
cannot read (non-English letters) is reported, not skipped.

It is strict on purpose: a true fact the graph does not hold is reported as
unverifiable, and a reviewer decides. It still reads words, not meaning: a clause
whose words, entities and numbers all come from one evidence statement about
those entities, arranged into a different claim, can pass.
"""
from __future__ import annotations

import re
import unicodedata

# -- vocabulary --------------------------------------------------------------- #
# relation word -> (relation, required action, voice). Required action: None means
# any edge of that relation; "inhib" / "activ" must match the edge's action type.
_R = {}
for w in ("act acts acting target targets targeting bind binds binding "
          "modulate modulates modulating").split():
    _R[w] = ("ACTS_ON", None, "active")
for w in ("targeted bound modulated").split():
    _R[w] = ("ACTS_ON", None, "passive")
for w in ("inhibit inhibits inhibiting block blocks blocking inhibitor inhibitors "
          "inhibition blocker blockers antagonist antagonists antagonises "
          "antagonizes").split():
    _R[w] = ("ACTS_ON", "inhib", "active")
for w in ("inhibited blocked antagonised antagonized").split():
    _R[w] = ("ACTS_ON", "inhib", "passive")
for w in ("activate activates activating activator activators agonist agonists "
          "stimulates stimulate").split():
    _R[w] = ("ACTS_ON", "activ", "active")
for w in ("activated stimulated").split():
    _R[w] = ("ACTS_ON", "activ", "passive")
for w in ("evaluate evaluates evaluating test tests testing study studies "
          "studying investigate investigates investigating assess assesses "
          "assessing").split():
    _R[w] = ("EVALUATES", None, "active")
for w in ("evaluated tested studied investigated assessed").split():
    _R[w] = ("EVALUATES", None, "passive")
for w in ("sponsor sponsors sponsoring run runs running conduct conducts "
          "conducting lead leads leading").split():
    _R[w] = ("SPONSORS_TRIAL_OF", None, "active")
for w in ("sponsored conducted led").split():
    _R[w] = ("SPONSORS_TRIAL_OF", None, "passive")
RELATION = _R
NOUN_FORMS = {"inhibitor", "inhibitors", "inhibition", "blocker", "blockers",
              "antagonist", "antagonists", "activator", "activators", "agonist",
              "agonists", "sponsor"}
ROLES = {"ACTS_ON": ("Drug", "Target"), "EVALUATES": ("Trial", "Drug"),
         "SPONSORS_TRIAL_OF": ("Company", "Drug")}
ACTION_WORDS = {"inhib": ("inhibitor", "antagonist", "blocker", "negative"),
                "activ": ("activator", "agonist", "positive", "opener")}

NEGATION = {"not", "no", "never", "none", "neither", "nor", "without", "cannot",
            "lack", "lacks", "lacking", "absent", "fail", "fails", "failed",
            "non", "longer", "nothing", "nobody", "nowhere", "hardly", "barely",
            "unlike", "except", "instead", "rather", "stopped", "ceased"}
COMPARISON = {"more", "less", "fewer", "most", "least", "best", "worst", "better",
              "worse", "superior", "inferior", "than", "only", "first", "largest",
              "smallest", "leading", "top", "main", "major", "primary", "sole",
              "exclusively", "mainly", "mostly", "chiefly"}
HEDGE = {"may", "might", "could", "likely", "possibly", "probably", "suggest",
         "suggests", "appears", "appear", "seems", "seem", "expected", "potential",
         "potentially", "promising", "perhaps", "presumably", "reportedly",
         # modality: what a drug can, will or should do is not what an edge records
         "can", "will", "would", "should", "must", "shall"}
DEVELOP = {"develop", "develops", "developing", "developed", "developer",
           "developers", "owns", "own", "owned", "owner", "markets", "market",
           "marketed", "makes", "made", "manufactures", "manufactured", "sells",
           "sold", "commercialises", "commercializes", "originator", "invented"}

# grammar and neutral nouns that make no claim of their own
FUNCTION = set("""
a an the and or of in on at to for by with from as into within across per via
is are was were be been being has have had does do did
it its this that these those there which who whom whose what where when also
such following listed list here namely include includes including included
trial trials study studies clinical phase phases stage stages max maximum
drug drugs agent agents molecule molecules compound compounds substance substances
organisation organisations organization organizations company companies
sponsorship graph evidence record records data according source sources
retrieved known reported shown show shows mechanism mechanisms profile findings
scope edge edges among lists
""".split())
# words about the graph itself: a clause made only of these and a negation is a
# statement about what the graph can answer ("this graph cannot answer that")
META = set("""
graph question questions answer answers answered evidence retrieved scope outside
cover covers covered information available found find determine supporting support
i we this that there here
""".split())
ARTICLES = {"a", "an", "the", "its", "their", "his", "her"}
TRIAL_NOUNS = {"trial", "trials", "study", "studies"}
BE = {"is", "are", "was", "were", "be", "been", "being"}
PREDICATE = BE | {"has", "have", "had", "does", "do", "did"} | set(RELATION)
PRONOUN = {"it": None, "its": None, "they": None, "them": None, "their": None,
           "this drug": "Drug", "the drug": "Drug", "this agent": "Drug",
           "the agent": "Drug", "this molecule": "Drug", "this trial": "Trial",
           "the trial": "Trial", "this study": "Trial", "the study": "Trial",
           "this target": "Target", "the target": "Target",
           "this company": "Company", "the company": "Company",
           "the sponsor": "Company", "this sponsor": "Company"}
STEM_SUPPORT = {"approved": "approval", "approve": "approval", "approves": "approval",
                "recruits": "recruiting", "recruit": "recruiting",
                "terminates": "terminated", "completes": "completed",
                "complete": "completed"}
STATUS = ["active not recruiting", "not yet recruiting", "enrolling by invitation",
          "recruiting", "completed", "terminated", "withdrawn", "suspended",
          "unknown", "available", "no longer available", "temporarily not available"]
SCOPE_PHRASES = [r"non[\s\-]?small[\s\-]cell lung (?:cancer|carcinoma)s?", r"\bnsclc\b",
                 r"\blung (?:cancer|carcinoma)\b"]

RE_NCT = re.compile(r"\bNCT\d{8}\b", re.I)
RE_CITE = re.compile(r"\[\s*(?:(?:NCT\d{8}|CHEMBL\d+|ENSG\d+|PMID:?\s*\d+|ORG:[^\]]+)"
                     r"\s*[,;]?\s*)+\]", re.I)
RE_MDLINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
RE_PHASE = re.compile(r"\bphase\s*([0-9]+[a-z]?|i{1,3}v?|iv)\b(?:\s*/\s*([0-9]+[a-z]?|i{1,3}))?",
                      re.I)
ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4"}
RE_TOKEN = re.compile(r"\x00(\d+)\x00|\d+[a-z]+\b|\d[\d,]*(?:\.\d+)?%?|[a-z]+(?:_[a-z]+)*(?:'[a-z]+)?"
                      r"|n't|[,;:]")


def _flat(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower().replace("(s)", "s")).strip()


def _squash(s: str) -> str:
    return re.sub(r"[\s_\-]+", "", s.lower())


def _has(label: str, low: str) -> bool:
    """Whole-word containment: "ALK" must not match "alkylating"."""
    return re.search(rf"(?<![a-z0-9]){re.escape(label.lower())}(?![a-z0-9])", low) is not None


def _non_english(s: str) -> bool:
    return any(ord(c) > 127 and unicodedata.category(c).startswith("L") for c in s)


# -- units -------------------------------------------------------------------- #
def _units(text: str) -> list[tuple[str, str]]:
    """Sentences, with a list heading ("Agents acting on ALK:") joined to each item."""
    text = RE_MDLINK.sub(r"\1", text)
    text = RE_CITE.sub(" ", text)
    lines = [l.strip() for l in text.splitlines()]
    out: list[str] = []
    heading = None
    for line in lines:
        if not line:
            heading = None
            continue
        bullet = re.match(r"^(?:[-*•]|\d+[.)])\s+", line)
        body = line[bullet.end():] if bullet else line
        if bullet and heading:
            item = body.rstrip(".")
            slot = re.search(r"\b(?:these|the following|following)(?:\s+[A-Za-z]+)?",
                             heading, re.I)
            joined = (heading[:slot.start()] + item + heading[slot.end():] if slot
                      else f"{item} — {heading}")
            out.append((joined, body))
            continue
        if body.endswith(":") and not bullet:
            heading = body[:-1]
            continue
        heading = None
        # sentence ends: . ! ? followed by space, or ; outside parentheses
        depth, start = 0, 0
        for i, ch in enumerate(body):
            depth += ch == "("
            depth -= ch == ")"
            end = (ch in ".!?" and (i + 1 == len(body) or body[i + 1] == " ")
                   and not re.search(r"\b(?:vs|e\.g|i\.e|approx|no)\.?$", body[start:i], re.I))
            if end or (ch == ";" and depth <= 0):
                out.append((body[start:i + 1].strip(), body[start:i + 1].strip()))
                start = i + 1
        out.append((body[start:].strip(), body[start:].strip()))
    return [u for u in out if re.search(r"[^\W\d_]", u[0])]   # any letter, any script


# -- the check ---------------------------------------------------------------- #
def check_claims(text: str, evidence: list, linker) -> list[dict]:
    """Return one finding per unsupported claim. `linker(text)` -> entities."""
    statements = [(e.relation, (e.statement or "").lower()) for e in evidence]
    flat_statements = [_flat(s) for _, s in statements]
    findings: list[dict] = []
    last_by_type: dict[str, dict] = {}
    last_subject: dict | None = None

    for unit, bare in _units(text):
        def flag(kind, value, why, unit=unit):
            findings.append({"kind": kind, "value": value, "sentence": unit, "why": why})

        if _non_english(unit):
            flag("unreadable", unit[:40], "text in a language the check cannot read is "
                                          "not verified")
            continue
        # a verbatim copy of a whole evidence statement says exactly what it says
        if {_flat(unit), _flat(bare.rstrip("."))} & set(flat_statements):
            first = next(iter(linker(bare)), None)   # still an antecedent for "it"
            if first and first.get("type") not in ("Refused", "Disease"):
                last_subject = first
                last_by_type[first["type"]] = first
            continue

        toks, ents = _tokenise(unit, linker, last_by_type, last_subject)
        for clause in _clauses(toks):
            c_ents = [ents[t[1]] for t in clause if t[0] == "ENT"]
            gone = [e for e in c_ents if e.get("type") == "Missing"]
            words = [t[1] for t in clause if t[0] == "W"]
            if gone and len(gone) == len(c_ents) and all(
                    w in META or w in NEGATION or w in FUNCTION or w in BE
                    or w.endswith("n't") for w in words):
                continue                  # "it cannot answer this question"
            if gone:
                flag("no_antecedent", gone[0]["label"],
                     "a pronoun with nothing before it to refer to")
                continue
            pred = next((i for i, t in enumerate(clause)
                         if t[0] == "W" and t[1] in PREDICATE), len(clause))
            implicit = None
            if not any(t[0] == "ENT" for t in clause[:pred]):
                implicit = last_subject   # "... and is phase 3"
            subjects = c_ents + ([implicit] if implicit and implicit not in c_ents else [])
            if not subjects:
                words = [t[1] for t in clause if t[0] == "W"]
                content = [w for w in words if w not in FUNCTION and w not in BE]
                if content and not all(w in META or w in NEGATION or w.endswith("n't")
                                       for w in content):
                    flag("no_subject", " ".join(content[:6]),
                         "this clause names no entity the evidence can be checked against")
                continue
            labels = [e["label"].lower() for e in subjects]
            support = [s for _, s in statements if all(_has(l, s) for l in labels)]
            _check_relations(clause, toks, ents, implicit, statements, flag)
            _check_attributes(clause, ents, subjects[0], support, statements, flag)
            last_subject = c_ents[0] if c_ents else last_subject
            for e in c_ents:
                last_by_type[e["type"]] = e
    return findings


def _tokenise(unit, linker, last_by_type, last_subject):
    """Entities become placeholders, pronouns become their antecedent."""
    s = unit
    for pat in SCOPE_PHRASES:
        s = re.sub(pat, " ", s, flags=re.I)
    s = s.replace("(s)", "s").replace("’", "'")
    s = re.sub(r"[()\[\]{}\"*—–]", " ", s)
    ents: list[dict] = []
    spans = []
    for m in RE_NCT.finditer(s):
        spans.append((m.start(), m.end(), {"type": "Trial", "label": m.group(0).upper()}))
    # the linker strips only " ?.," from tokens, so "EGFR;" or "ALK:" would not link
    linked = linker(re.sub(r"[;:!]", " ", RE_NCT.sub(lambda m: " " * len(m.group(0)), s)))
    for e in linked:
        if e.get("type") in ("Disease",):
            continue
        mt = e.get("matched_text") or ""
        words = [re.escape(w) for w in mt.split()]
        if not words:
            continue
        pat = r"(?<![A-Za-z0-9])" + r"[\W_]+".join(words) + r"(?![A-Za-z0-9])"
        for m in re.finditer(pat, s, re.I):
            if not any(a < m.end() and m.start() < b for a, b, _ in spans):
                spans.append((m.start(), m.end(), e))
    # pronouns
    low = s.lower()
    for phrase, typ in sorted(PRONOUN.items(), key=lambda x: -len(x[0])):
        for m in re.finditer(rf"\b{re.escape(phrase)}\b", low):
            if any(a < m.end() and m.start() < b for a, b, _ in spans):
                continue
            after = low[m.end():]
            if re.match(r"\s+of\b", after) or any(
                    a >= m.end() and not s[m.end():a].strip(" ,") for a, _, _ in spans):
                continue                 # "the target of X", "the drug osimertinib"
            ante = last_by_type.get(typ) if typ else last_subject
            spans.append((m.start(), m.end(), ante or {"type": "Missing", "label": phrase}))
    spans.sort()
    out, last = [], 0
    for a, b, e in spans:
        out.append(s[last:a])
        out.append(f" \x00{len(ents)}\x00 ")
        ents.append(e)
        last = b
    out.append(s[last:])
    toks = []
    for m in RE_TOKEN.finditer("".join(out).lower()):
        if m.group(1) is not None:
            toks.append(("ENT", int(m.group(1))))
        elif m.group(0) in ",;:":
            toks.append(("P", m.group(0)))
        elif m.group(0)[0].isdigit():
            toks.append(("N", m.group(0).replace(",", "").rstrip("%")))
        else:
            toks.append(("W", m.group(0)))
    return toks, ents


def _clauses(toks):
    """Split at ; and at and/but/while/whereas when both sides have a predicate."""
    cuts = [-1]
    for i, t in enumerate(toks):
        if t == ("P", ";"):
            cuts.append(i)
        elif t[0] == "W" and t[1] in ("and", "but", "while", "whereas"):
            left = toks[cuts[-1] + 1:i]
            right = toks[i + 1:]
            nxt = next((j for j in range(i + 1, len(toks))
                        if toks[j][0] == "W" and toks[j][1] in ("and", "but", "while",
                                                               "whereas")
                        or toks[j] == ("P", ";")), len(toks))
            right = toks[i + 1:nxt]
            if any(x[0] == "W" and x[1] in PREDICATE for x in left) and \
                    any(x[0] == "W" and x[1] in PREDICATE for x in right):
                cuts.append(i)
    cuts.append(len(toks))
    return [toks[a + 1:b] for a, b in zip(cuts, cuts[1:]) if toks[a + 1:b]]


def _group(clause, k, step):
    """The run of entities nearest to position k in direction step, joined by , and or."""
    i = k + step
    while 0 <= i < len(clause) and clause[i][0] != "ENT":
        i += step
    grp = []
    while 0 <= i < len(clause):
        if clause[i][0] == "ENT":
            grp.append(clause[i][1])
            i += step
        elif clause[i] in (("P", ","), ("W", "and"), ("W", "or"), ("W", "as"),
                           ("W", "well")):
            i += step
        else:
            break
    return grp


def _after_group(clause, k):
    """Index just past the entity run that follows position k."""
    i = k + 1
    while i < len(clause) and clause[i][0] != "ENT":
        i += 1
    if i >= len(clause):
        return None
    while i < len(clause) and (clause[i][0] == "ENT" or clause[i] in (
            ("P", ","), ("W", "and"), ("W", "or"))):
        i += 1
    return i


def _check_relations(clause, toks, ents, implicit, statements, flag):
    for k, t in enumerate(clause):
        if t[0] != "W" or t[1] not in RELATION:
            continue
        rel, action, voice = RELATION[t[1]]
        if t[1] == "sponsor" and k and clause[k - 1] == ("W", "lead"):
            continue                       # "lead sponsor": one noun, handled at "lead"
        subj_t, obj_t = ROLES[rel]
        left = [ents[i] for i in _group(clause, k, -1)]
        right = [ents[i] for i in _group(clause, k, +1)]
        prev = clause[k - 1] if k else None
        nxt = clause[k + 1] if k + 1 < len(clause) else None
        noun = (t[1] in NOUN_FORMS or t[1] in ("target", "targets")) and (
            (prev and prev[0] == "W" and (prev[1] in ARTICLES or prev[1] in TRIAL_NOUNS))
            or nxt == ("W", "of") or nxt is None or (prev and prev[0] == "ENT"))
        if t[1] in NOUN_FORMS and prev and prev[0] == "ENT" and ents[prev[1]]["type"] == obj_t:
            right, left = [ents[prev[1]]], [ents[i] for i in _group(clause, k - 1, -1)]
        elif t[1] in ("target", "targets") and nxt == ("W", "of"):
            # "EGFR is the target of osimertinib" / "the target of osimertinib is EGFR"
            drug_side = right
            target_side = left
            if not target_side:
                after = _after_group(clause, k)
                if after is not None and after < len(clause) and clause[after][0] == "W" \
                        and clause[after][1] in BE:
                    target_side = [ents[i] for i in _group(clause, after, +1)]
            left, right = drug_side, target_side
        elif voice == "passive" and (
                any(x == ("W", b) for x in clause[max(0, k - 3):k] for b in BE)
                or nxt == ("W", "by")):
            left, right = right, left
        if not left and implicit:
            left = [implicit]
        if noun and (not left or not right):
            used = {id(e) for e in left + right}
            pool = [ents[x[1]] for x in clause if x[0] == "ENT" and id(ents[x[1]]) not in used]
            left = left or [e for e in pool if e["type"] == subj_t]
            right = right or [e for e in pool if e["type"] == obj_t]
        if rel == "EVALUATES" and not any(e["type"] == "Trial" for e in left + right):
            # without a named trial, the subject must be the word "trials" ("trials
            # evaluating X") or the drug must be the grammatical object ("X is tested")
            passive = voice == "passive" and (
                any(x == ("W", b) for x in clause[max(0, k - 3):k] for b in BE)
                or nxt == ("W", "by"))
            trial_subject = any(x[0] == "W" and x[1] in TRIAL_NOUNS
                                for x in clause[max(0, k - 3):k])
            objs = right if (passive or trial_subject) else []
            if not (passive or trial_subject):
                flag("relation_direction", f"{'/'.join(e['label'] for e in left)} {t[1]}",
                     "trials evaluate drugs; this sentence has something else evaluating")
                continue
            if not objs or any(e["type"] != "Drug" for e in objs):
                flag("relation_incomplete", t[1], "an evaluation relation whose object is "
                                                  "not a drug")
                continue
            drugs = objs
            for d in drugs:
                if not any(r in ("EVALUATES", "SPONSORS_TRIAL_OF") and _has(d["label"], s)
                           for r, s in statements):
                    flag("relation", f"{d['label']} evaluated in trials",
                         "no retrieved trial evaluates this drug")
            continue
        if not left or not right:
            flag("relation_incomplete", t[1], "a relation whose two sides could not both "
                                              "be identified in the sentence")
            continue
        if any(e["type"] != subj_t for e in left) or any(e["type"] != obj_t for e in right):
            flag("relation_direction",
                 f"{'/'.join(e['label'] for e in left)} {t[1]} "
                 f"{'/'.join(e['label'] for e in right)}",
                 f"this relation runs from a {subj_t.lower()} to a {obj_t.lower()}; "
                 "the sentence has it the other way or between the wrong kinds")
            continue
        for x in left:
            for y in right:
                hits = [s for r, s in statements if r == rel and _has(x["label"], s)
                        and _has(y["label"], s)]
                if not hits:
                    flag("relation", f"{x['label']} — {t[1]} — {y['label']}",
                         "no retrieved edge links these two entities this way")
                elif action and not any(any(a in s for a in ACTION_WORDS[action])
                                        for s in hits):
                    flag("action", f"{x['label']} {t[1]} {y['label']}",
                         "the evidence gives a different or no action type")


def _owner(clause, ents, i, prefer):
    """The entity a value at position i belongs to: nearest in `prefer` direction first."""
    order = [range(i + 1, len(clause)), range(i - 1, -1, -1)]
    if prefer == "before":
        order.reverse()
    for rng in order:
        for j in rng:
            if clause[j][0] == "ENT":
                return ents[clause[j][1]]
    return None


def _check_attributes(clause, ents, subject, support, statements, flag):
    def scoped(i, prefer):
        """Evidence statements naming the clause subject and the value's own entity."""
        own = _owner(clause, ents, i, prefer) or subject
        names = {own["label"].lower(), subject["label"].lower()}
        return [s for _, s in statements if all(_has(n, s) for n in names)]

    words = [t[1] for t in clause if t[0] == "W"]
    joined = " ".join(words)
    sup_tokens: set[str] = set()
    for s in support:
        sup_tokens |= set(re.findall(r"[a-z]+(?:_[a-z]+)*", s))
    sup_flat = " " + " ".join(_flat(s) for s in support) + " "
    sup_squash = "".join(_squash(s) for s in support)

    # status phrases are one claim, in the registry's spelling
    for st in STATUS:
        if re.search(rf"\b{st}\b", joined):
            if f" {st} " not in sup_flat or (st == "recruiting" and not re.search(
                    r"(?<!not )(?<!yet )\brecruiting\b",
                    sup_flat.replace("active not recruiting", "")
                    .replace("not yet recruiting", ""))):
                flag("status", st, "no evidence statement about these entities gives "
                                   "that status")
            joined = re.sub(rf"\b{st}\b", " ", joined)
    words = joined.split()

    i = 0
    while i < len(clause):
        t = clause[i]
        if t == ("W", "phase"):
            j = i + 1
            nums = []
            while j < len(clause) and clause[j][0] in ("N", "W") and len(nums) < 2:
                v = clause[j][1]
                if clause[j][0] == "N" or v in ROMAN or re.fullmatch(r"\d+[a-z]", v):
                    nums.append(ROMAN.get(v, v))
                    j += 1
                elif v in ("or", "to"):
                    j += 1
                else:
                    break
            if nums:
                key = "phase" + "".join(nums)
                own = "".join(_squash(s) for s in scoped(i, "before"))
                if key not in own and not all(f"phase{n}" in own for n in nums):
                    flag("phase", "phase " + "/".join(nums), "no evidence statement about "
                         "these entities gives that phase")
                i = j
                continue
        if t[0] == "N":
            n = t[1]
            own = " ".join(_flat(s) for s in scoped(i, "after")).replace(",", "")
            if not re.search(rf"(?<![\d.]){re.escape(n)}(?![\d.])", own):
                flag("number", n, "no evidence statement about these entities gives "
                                  "that figure")
        if t[0] == "W" and re.fullmatch(r"\d+[a-z]", t[1]):
            flag("number", t[1], "a figure with a suffix the evidence does not use")
        i += 1

    seen = set()
    for w in words:
        if w in seen:
            continue
        seen.add(w)
        for vocab, kind, why in (
                (NEGATION, "negation", "the graph stores only relations that exist; it "
                                       "cannot confirm an absence or a failure"),
                (COMPARISON, "comparison", "a ranking or comparison is not a relation "
                                           "the graph holds"),
                (HEDGE, "speculation", "a guess about what may be true is not in the "
                                       "evidence"),
                (DEVELOP, "development_claim", "the graph records trial sponsorship, "
                                               "which is not evidence of developing, "
                                               "owning or marketing a drug")):
            if w in vocab or (kind == "negation" and (w.endswith("n't") or
                                                       w.startswith("non_"))):
                flag(kind, w, why)
                break
        else:
            if w in RELATION or w in FUNCTION or w in BE or len(w) < 2:
                continue
            if w in sup_tokens or STEM_SUPPORT.get(w) in sup_tokens:
                continue
            flag("wording", w, "this word makes a claim no evidence statement about "
                               "these entities supports")
