"""Clause-level claim check for a generated answer.

The name-and-number check in query.py catches invented drugs and invented
figures. It cannot catch a false statement built from true tokens:
"AstraZeneca has discontinued osimertinib", "osimertinib does not act on EGFR",
"osimertinib is safe for all patients", "EGFR acts on osimertinib". This module
reads each clause the way a reviewer would: who is it about, what does it say
about them, and which retrieved statement says the same about the same entities?

What the check asks of each clause (a description of the rules, not a guarantee;
see the last paragraph):

  * Relations (acts on / inhibits / activates, evaluates, sponsors) are read by
    position: the entities before the relation word are its subject, the ones after
    its object, reversed for a passive ("is inhibited by") and for "target of".
    Both sides must be named (or be the subject carried over from the clause before),
    must be the right kinds (a drug acts on a target, a trial evaluates a drug, a
    company sponsors trials of a drug), and an evidence statement of that relation
    must name both. Inhibit/activate must match the edge's action type.
  * In a clause that states a relation, every entity it names must be part of a
    relation that was checked.
  * A phase belongs to the trials named just before it (a run joined by "and" shares
    it), else to a drug's maximum stage; a figure belongs to the nearest entity after
    it and must appear in evidence naming that entity and the clause's subject; a
    trial count must appear as a trial count, a percentage as a percentage.
  * A status belongs to the trial named before it. Words naming a kind of thing
    ("drug", "company", "trial") need an entity of that kind or evidence about its
    trials; "NSCLC" may only qualify trials the evidence calls NSCLC trials, never an
    approval. A word naming a kind belongs to the entity just before it ("EGFR is a
    drug" is reported). A trial count in a clause naming several drugs needs a count
    per drug. Two different entities on either side of a verb that is no relation
    ("X is Y") are reported. A plural pronoun, an elided subject after a group, and an
    "it" after a group are checked once for every entity they stand for. Letters
    spelled out one by one are reported. A heading's determiner ("these", "the
    following") is replaced by the item, but adjectives in it stay and are checked.
  * Every other content word must appear in evidence naming every entity of the
    clause.
  * Negations, comparisons, hedges and modal verbs, and claims of developing,
    owning or marketing are reported; so are distinct products the resolver refuses,
    pronouns with nothing to refer to, and text that is not English.

Exceptions, all narrow: a line that is a copy of a whole evidence statement (case
and punctuation aside) passes as it stands, though any heading above it is still
checked; a clause that names no entity and uses only words about the graph itself
("this graph cannot answer that question") passes; a bracket is dropped as a
citation only when every id in it is a record of the retrieved evidence.

It is strict on purpose: a true fact the graph does not hold is reported as
unverifiable, and a reviewer decides. It reads words and their order, not meaning,
so a sentence it cannot parse into the shapes above can be misread; the known
residue is listed in the README (known defect 13).
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
# nouns naming the one who acts: "an EGFR inhibitor", "an inhibitor of EGFR"
AGENT_NOUNS = {"inhibitor", "inhibitors", "inhibition", "blocker", "blockers",
               "antagonist", "antagonists", "activator", "activators", "agonist",
               "agonists"}
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
phase phases stage stages max maximum
sponsorship graph evidence record records recorded data according source sources
retrieved known reported shown show shows mechanism mechanisms profile findings
scope edge edges among lists
""".split())
# a clause with no entity, no figure, and only these words is a statement about the
# graph ("this graph cannot answer that question"), not about the world
META_OK = set("""
graph question questions answer answers answered evidence retrieved scope outside
cover covers covered information available found find determine supporting support
i we this that there here it is are be been was can cannot not no n't do does
a an the of for to in from with so and or any contain contains contained needed relevant
records recorded record lists listed holds hold about
""".split())
META_ANCHOR = {"graph", "evidence", "question", "questions", "information"}
# a word naming a kind of thing is a claim that the thing is of that kind
KIND_WORDS = {
    **{w: "Drug" for w in "drug drugs agent agents molecule molecules compound "
                          "compounds substance substances medicine medicines".split()},
    **{w: "Company" for w in "company companies organisation organisations "
                             "organization organizations".split()},
    **{w: "trials" for w in "trial trials clinical".split()},
}
ARTICLES = {"a", "an", "the", "its", "their", "his", "her"}
TRIAL_NOUNS = {"trial", "trials", "study", "studies"}
BE = {"is", "are", "was", "were", "be", "been", "being"}
PASSIVE_GAP = {"being", "been", "also", "still", "currently", "now", "already",
               "reportedly", "directly", "selectively"}
GROUP_GLUE = {("P", ","), ("W", "and"), ("W", "or"), ("W", "as"), ("W", "well"),
              ("W", "on"), ("W", "of"), ("W", "to"), ("W", "also"), ("W", "both"),
              ("W", "either")}
PREDICATE = BE | {"has", "have", "had", "does", "do", "did"} | set(RELATION)
PLURAL = {"they", "them", "their"}
PRONOUN = {"it": None, "its": None, "they": None, "them": None, "their": None,
           "this drug": "Drug", "the drug": "Drug", "this agent": "Drug",
           "the agent": "Drug", "this molecule": "Drug", "this trial": "Trial",
           "the trial": "Trial", "this study": "Trial", "the study": "Trial",
           "this target": "Target", "the target": "Target",
           "this company": "Company", "the company": "Company",
           "this organisation": "Company", "this organization": "Company",
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
# a citation is a bracket holding only record ids; anything else stays text
RE_CITE = re.compile(r"\[\s*(?:(?:NCT\d{8}|CHEMBL\d+|ENSG\d+|PMID:?\s*\d+|ORG:[A-Za-z0-9_.\-]+)"
                     r"\s*[,;]?\s*)+\]", re.I)
RE_MDLINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4"}
RE_TOKEN = re.compile(r"\x00(\d+)\x00|\d+[a-z]+\b|\d+(?:,\d{3})*(?:\.\d+)?%?"
                      r"|[a-z]+(?:_[a-z]+)*(?:'[a-z]+)?|n't|[,;:]")


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
def _sentences(body: str) -> list[str]:
    out, depth, start = [], 0, 0
    for i, ch in enumerate(body):
        depth += ch == "("
        depth -= ch == ")"
        end = (ch in ".!?" and (i + 1 == len(body) or body[i + 1] == " ")
               and not re.search(r"\b(?:vs|e\.g|i\.e|approx|no)\.?$", body[start:i], re.I))
        if end or (ch == ";" and depth <= 0):
            out.append(body[start:i + 1].strip())
            start = i + 1
    out.append(body[start:].strip())
    return out


def _strip_citations(text: str, known: set[str]) -> str:
    """Drop "[NCT…, ORG:…]" only when every id in it is a record in the evidence;
    anything else in brackets is read as text."""
    def drop(m):
        ids = [x.strip().lower() for x in re.split(r"[,;\s]+", m.group(0).strip("[] "))
               if x.strip()]
        return " " if ids and all(i in known for i in ids) else m.group(0)
    return RE_CITE.sub(drop, text)


def _units(text: str) -> list[dict]:
    """Sentences. A list item under a heading carries the heading with it."""
    text = RE_MDLINK.sub(r"\1", text)
    out: list[dict] = []
    heading, used = None, False

    def close_heading():
        if heading is not None and not used:      # a heading with no items is prose
            out.extend({"text": s} for s in _sentences(heading))

    for raw in text.splitlines() + [""]:
        line = raw.strip()
        bullet = re.match(r"^(?:[-*•]|\d+[.)])\s+", line)
        body = line[bullet.end():] if bullet else line
        if bullet and heading is not None:
            out.append({"text": body, "heading": heading})
            used = True
            continue
        close_heading()
        heading, used = None, False
        if not line:
            continue
        if body.endswith(":") and not bullet:
            heading = body[:-1]
            continue
        out.extend({"text": s} for s in _sentences(body))
    return [u for u in out if re.search(r"[^\W\d_]", u["text"] + u.get("heading", ""))]


def _join(item: str, heading: str) -> str:
    if not item:
        return heading
    # the slot is a determiner and its plain noun ("these NSCLC drugs"); an adjective
    # ("the following safe drugs") is a claim and stays in the sentence
    slot = re.search(r"\b(?:these|the following|following)(?:\s+(?:NSCLC\s+)?(?:drugs|agents|trials|"
                     r"companies|sponsors|targets|molecules|compounds|organisations|"
                     r"organizations|items|ones|records|entries)\b)?", heading, re.I)
    if slot:
        return heading[:slot.start()] + item + heading[slot.end():]
    return f"{item} — {heading}"


# -- the check ---------------------------------------------------------------- #
class _State:
    def __init__(self, question_entities):
        self.by_type: dict[str, dict] = {}
        self.subject: dict | None = None
        for e in question_entities or []:
            if e.get("type") in ("Drug", "Target", "Company"):
                self.by_type.setdefault(e["type"], e)
                self.subject = self.subject or e

        self.group: list[dict] = [self.subject] if self.subject else []
        self.last: list[dict] = list(self.group)

    def note(self, ents, group=None):
        real = [e for e in ents if e and e.get("type") in ("Drug", "Target", "Company", "Trial")]
        if real:
            self.subject = real[0]
            self.group = [e for e in (group or []) if e in real] or [real[0]]
            self.last = real
            for e in real:
                self.by_type[e["type"]] = e

    def restore(self, members, last):
        """After a clause checked once per member of a group, the group still stands."""
        self.subject, self.group, self.last = members[0], list(members), list(last)


def check_claims(text: str, evidence: list, linker, question_entities=None) -> list[dict]:
    """Return one finding per unsupported claim. `linker(text)` -> entities.

    `question_entities` seed what "this drug" / "this target" refer to."""
    statements = [(e.relation, (e.statement or "").lower()) for e in evidence]
    flat_statements = {_flat(s) for _, s in statements}
    findings: list[dict] = []
    st = _State(question_entities)

    known = set()
    for e in evidence:
        for part in [e.source_record or "", e.edge_id or "", e.statement or ""]:
            known |= {x.strip().lower() for x in re.split(r"[,;\s|]+", part) if x.strip()}
    text = _strip_citations(text, known)
    for u in _units(text):
        item, heading = u["text"], u.get("heading")
        unit = _join(item.rstrip("."), heading) if heading else item

        def flag(kind, value, why, unit=unit):
            findings.append({"kind": kind, "value": value, "sentence": unit, "why": why})

        if _non_english(unit):
            flag("unreadable", unit[:40], "text in a language the check cannot read is "
                                          "not verified")
            continue
        if _flat(item.rstrip(".")) in flat_statements:
            # a verbatim evidence line says exactly what the evidence says; it still
            # sets the subject for what follows, and its heading is still read
            item_ents = ([{"type": "Trial", "label": m.upper()} for m in RE_NCT.findall(item)]
                         + [e for e in linker(item)
                            if e.get("type") in ("Drug", "Target", "Company")])
            if heading:
                # the item's own subject: its words up to the first verb
                lead = re.split(r"\b(?:is|are|was|were|has|have|acts?|evaluates?|sponsors?)\b",
                                re.sub(r"\([^)]*\)", " ", item), maxsplit=1)[0].strip()
                # an unlinkable name ("Tianjin Medical University ...") fills nothing;
                # the item itself is already verified
                linked = RE_NCT.search(lead) or any(
                    e.get("type") in ("Drug", "Target", "Company") for e in linker(lead))
                fill = lead if linked else ""
                _check_unit(_join(fill, heading), statements, linker, st, flag,
                            joined=bool(fill))
            st.note(item_ents)
            continue
        _check_unit(unit, statements, linker, st, flag)
    return findings


def _check_unit(unit, statements, linker, st, flag, lenient=False, joined=False):
    toks, ents = _tokenise(unit, linker)
    for clause in _clauses(toks):
        # pronouns take the subject as it stands at this clause, not at the unit start;
        # one after a relation verb is that relation's object ("targets EGFR and
        # inhibits it"); a plural one stands for every member of the subject group
        plural = None
        for k, t in enumerate(clause):
            if t[0] != "ENT" or ents[t[1]]["type"] != "Pronoun":
                continue
            p = ents[t[1]]
            want = p["want"]
            back = [x for x in clause[max(0, k - 2):k] if x[0] == "W"]
            if want is None and back and back[-1][1] in set(RELATION) | {"on", "of"}:
                verb = next((x[1] for x in reversed(back) if x[1] in RELATION), None)
                if verb:
                    want = ROLES[RELATION[verb][0]][1]
            if want is None:
                # "they" (or an "it" that could be either) after a clause naming several
                # entities of one kind stands for all of them: the subject group, or
                # else the largest set of one kind ("ALK is targeted by A and B")
                kinds_last: dict[str, list] = {}
                for e in st.last:
                    kinds_last.setdefault(e.get("type"), []).append(e)
                biggest = max(kinds_last.values(), key=len, default=[])
                members = (list(st.group) if len(st.group) > 1 else
                           biggest if p["label"] in PLURAL and len(biggest) > 1 else [])
            else:
                members = ([e for e in st.last if e.get("type") == want]
                           if p["label"] in PLURAL else [])
            if len(members) > 1:
                plural = (t[1], members)
                ents[t[1]] = dict(members[0])
                continue
            ante = st.by_type.get(want) if want else st.subject
            ents[t[1]] = (dict(ante, _pron=True) if ante
                          else {"type": "Missing", "label": p["label"]})
        pred = next((i for i, t in enumerate(clause)
                     if t[0] == "W" and t[1] in PREDICATE), len(clause))
        elided = pred < len(clause) and not any(t[0] == "ENT" for t in clause[:pred])
        if plural:
            idx, members = plural
            for m in members:                 # "they are approved": each of them
                ents[idx] = dict(m)
                _check_clause(clause, ents, statements, st, flag, lenient, joined)
            if idx in [t[1] for t in clause[:pred] if t[0] == "ENT"]:
                st.restore(members, members)  # "they" stays the group for what follows
            else:
                names = {m["label"] for m in members}
                st.last = [e for e in st.last if e.get("label") not in names] + members
        elif elided and len(st.group) > 1 and not lenient:
            members, last = list(st.group), list(st.last)
            for m in members:                 # "LORLATINIB and PLB1003 ... and are approved"
                st.subject = m
                _check_clause(clause, ents, statements, st, flag, lenient, joined)
            st.restore(members, last)
        else:
            _check_clause(clause, ents, statements, st, flag, lenient, joined)


def _check_clause(clause, ents, statements, st, flag, lenient=False, joined=False):
    if True:
        c_ents = [ents[t[1]] for t in clause if t[0] == "ENT"]
        words = [t[1] for t in clause if t[0] == "W"]
        has_num = any(t[0] == "N" for t in clause)

        refused = [e for e in c_ents if e["type"] == "Refused"]
        for e in refused:
            flag("distinct_product", e["label"], "names a distinct product (biosimilar, "
                 "other formulation, tracer) the graph does not hold")
        c_ents = [e for e in c_ents if e["type"] != "Refused"]

        gone = [e for e in c_ents if e["type"] == "Missing"]
        if len(gone) == len(c_ents) and not has_num and all(
                w in META_OK or w.endswith("n't") or w in FUNCTION
                or (w in KIND_WORDS and META_ANCHOR & set(words)) for w in words) and (
                not any(w in KIND_WORDS or w in FUNCTION for w in words if w not in META_OK)
                or META_ANCHOR & set(words)):
            return                            # "this graph cannot answer that"
        if gone:
            flag("no_antecedent", gone[0]["label"],
                 "a pronoun with nothing before it to refer to")
            return

        pred = next((i for i, t in enumerate(clause)
                     if t[0] == "W" and t[1] in PREDICATE), len(clause))
        implicit = None
        if pred < len(clause) and not lenient and not any(
                t[0] == "ENT" and ents[t[1]]["type"] != "Refused" for t in clause[:pred]):
            implicit = st.subject             # "... and is phase 3"
        subjects = c_ents + ([implicit] if implicit and implicit not in c_ents else [])
        if not subjects:
            content = [w for w in words if w not in FUNCTION and w not in BE]
            if content or has_num:
                flag("no_subject", " ".join(content[:6]) or "figure",
                     "this clause names no entity the evidence can be checked against")
            return
        labels = [e["label"].lower() for e in subjects]
        support = [(r, s) for r, s in statements if all(_has(l, s) for l in labels)]
        covered = _check_relations(clause, ents, implicit, statements, flag, lenient)
        left_e = {ents[t[1]]["label"].lower() for t in clause[:pred] if t[0] == "ENT"} or (
            {implicit["label"].lower()} if implicit else set())
        right_e = {ents[t[1]]["label"].lower() for t in clause[pred:] if t[0] == "ENT"}
        if covered is None and pred < len(clause) and left_e and right_e and (
                left_e != right_e or len(left_e) > 1):
            # "PLB1003 is LORLATINIB": two entities joined by a verb that is no relation
            flag("identity", " = ".join(e["label"] for e in c_ents),
                 "two different entities joined by a verb the graph has no edge for")
        # under a joined heading the first entity is the copied line's subject and the
        # dash is ours; the heading's own named entities still may not pair silently
        own = ([ents[t[1]] for t in clause if t[0] == "ENT"][1:] if joined else c_ents)
        own = [e for e in own if not e.get("_pron")]
        if covered is None and pred == len(clause) and not lenient and (
                not joined or own):
            kinds = {e["type"] for e in c_ents}
            first = next((t for t in clause if t[0] != "P"), None)
            if len(kinds) > 1 or (first and first[0] == "W" and first[1] in
                                  ("on", "of", "to", "in", "with", "for", "against", "by")):
                flag("fragment", " ".join(e["label"] for e in c_ents) or first[1],
                     "a clause with no verb: the relation it implies cannot be read")
        if covered is not None and not lenient:
            for t in clause:
                if t[0] == "ENT" and t[1] not in covered and ents[t[1]]["type"] != "Refused":
                    flag("unrelated_entity", ents[t[1]]["label"],
                         "named in a clause that states a relation, but not part of any "
                         "relation that was checked")
        _check_attributes(clause, ents, subjects, support, statements, flag)
        group = [ents[t[1]] for t in clause[:pred] if t[0] == "ENT"]
        st.note(c_ents, group)


def _tokenise(unit, linker):
    """Entities and pronouns become placeholders."""
    s = unit
    for pat in SCOPE_PHRASES:
        s = re.sub(pat, " nsclc ", s, flags=re.I)
    s = s.replace("(s)", "s").replace("’", "'")
    s = re.sub(r"[()\[\]{}\"*—–]", " ", s)
    ents: list[dict] = []
    spans = []
    for m in RE_NCT.finditer(s):
        spans.append((m.start(), m.end(), {"type": "Trial", "label": m.group(0).upper()}))

    def blanked():
        b = list(s)
        for a, z, _ in spans:
            b[a:z] = " " * (z - a)
        # the linker strips only " ?.," from tokens, so "EGFR;" or "ALK:" would not link
        return re.sub(r"[;:!]", " ", "".join(b))

    # the linker reports each entity once, so "Osimertinib (Tagrisso)" needs a second look
    for _ in range(8):
        new = 0
        for e in linker(blanked()):
            if e.get("type") == "Disease":
                continue
            words = [re.escape(w) for w in (e.get("matched_text") or "").split()]
            if not words:
                continue
            pat = r"(?<![A-Za-z0-9])" + r"[\W_]+".join(words) + r"(?![A-Za-z0-9])"
            for m in re.finditer(pat, s, re.I):
                if not any(a < m.end() and m.start() < b for a, b, _ in spans):
                    spans.append((m.start(), m.end(), e))
                    new += 1
        if not new:
            break
    low = s.lower()
    for phrase, typ in sorted(PRONOUN.items(), key=lambda x: -len(x[0])):
        for m in re.finditer(rf"\b{re.escape(phrase)}\b", low):
            if any(a < m.end() and m.start() < b for a, b, _ in spans):
                continue
            after = low[m.end():]
            if re.match(r"\s+of\b", after) or any(
                    a >= m.end() and not s[m.end():a].strip(" ,") for a, _, _ in spans):
                continue                 # "the target of X", "the drug osimertinib"
            spans.append((m.start(), m.end(), {"type": "Pronoun", "label": phrase,
                                               "want": typ}))
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
        elif m.group(0)[0].isdigit() and not re.fullmatch(r"\d+[a-z]+", m.group(0)):
            toks.append(("N", m.group(0).replace(",", "")))
        else:
            toks.append(("W", m.group(0)))
    return toks, ents


def _clauses(toks):
    """Split at ; and at and/but/while/whereas when both sides have a predicate."""
    joins = ("and", "but", "while", "whereas")
    cuts = [-1]
    for i, t in enumerate(toks):
        if t == ("P", ";"):
            cuts.append(i)
        elif t[0] == "W" and t[1] in joins:
            left = toks[cuts[-1] + 1:i]
            nxt = next((j for j in range(i + 1, len(toks))
                        if (toks[j][0] == "W" and toks[j][1] in joins)
                        or toks[j] == ("P", ";")), len(toks))
            right = toks[i + 1:nxt]
            if any(x[0] == "W" and x[1] in PREDICATE for x in left) and \
                    any(x[0] == "W" and x[1] in PREDICATE for x in right):
                cuts.append(i)
    cuts.append(len(toks))
    return [toks[a + 1:b] for a, b in zip(cuts, cuts[1:]) if toks[a + 1:b]]


def _group(clause, k, step, skip=()):
    """Positions of the entity run nearest to k in direction `step`."""
    i = k + step
    while 0 <= i < len(clause) and (clause[i][0] != "ENT" or i in skip):
        i += step
    grp = []
    while 0 <= i < len(clause):
        if clause[i][0] == "ENT" and i not in skip:
            grp.append(i)
            i += step
        elif clause[i] in GROUP_GLUE:
            i += step
        elif step > 0 and grp and clause[i - 1] == ("W", "and"):
            # an elided repeat: "... of 14 trials of A and 10 trials of B" -> A, B
            j = i
            while j < len(clause) and clause[j][0] in ("N", "W") and not (
                    clause[j][0] == "W" and clause[j][1] in PREDICATE):
                j += 1
            if j < len(clause) and clause[j][0] == "ENT" and j not in skip:
                i = j
                continue
            break
        else:
            break
    return grp


def _is_passive(clause, k):
    """A participle right after a form of "be" (adverbs allowed), or before "by"."""
    if k + 1 < len(clause) and clause[k + 1] == ("W", "by"):
        return True
    i = k - 1
    while i >= 0 and clause[i][0] == "W" and clause[i][1] in PASSIVE_GAP:
        i -= 1
    return i >= 0 and clause[i][0] == "W" and clause[i][1] in BE


def _check_relations(clause, ents, implicit, statements, flag, lenient):
    """Check every relation in the clause; return the clause positions it covered,
    or None when the clause states no relation."""
    covered: set[int] = set()
    any_rel = False
    for k, t in enumerate(clause):
        if t[0] == "W" and t[1] in TRIAL_NOUNS and k + 1 < len(clause) and \
                clause[k + 1] == ("W", "of"):
            # "<trial> is a phase 1 trial of <drug>": the trial evaluates the drug;
            # "<company> sponsors 14 trials of <drug>": the sponsorship carries it
            drugs = _group(clause, k, +1)
            trials = [i for i in _group(clause, k, -1)
                      if ents[clause[i][1]]["type"] == "Trial"]
            if drugs and not trials:
                j = max(drugs) + 1
                if j < len(clause) and clause[j][0] == "W" and clause[j][1] in (
                        "include", "includes", "including", "are", "were"):
                    trials = _group(clause, j, +1)
                    bad = [i for i in trials if ents[clause[i][1]]["type"] != "Trial"]
                    if bad:
                        trials = [i for i in trials if i not in bad]
            if drugs and trials:
                any_rel = True
                covered |= {clause[i][1] for i in drugs + trials}
                for x in trials:
                    for y in drugs:
                        X, Y = ents[clause[x][1]], ents[clause[y][1]]
                        if not any(r == "EVALUATES" and _has(X["label"], s)
                                   and _has(Y["label"], s) for r, s in statements):
                            flag("relation", f"{X['label']} — trial of — {Y['label']}",
                                 "no retrieved edge links these two entities this way")
            continue
        if t[0] != "W" or t[1] not in RELATION:
            continue
        if t[1] == "sponsor" and k and clause[k - 1] == ("W", "lead"):
            continue                       # "lead sponsor": one noun, read at "lead"
        any_rel = True
        rel, action, voice = RELATION[t[1]]
        subj_t, obj_t = ROLES[rel]
        prev = clause[k - 1] if k else None
        nxt = clause[k + 1] if k + 1 < len(clause) else None

        if t[1] in AGENT_NOUNS:
            # "X is an inhibitor of Y", "X is a Y inhibitor": X acts, Y is acted on
            before = clause[k - 2] if k >= 2 else None
            if prev and prev[0] == "ENT" and (
                    (before and before[0] == "W" and before[1] in ARTICLES)
                    or ents[prev[1]]["type"] == obj_t):
                obj, subj = [k - 1], _group(clause, k - 1, -1)
            else:
                obj = _group(clause, k, +1) if nxt == ("W", "of") else []
                subj = _group(clause, k, -1)
            noun = True
        elif t[1] in ("target", "targets") and nxt == ("W", "of"):
            # "EGFR is the target of osimertinib" / "the target of osimertinib is EGFR"
            subj = _group(clause, k, +1)
            obj = _group(clause, k, -1)
            if not obj and subj:
                j = max(subj) + 1
                while j < len(clause) and clause[j] in GROUP_GLUE:
                    j += 1
                if j < len(clause) and clause[j][0] == "W" and clause[j][1] in BE:
                    obj = _group(clause, j, +1)
            noun = True
        else:
            subj, obj = _group(clause, k, -1), _group(clause, k, +1)
            if voice == "passive" and _is_passive(clause, k):
                if obj:
                    between = {x[1] for x in clause[k + 1:min(obj)] if x[0] == "W"}
                    allowed = {"by"} | ({"in", "at"} if rel == "EVALUATES" else set())
                    if not between & allowed:
                        flag("relation_direction", f"{t[1]} without 'by'",
                             "a passive verb whose agent is not introduced by 'by'; the "
                             "sentence cannot be read in one direction")
                        any_rel = True
                        covered |= {clause[i][1] for i in subj + obj}
                        continue
                subj, obj = obj, subj
            noun = t[1] in ("sponsor", "sponsors") and (
                (prev and prev[0] == "W" and (prev[1] in ARTICLES or prev[1] in TRIAL_NOUNS))
                or nxt == ("W", "of") or nxt is None)
        left = [ents[clause[i][1]] for i in subj]
        right = [ents[clause[i][1]] for i in obj]
        if not left and implicit:
            left = [implicit]
        if noun and left and not right:
            # "AstraZeneca is a trial sponsor" (of the drug named in the clause)
            pool = [i for i, x in enumerate(clause) if x[0] == "ENT" and i not in subj
                    and ents[x[1]]["type"] == obj_t]
            obj, right = pool, [ents[clause[i][1]] for i in pool]
        here = {clause[i][1] for i in subj + obj}

        if rel == "EVALUATES" and not any(e["type"] == "Trial" for e in left + right):
            # no named trial: the subject must be the word "trials" ("trials
            # evaluating X") or the drug the grammatical object ("X is tested in")
            passive = voice == "passive" and _is_passive(clause, k)
            trial_subject = any(x[0] == "W" and x[1] in TRIAL_NOUNS
                                for x in clause[max(0, k - 3):k])
            if not (passive or trial_subject):
                flag("relation_direction", f"{'/'.join(e['label'] for e in left)} {t[1]}",
                     "trials evaluate drugs; this sentence has something else evaluating")
                continue
            drugs = right
            # with "trials" as the subject, the entity before it belongs to another relation
            covered |= ({clause[i][1] for i in obj} if trial_subject and not passive
                        else here)
            # "trials evaluating X include NCT1 and NCT2": the listed trials evaluate X
            if trial_subject and obj:
                j = max(obj) + 1
                if j < len(clause) and clause[j][0] == "W" and clause[j][1] in (
                        "include", "includes", "including", "are", "were"):
                    listed = _group(clause, j, +1)
                    for x in listed:
                        X = ents[clause[x][1]]
                        covered.add(clause[x][1])
                        for d in drugs:
                            if X["type"] != "Trial" or not any(
                                    r == "EVALUATES" and _has(X["label"], s)
                                    and _has(d["label"], s) for r, s in statements):
                                flag("relation", f"{X['label']} — evaluates — {d['label']}",
                                     "no retrieved edge links these two entities this way")
            if not drugs or any(e["type"] != "Drug" for e in drugs):
                if not lenient:
                    flag("relation_incomplete", t[1], "an evaluation relation whose "
                                                      "object is not a drug")
                continue
            for d in drugs:
                if not any(r in ("EVALUATES", "SPONSORS_TRIAL_OF") and _has(d["label"], s)
                           for r, s in statements):
                    flag("relation", f"{d['label']} evaluated in trials",
                         "no retrieved trial evaluates this drug")
            continue
        covered |= here
        if not left or not right:
            if not lenient:
                flag("relation_incomplete", t[1], "a relation whose two sides could not "
                                                  "both be identified in the sentence")
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
                elif action and not any(re.search(rf"\b{a}\b", s)
                                        for s in hits for a in ACTION_WORDS[action]):
                    flag("action", f"{x['label']} {t[1]} {y['label']}",
                         "the evidence gives a different or no action type")
    return covered if any_rel else None


def _owner(clause, ents, i, prefer, kinds=("Drug", "Target", "Company", "Trial")):
    """The entity a value at position i belongs to: nearest in `prefer` direction first,
    among the kinds of entity that can carry that value."""
    order = [range(i + 1, len(clause)), range(i - 1, -1, -1)]
    if prefer == "before":
        order.reverse()
    for rng in order:
        for j in rng:
            if clause[j][0] == "ENT" and ents[clause[j][1]]["type"] in kinds:
                return ents[clause[j][1]]
    return None


def _check_attributes(clause, ents, subjects, support, statements, flag):
    subject = subjects[0]
    present = {e["type"] for e in subjects} | {
        ents[t[1]]["type"] for t in clause if t[0] == "ENT"}
    has_company = "Company" in present
    companies = [e for e in subjects if e["type"] == "Company"]

    def scoped(i, prefer, count=False, kinds=("Drug", "Target", "Company", "Trial")):
        """Evidence naming the clause subject, any company the clause is about (said or
        carried over) and the value's own entity. A count of trials in a sponsorship
        statement belongs to the sponsor-drug pair, so it does not count for a clause
        that names no company."""
        own = _owner(clause, ents, i, prefer, kinds) or subject
        # a trial's phase is its own; any other value is about the clause's subject too
        names = ({own["label"].lower()} if own["type"] == "Trial" else
                 {own["label"].lower(), subject["label"].lower()} | {
                     c["label"].lower() for c in companies})
        rows = [s for r, s in statements if all(_has(n, s) for n in names)
                and not (count and r == "SPONSORS_TRIAL_OF" and not has_company)]
        return own, rows

    consumed: set[int] = set()
    sup_tokens: set[str] = set()
    for _, s in support:
        sup_tokens |= set(re.findall(r"[a-z]+(?:_[a-z]+)*", s))
    sup_flat = " " + " ".join(_flat(s) for _, s in support) + " "
    # whether the clause is about trials (and NSCLC trials) is read from the statements
    # pairing its subject with any of its entities, so a list of drugs can share it
    others = {e["label"].lower() for e in subjects[1:]} | {
        ents[t[1]]["label"].lower() for t in clause if t[0] == "ENT"}
    others.discard(subject["label"].lower())
    # trials and NSCLC are about the clause's subject, not any entity it mentions
    wide = [(r, s) for r, s in statements if _has(subject["label"], s)]
    counted = any(t[0] == "N" and any(x[0] == "W" and x[1] in TRIAL_NOUNS
                                      for x in clause[k + 1:k + 4])
                  for k, t in enumerate(clause))
    # a stated count of trials is itself checked as a number; otherwise the evidence
    # must show trials for these entities (a count of zero shows none)
    about_trials = any(r in ("EVALUATES", "SPONSORS_TRIAL_OF")
                       or re.search(r"(?<![\d.])[1-9]\d*\s+(?:\S+\s+)?trial", s)
                       or (counted and "trial" in s)
                       for r, s in wide)
    wide_tokens = {w for _, s in wide for w in re.findall(r"[a-z]+", s)}

    def trial_run(at):
        """The trials a value at `at` is about: the run of trials (joined by and/or/
        commas) just before it, or else the first run after it."""
        before = [k for k, t in enumerate(clause[:at]) if t[0] == "ENT"
                  and ents[t[1]]["type"] == "Trial"]
        if before:
            run = _group(clause, before[-1] + 1, -1)
        else:
            after = next((k for k in range(at + 1, len(clause)) if clause[k][0] == "ENT"
                          and ents[clause[k][1]]["type"] == "Trial"), None)
            run = _group(clause, after - 1, +1) if after is not None else []
        return [ents[clause[k][1]]["label"] for k in run
                if ents[clause[k][1]]["type"] == "Trial"]

    i = 0
    while i < len(clause):
        t = clause[i]
        if t == ("W", "phase"):
            j = i + 1
            nums = []
            while j < len(clause) and clause[j][0] in ("N", "W") and len(nums) < 2:
                v = clause[j][1]
                if clause[j][0] == "N" or v in ROMAN or re.fullmatch(r"\d+[a-z]+", v):
                    nums.append(ROMAN.get(v, v))
                    j += 1
                elif v in ("or", "to"):
                    j += 1
                else:
                    break
            if nums:
                consumed |= set(range(i, j))
                key = "phase" + "".join(nums)
                # only a trial or a drug has a phase; with a trial named, it is the trial's
                owner, rows = scoped(i, "before", kinds=(("Trial",) if "Trial" in present
                                                         else ("Trial", "Drug")))
                run = trial_run(i) if "Trial" in present else []
                if len(run) > 1:
                    # "NCT1 and NCT2 are phase 3": each of them
                    def has(lab):
                        own1 = " ".join(_squash(x) for _, x in statements if _has(lab, x))
                        return re.search(rf"{key}(?![0-9a-z])", own1) or all(
                            re.search(rf"phase{n}(?![0-9a-z])", own1) for n in nums)
                    ok = all(has(lab) for lab in run)
                    if not ok:
                        flag("phase", "phase " + "/".join(nums), "not every trial named "
                             "here has that phase in the evidence")
                    i = j
                    continue
                own = " ".join(_squash(s) for s in rows)
                if owner["type"] == "Trial":
                    ok = re.search(rf"{key}(?![0-9a-z])", own) or all(
                        re.search(rf"phase{n}(?![0-9a-z])", own) for n in nums)
                elif owner["type"] == "Drug":
                    # a drug's phase is its maximum stage, not the phase of a trial of it
                    ok = re.search(rf"stage{key}(?![0-9a-z])", own)
                else:
                    ok = False
                if not ok:
                    flag("phase", "phase " + "/".join(nums), "no evidence statement about "
                         "these entities gives that phase")
                i = j
                continue
        if t[0] == "N":
            n = t[1]
            ahead = [x[1] for x in clause[i + 1:i + 4] if x[0] == "W"]
            behind = [x[1] for x in clause[max(0, i - 3):i] if x[0] == "W"]
            counting = any(w in TRIAL_NOUNS for w in ahead) or (
                bool(behind) and behind[-1] in TRIAL_NOUNS)        # "trials: 13"
            own = " ".join(_flat(s) for s in scoped(i, "after", counting)[1]).replace(",", "")
            if counting:
                # a count of trials must be stated as a count of trials, not a phase
                ok = re.search(rf"(?<!phase )(?<![\d.]){re.escape(n)}\s+(?:[a-z]+\s+){{0,2}}"
                               r"trial", own)
            else:
                # a bare figure, not the digit of a phase ("PHASE_1" is no count of 1)
                ok = re.search(rf"(?<!phase )(?<![\d.]){re.escape(n)}(?![\d.])", own)
            if not ok:
                flag("number", n, "no evidence statement about these entities gives "
                                  "that figure")
        if t[0] == "W" and re.fullmatch(r"\d+[a-z]+", t[1]):
            flag("number", t[1], "a figure with a suffix the evidence does not use")
        i += 1

    # a count shared by several drugs in one clause cannot be told apart: each drug
    # needs its own "N trials of/evaluating <drug>"
    drugs, seen_labels = [], set()
    for k, t in enumerate(clause):          # an alias in brackets is the same drug
        if t[0] == "ENT" and ents[t[1]]["type"] == "Drug" and \
                ents[t[1]]["label"] not in seen_labels:
            drugs.append(k)
            seen_labels.add(ents[t[1]]["label"])
    counts = [k for k, t in enumerate(clause) if t[0] == "N" and (
        any(x[0] == "W" and x[1] in TRIAL_NOUNS for x in clause[k + 1:k + 4])
        or any(x[0] == "W" and x[1] in TRIAL_NOUNS for x in clause[max(0, k - 2):k]))]
    if counts and len(drugs) > 1:
        owned = set()
        for k in counts:
            j = k + 1
            while j < len(clause) and j < k + 6 and clause[j][0] != "ENT":
                j += 1
            if j < len(clause) and clause[j][0] == "ENT" and j in drugs:
                owned.add(j)
        if set(drugs) - owned:
            flag("count_ambiguous", " / ".join(ents[clause[k][1]]["label"] for k in drugs),
                 "a trial count in a clause naming several drugs, without a count for "
                 "each drug of its own")

    # status phrases are one claim, in the registry's spelling, and belong to the
    # trial named before them (or, with one subject, to the clause's entities)
    trial_pos = [k for k, t in enumerate(clause) if t[0] == "ENT"
                 and ents[t[1]]["type"] == "Trial"]
    wpos = [k for k, t in enumerate(clause) if t[0] == "W" and k not in consumed]
    wseq = [clause[k][1] for k in wpos]
    taken: set[int] = set()
    for status in STATUS:                    # longest phrases first, as listed
        parts = status.split()
        for j in range(len(wseq) - len(parts) + 1):
            if wseq[j:j + len(parts)] != parts or taken & set(range(j, j + len(parts))):
                continue
            taken |= set(range(j, j + len(parts)))
            at = wpos[j]
            if trial_pos:
                labs = trial_run(at) or [ents[clause[trial_pos[0]][1]]["label"]]
                row_sets = [[x for _, x in statements if _has(lab, x)] for lab in labs]
            else:
                row_sets = [[x for _, x in support]]
            for rows in row_sets:          # with several trials, each of them
                own = " " + " ".join(_flat(x) for x in rows) + " "
                plain = own.replace("active not recruiting", "").replace(
                    "not yet recruiting", "")
                if f" {status} " not in own or (status == "recruiting"
                                                and " recruiting " not in plain):
                    flag("status", status, "no evidence statement about that entity gives "
                                           "that status")
                    break
    words = [w for j, w in enumerate(wseq) if j not in taken]


    toks_w = [t[1] for t in clause if t[0] in ("W", "N")]
    for j, w in enumerate(toks_w):
        if w == "nsclc":
            nxt = toks_w[j + 1] if j + 1 < len(toks_w) else ""
            prv = toks_w[j - 1] if j else ""
            # the disease may only qualify trials the evidence itself calls NSCLC trials:
            # "NSCLC trials", or "in NSCLC" in a clause that is about trials, never a
            # drug's approval or use ("approved in NSCLC")
            trial_clause = any(x in TRIAL_NOUNS or (x in RELATION and RELATION[x][0] in (
                "EVALUATES", "SPONSORS_TRIAL_OF")) for x in toks_w)
            approval = any(x in ("approved", "approval", "approve", "approves",
                                 "indicated", "indication", "licensed") for x in toks_w)
            if approval or not ((nxt in TRIAL_NOUNS or (prv == "in" and trial_clause))
                                and "nsclc" in wide_tokens and about_trials):
                flag("indication", "lung cancer", "a claim about the disease itself (what a "
                     "drug is for or is); the graph holds trials, not indications")
    words = [w for w in words if w != "nsclc"]

    # letters spelled out one by one ("N O T") hide a word from every check
    run = 0
    for t in clause + [("P", "")]:
        if t[0] == "W" and len(t[1]) == 1 and t[1] not in ("a", "i"):
            run += 1
            continue
        if run >= 2:
            flag("unreadable", "spelled-out letters", "letters written one by one cannot "
                                                      "be read as a word and checked")
        run = 0

    # a word naming a kind belongs to the entity just before it ("EGFR is a drug"),
    # or, with none before, to an entity of that kind in the clause
    for k, t in enumerate(clause):
        if t[0] != "W" or t[1] not in KIND_WORDS or KIND_WORDS[t[1]] == "trials":
            continue
        kind = KIND_WORDS[t[1]]
        prev_e = [ents[x[1]] for x in clause[:k] if x[0] == "ENT"]
        ok = prev_e[-1]["type"] == kind if prev_e else kind in present
        if not ok:
            flag("wording", t[1], "calls something a drug or company that the evidence "
                                  "does not")

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
            if w in KIND_WORDS:
                kind = KIND_WORDS[w]
                ok = about_trials if kind == "trials" else True   # checked above by owner
                if not ok:
                    flag("wording", w, "calls something a drug, company or trial that "
                                       "the evidence does not")
                continue
            if w in RELATION or w in FUNCTION or w in BE or len(w) < 2:
                continue
            if w in sup_tokens or STEM_SUPPORT.get(w) in sup_tokens:
                continue
            flag("wording", w, "this word makes a claim no evidence statement about "
                               "these entities supports")
