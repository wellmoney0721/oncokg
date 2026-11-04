# OncoKG — reading messy trial text into a drug knowledge graph

A small, honest pipeline over public non-small cell lung cancer data. It takes the
free text clinical trial registries actually contain, resolves it to reference
identifiers, builds a knowledge graph with provenance, answers questions against
that graph, and reports what it got wrong.

The point of the project is not the graph. It is the gap between a curated
vocabulary and the text real people type, and what it takes to cross that gap
without inventing facts.

**Live dashboard:** *(add the published link here)*

---

## The problem, in one record

```
NCT02303977  "Phase II Study of Abraxane and Gemicitabine in Patients With
              Advanced Adenocarcinoma Non-Small Cell Lung Cancer ..."
```

`Abraxane` is nab-paclitaxel — a different product from the paclitaxel its
synonym list points at. `Gemicitabine` is gemcitabine, misspelled. The stated
condition is `Patients With Stage IV or Recurrent Adenocarcinoma of the Lung`,
which no ontology contains verbatim. Across 3,000 trials there are **2,742
distinct drug strings** for roughly a thousand molecules and **2,175 distinct
condition strings** for one disease.

Those strings fail in recognisable families:

| family | example |
| --- | --- |
| dose and route noise | `Pembrolizumab 100 mg I.V single dose` |
| salt and formulation | `Anlotinib hydrochloride capsule` |
| trade and development names | `Avastin`, `ZD6474 (ZACTIMA)`, `OSI-774` |
| combinations, no separator | `Cisplatin Docetaxel Gefitinib Pemetrexed` |
| placebo arms | `Placebo Erlotinib 150/100mg` vs `placebo plus docetaxel` |
| class terms that are not substances | `Platinum Based Chemotherapy` |
| distinct products sharing a molecule | `Bevacizumab Biosimilar HLX04` |
| radiotracers | `[18F]F-AraG PET imaging` |

---

## Results, with both denominators

Precision was measured on **three disjoint hand-scored samples**, because a
number measured on the data you tuned against is not a measurement.

**The headline is 88.7%** — 102 of 115 accepted matches correct on the held-out
test sample (Wilson 81.6–93.3), scoring the pipeline as it was when that sample
was held out. It started as 91.3%; a second independent audit found two more
leniently-scored held-out labels (89.6%), and a third found one more (88.7%).
Each time the figure went down, and this is the defensible one.

| sample | rows | accepted rows, as labelled | **raw precision, as labelled** |
| --- | --- | --- | --- |
| development | 214 | 137 | 90.5% (84.4–94.4) |
| **held-out test** | **172** | **115** | **88.7% (81.6–93.3)** |
| post-fix | 58 | 38 | 92.1% (79.2–97.3) |

**There is no held-out figure for the repaired pipeline, and none is
published.** Three audit rounds used the test sample to find defects, and the
repairs changed the resolution of 26 of its 172 rows. Those rows are *stale*:
their label scores a resolution the pipeline no longer produces, so
`src/evaluate.py` sets them aside and lists them for re-labelling instead of
inventing a verdict. What remains scores 98 of 98 — but the stale rows held
every one of the errors, so the survivors are exactly the rows the repairs left
alone. The evaluation JSON still carries a stratified estimate and two
intervals for those survivors (`accepted_precision`); they are survivor-selected
and are not reported here as a precision. **Measuring the repaired pipeline
needs a new sample, labelled by someone other than the author.**

**The sample size is not the precision denominator.** Only rows in an accepting
tier can be right or wrong about a match; the rest are refusals, scored
separately. Of the 172 held-out rows, 115 asserted a match when labelled.
Quoting 172 as the denominator overstates the evidence, and an earlier version
of this file did exactly that.

**Why the headline is raw, not stratified.** The sample is drawn by a
disproportionate per-tier quota, so a stratified estimate is the right estimator
in principle — but it needs the tier populations at labelling time, and those
were not saved. Weighting old labels by today's populations mixes two pipelines
into one number, which is what the first version did. An earlier version also
put a normal-approximation interval on the stratified mean and published
`99.1% [98.4, 99.8]`; with 88% of the weight in tiers that scored 100%, the
variance term was zero and the interval collapsed.

Coverage of substance-like strings is **78.0%** (4,936 of 6,329). Precision and
coverage are reported separately on purpose: coverage can always be bought by
lowering a threshold, and one number hides that trade.

Two more figures matter as much as the headline:

* **44.4%** (4 of 9, development sample, rows still current) — how often a
  proposal the pipeline *held back for review* would actually have been right.
  A number below half is the evidence that the automatic threshold is not set
  too low; with nine rows it is weak evidence.
* **100%** (8/8, Wilson 67.6–100) — the placebo guard on the held-out sample,
  after the development sample showed it was over-blocking combination arms.

---

## What an independent review found

The labels in all three samples were assigned by one annotator — the same person
who wrote the matching rules. Saying so in a limitations section is not the same
as testing it, so the project was handed to independent reviewers with
instructions to disagree, three times, and each time they did. The second and third
rounds' reports are `codex_report.txt` and `codex_report_round3.txt`, with
evidence in `audit_evidence_20261103/` and `audit_evidence_round3/`;
`CODEX_R2_VERDICT.md` and `CODEX_R3_VERDICT.md` record which findings were
reproduced, which were partly wrong, and what the reviewers missed. Everything
below is a defect a review found and this repository now carries the fix.

### Round 3

**A defect this file said was fixed was not.** Round 2's write-up removed the
`adenovirus` vaccine item from the known defects because it "no longer
reproduces" — but only the short string had been tried. The sample's actual
string, `autologous dendritic cell-adenovirus CCL21 vaccine`, is 50 characters;
the class pattern capped its qualifier at 40, so it still resolved to
TASADENOTUREV and produced live edges. The cap is 90 now, bare vector words
(`adenovirus`, `vaccinia`, `lentivirus`) are class terms, and both edges are
retired.

**The query layer bypassed the resolver's refusals.** It linked question words
straight against the synonym index, so "What trials evaluate Mvasi?" answered
with twelve bevacizumab trials. Distinct-product names no longer enter the index
from any source, and a question naming one is refused.

**Renames were still recorded as ownership.** `GSK` became a subsidiary of
`GlaxoSmithKline` (the self-parent check compared the parent's display name),
and Schering-Plough sat under Merck & Co although it was the legal survivor of
the 2009 merger and renamed itself Merck & Co., Inc. Both are now one entity.

**Four more labels were lenient**, by the same product criterion: `DN-101`
(high-dose calcitriol), `Genexol-PM`, pegylated liposomal doxorubicin and
`ABI-007` (Abraxane's code) — one held-out, two development, one post-fix. The
held-out figure fell from 89.6% to 88.7%. The label-correction guard also
ignored the component column, and an outdated reason survived in a CSV note;
both are fixed.

**More domain rules were wrong:** `pembrolizumab-free regimen` resolved to
pembrolizumab (`free` read as an FDA suffix); `[89Zr]pembrolizumab` lost its
isotope; growth-factor biosimilars (`filgrastim-sndz`) and `Pazenir` reached
their reference molecules while an uppercase originator suffix
(`Cemiplimab-RWLC`) was blocked; the ester guard ran after the synonym lookup;
`ICE`, a regimen, resolved to ifosfamide because only registry synonyms were
screened; and `cisplatin + placebo to match pembrolizumab` lost the cisplatin
the arm really received. The groundedness check still passed `aspirin`, `1e6`
and `⅔`. Each has a regression test.

### Round 2

### Round 2

**Three more gold labels were wrong, again leniently** — two held-out, one
post-fix. `CC-486` (oral
azacitidine, whose label forbids substituting it for the injectable),
`NanoPac` (nanoparticulate paclitaxel) and a post-fix `Nab-paclitaxel` had been
scored correct as AZACITIDINE and PACLITAXEL. Round 1 had already set the rule
that a separately approved, non-substitutable product is a different product;
these three broke it. One round-1 correction also carried a wrong reason — it
called a trial a comparison of two paclitaxel formulations when the taxane was
only its backbone — and the reason is corrected. The held-out figure fell from
91.3% to 89.6%.

**The relation rename had broken retrieval.** `DEVELOPS` was renamed in the
graph but the query layer and the dashboard still asked for it, so "Which
companies are developing osimertinib?" returned no evidence and the dashboard's
company table was empty. Both read `SPONSORS_TRIAL_OF` now, and each answer line
states the sponsor's class and that a sponsorship is not a development claim.

**The Merck fix had not held.** `Merck & Co., Inc.` reduces to `merck` once its
legal suffixes are stripped, `merckkgaa` starts with `merck`, and a reverse
prefix test made the American company a subsidiary of its German competitor. The
reverse test is gone. The same review found `BeiGene` recorded as a *subsidiary*
of `BeOne Medicines` — a rename stored as ownership. Renames and plain short
forms of one company now merge into one node before any parent lookup; only
genuinely distinct legal entities get `PARENT_OF`. The bare key `schering` also
caught Bayer's Schering AG and is now `scheringplough`.

**A removed trial kept its derived claim for one build.** The derived
sponsorship was computed before unseen base edges were retired, so a trial that
had left the sources still contributed to it. Base edges are retired first now,
and nodes no source mentions are marked retired rather than counted as live.

**The groundedness check let inventions through.** `xyzabumab cures cancer.`
passed, because only capitalised words were checked. Numbers were split on the
decimal point, so against evidence reading `47.5%` an invented `47%` passed and
the exact `47.5%` was rejected; a figure written in words passed untouched. It
now checks drug-shaped lowercase names, matches decimals whole and refuses
figures in words — and its docstring lists what it still cannot catch.

**The label-correction check always passed.** `--check` printed `PENDING` and
then "all corrections are already in the labels", exiting 0. A pending
correction now fails the check, and every correction is pinned to the row's raw
string and resolved identifier, not only to its id.

**The reference vocabulary was dirtier than round 1 measured.** 2,595 of the
9,316 synonyms in the snapshot come from AACT, which links trial intervention
text to molecules, so they carry whatever else the arm contained: `tobramycin`
under DEXAMETHASONE, `carboplatin` under CISPLATIN, `docetaxel` under
PACLITAXEL, `CHOP` under PREDNISONE, the bare word `mab` under PEMBROLIZUMAB.
A curation rule now removes registry synonyms that name another ingredient, a
regimen, an abbreviation that does not single out one molecule, or a distinct
product. It errs toward refusal, and the errors it makes are listed under known
defects. Round 3 measured its cost before its own repairs: with the rule switched off,
accepted occurrences went from 4,942 to 4,950 — ten lost, two gained.

**Several domain rules were wrong in a way a pharmacist would catch.** Biosimilar
brands (`Mvasi`, `Alymsys`, `Zirabev`) resolved to bevacizumab; FDA four-letter
suffixes were all treated as biosimilars, which blocked originators like
`cemiplimab-rwlc`; `liposomal doxorubicin` was blocked alone and accepted once
`and cisplatin` was added, because cleaning removed the word the guard looked
for; `prednisolone phosphate`, an ester, was stripped as if it were a salt;
`No pembrolizumab` was accepted as an exposure; a bracketed code in a
combination attached itself to an unrelated component, so `AZD8205 and AZD5305
(saruparib)` recorded AZD8205 as saruparib; and the class guard's INN exemption
matched only the literal word `mab`, so `pembrolizumab antibody` was blocked and
`mab inhibitor` let through. Each has a regression test in
`tests/test_audit_round2.py`.

### Round 1

**Five gold labels were wrong, all of them leniently.** `Abraxane` and
`Nab-Paclitaxel` scored as correct resolutions to PACLITAXEL; `Bevacizumab
Biosimilar HLX04` and `Bevacizumab-Pfizer` as correct resolutions to
BEVACIZUMAB; `Interferon-a` as a correct match to a ChEMBL class node whose
aliases are `ifn`, `pegasys` and `pegylated interferon` — the same error this
annotator had scored *incorrect* three rows earlier for `Epothilone`. The
corrections and their reasons are in `src/apply_label_corrections.py`, applied
by a script rather than edited into the CSVs, so the published figures trace
back to the labels that produced them.

**A derived relation was unsound and is gone.** The graph used to assert
`DEVELOPS` between a company and a drug whenever that company led a trial
evaluating it. Measured, 58.8% of those edges had a non-industry lead sponsor:
the graph claimed *National Cancer Institute develops paclitaxel*, *Memorial
Sloan Kettering develops cisplatin*, and — because 36 trials are led by named
physicians — that an individual doctor develops nivolumab. Sponsoring a trial is
an observation; developing a drug is a different claim, and nothing in these
sources supports it. The edge is now `SPONSORS_TRIAL_OF`, carries the sponsor's
class, and makes no development claim at all.

**Figures in this file did not match the artifacts.** The node count was stated
as 6,481 where every artifact said 6,475. `class_term_as_synonym` was stated as
56 where the quality report said 134. Coverage was stated as 78.3% where the
evaluator printed 78.2%. The curation claim "2,008 → 66" was reproducible from
nothing at all. That one is now a measurement: `src/curation_effect.py` resolves
the whole corpus twice, with and without curation, and writes the before/after
to `reports/curation_effect.json`.

**The groundedness check could not fail on the default path.** The template
answer is built by concatenating the retrieved evidence, so checking it against
that same evidence is circular — it passes by construction. It now reports
`applicable: false` and asserts nothing when the answer was rendered rather than
generated. The numeric check was also substring-based, so a fabricated "47%
response rate" passed against an NCT id containing `47`; it was tokenised — and
round 2 found the tokenising itself broke decimals.

**A dead `break_outer = False` made company-name cleaning strip sector words
from anywhere in a name**, turning `Alliance For Clinical Trials In Oncology`
into `Alliance For Clinical Trials In` and `Spanish Lung Cancer Group` into
`Spanish Lung Cancer`. Legal forms are now stripped anywhere, sector words only
in trailing position, and never from a name carrying an academic or
cooperative-group marker.

**The corporate map was stale, and in one place wrong in a way a pharma reader
would catch immediately.** Sandoz was mapped to Novartis three years after its
spin-off. BeiGene was not mapped to its 2025 name, BeOne Medicines, so one
company sat under two nodes. Seagen, Mirati, Turning Point, RayzeBio, Acerta and
Alexion were unparented. And **Merck KGaA had no entries at all** while Merck &
Co had five — so EMD Serono, the Darmstadt company's North American arm, floated
free while its competitor was fully mapped. Round 1 added the entries; round 2
found the matching rule still merged the two Mercks, and the BeiGene fix stored a
rename as ownership (see above).

**The dashboard was non-deterministic and stale.** It serialised a Python `set`,
so every rebuild produced a different byte order and dirtied the tree, and the
committed copy came from a different run than `reports/` — a reader opening the
page saw different numbers than the JSON. Sorted now, and rebuilt by the same
command as everything else.

---

## What the pipeline refuses to do

Most of the engineering here is refusal. Each of these was a real error found in
the data, not a hypothetical.

**A placebo arm is not a drug-free arm, and it is not an exposure either.**
`placebo plus docetaxel` really did administer docetaxel; `Placebo to Match
ZD6474` administered nothing. Blocking the whole string is safe for the second
and silently destroys a true exposure in the first, so the two are separated: a
placebo joined by a combination separator means co-administration, a placebo
naming its reference drug does not.

**Development codes are never fuzzy-matched.** `BMS-986504` scored 88.9 against a
neighbouring BMS code. One character apart is a different molecule, so ordinary
string-similarity intuition is wrong here and approximate matching is disabled
for anything shaped like a development code.

**Digits veto a fuzzy match.** `recombinant interleukin-12` matched `aldesleukin`
— interleukin-2 — at 97.9. Any disagreement in the numeric tokens now rejects the
match outright.

**A partial parse is worse than no parse.** `Cisplatin Docetaxel Gefitinib
Pemetrexed Vinorelbine Gemcitabine` names six substances with no separator at
all. Matching the first and discarding the rest produces a record that *looks*
complete, which nothing downstream can detect. Greedy dictionary segmentation
extracts every component it can, and a leftover of five or more letters, or
anything shaped like a development code, is emitted as an explicit unresolved
residue. Shorter leftovers are dropped as parse filler, so a three-letter code
next to a known drug (`pembrolizumab new XYZ`) disappears without a trace.

**A biosimilar is not its originator.** `Bevacizumab Biosimilar HLX04` and
`Bevacizumab-Pfizer` name separate regulatory products. Resolving them to
BEVACIZUMAB puts a competitor's asset on Genentech's molecule and makes the
asset under study vanish. There is no identifier for these in the vocabulary, so
they are refused with a reason code. The same rule covers liposomal,
albumin-bound and nanoparticulate reformulations, biosimilar brands such as
`Mvasi` and `Zirabev`, and FDA suffixes known to belong to biosimilars
(`bevacizumab-awwb`) — while an originator's own suffix (`cemiplimab-rwlc`) is
stripped and resolved. The check runs on the text before cleaning, so a
reformulation named inside a combination or in brackets is still seen.

**A negated substance is an absence.** `No pembrolizumab` records that the arm
did *not* receive it, and gets its own tier, `BLOCKED_NEGATED`, rather than an
`EVALUATES` edge. A prefix is not a negation: `Non-platinum chemotherapy:
paclitaxel` still resolves paclitaxel.

**Class terms, gene symbols and isotopes are not drugs.** `PD-1 inhibitor`,
`EGFR` and `18F` are each refused by their own guard with a reason code — and so
now are `VEGF inhibitor`, `ALK inhibitor`, `CAR-T cells`, `antibody-drug
conjugate` and bare `platinum`, all of which an independent review found falling
through to UNRESOLVED or, in platinum's case, becoming a confidence-1.00 edge to
the chemical element in seven trials. Exact membership in a blocklist can never
be complete, so a pattern rule now catches any gene or pathway qualifier in
front of a head noun like `inhibitor` or `blockade`.

---

## The reference database is wrong too

Treating a curated vocabulary as ground truth is the fastest way to inherit its
errors. The synonym list for **atezolizumab** in this snapshot contains
`avelumab`, `durvalumab`, `adebrelimab` and `medi4736` — three other molecules,
one of them twice, since MEDI4736 is durvalumab's development code. Durvalumab's
contains `atezolizumab`, `toripalimab` and `durvalumab placebo`.

So the dictionary is curated before any record is matched against it, by rules
that each record what they changed. Counts are from `reports/quality_report.json`;
the registry rule runs first, so the later rows count what it left:

| defect | found | what the rule does |
| --- | --- | --- |
| `registry_alias_removed` | 248 | an AACT-sourced synonym naming another ingredient (`tobramycin` under dexamethasone), a regimen (`CHOP`, `AC`), an abbreviation shared by several molecules (`lv`, `ici`) or a distinct product — removed |
| `distinct_product_alias` | 204 | biosimilar and reformulation names (`abraxane`, `doxil`, `mvasi`, `bevacizumab-awwb`) dropped before indexing, from any source |
| `class_term_as_synonym` | 118 | `anti-PD-L1`, `pd-l1 blockade` removed from the lookup index |
| `genuinely_ambiguous_alias` | 99 | kept ambiguous; records matching it go to review |
| `parent_child_collapse` | 60 | salt and child forms folded into the parent |
| `cross_drug_synonym` | 57 | an alias that is another molecule's **preferred name** is bound to that molecule; the records listing it carry a suspected upstream error |
| `suspected_duplicate_entity` | 46 | two identifiers that look like one substance — reported, never auto-merged |
| `placebo_string_in_synonym_list` | 6 | `durvalumab placebo` dropped before indexing |

Measured by resolving the corpus twice, curation cuts ambiguous resolutions from
**2,187 to 65** and raises exact matches from **1,997 to 4,053**
(`reports/curation_effect.json`).

---

## The graph

6,469 live nodes and 17,564 live edges over `Company`, `Investigator`, `Drug`,
`Target`, `Disease` and `Trial`.

| relation | edges |
| --- | --- |
| `SPONSORS` | 4,652 |
| `EVALUATES` | 4,437 |
| `SPONSORS_TRIAL_OF` *(derived)* | 3,176 |
| `STUDIES` | 2,774 |
| `ACTS_ON` | 2,186 |
| `ASSOCIATED_WITH` | 300 |
| `PARENT_OF` | 39 |

Every edge carries its **source**, its **fetch timestamp** and a **confidence**.
Edges read from a single record carry that **source record**; the derived
`SPONSORS_TRIAL_OF` edges have no single record and carry the full list of
trials they rest on in their properties instead, so all 3,176 of them have an
empty `source_record` by design. Only edges produced by resolving a free-text
string carry a **resolution tier** — `EVALUATES` and `STUDIES` — so the other
10,353 have none. Only accepted resolutions become edges; ambiguous, blocked and
unresolved components stay in the quality report, because the graph is the part
that claims to be true.

The one derived relation says only what the evidence shows. Of its 3,176 edges,
41.2% have an industry lead sponsor and 58.8% do not; the class rides on the
edge so a consumer can filter. Its confidence is a flat 1.0 meaning "the
sponsorship is recorded", not a score derived from the trial count.

Re-running against a newer snapshot **retires** edges and nodes instead of
deleting them and writes every edge change to a change log, so "when did this
relationship appear, and on what evidence?" stays answerable. Two consecutive
rebuilds from the same snapshot record zero added, changed or retired edges; a
rebuild after a source changes records exactly what changed, including derived
edges, which are recomputed only after the base edges are settled.

A corporate parent is modelled as a `PARENT_OF` **relationship**, not as a
rename. An earlier version renamed MedImmune to "AstraZeneca" and produced two
nodes with one label, after which a lookup by name silently picked whichever one
it found first.

---

## Asking it things

Questions are linked against the same dictionary the pipeline uses, so a question
naming a trade name finds a graph that stores a ChEMBL id. A question naming a
distinct product (`Mvasi`, `liposomal doxorubicin`) is refused rather than
answered as the originator.

```
$ python src/query.py "What trials evaluate Tagrisso?"

Trials evaluating this drug:
  - NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB [NCT03909334]
  ...
Scope: 12 edge(s) from this graph; non-small cell lung cancer only.
```

Out of scope, it says so rather than guessing — though only when nothing links;
a question naming a drug it knows will be answered as a drug question, which is
listed below as a defect rather than described as a feature.

With `ANTHROPIC_API_KEY` set, the language model does **not** write the answer.
It returns claims as JSON, and the program writes the answer from the claims that
check out (`src/structured.py`):

```json
{"claims": [
  {"kind": "relation", "relation": "ACTS_ON", "subject": "osimertinib", "object": "EGFR",
   "evidence": "CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410", "action": "INHIBITOR"},
  {"kind": "trial", "trial": "NCT03909334", "evidence": "NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334",
   "phase": ["PHASE2"], "status": "ACTIVE_NOT_RECRUITING"}
]}
```

Each claim is accepted only if its keys are exactly those of its kind (no free-text
field exists, and an unknown key rejects the claim), the cited edge is one of those
retrieved for the question and is live (a drug claim may also cite the drug's
profile record retrieved for the question), the edge's relation and both ends are the
ones the claim names (a name is an id, a label that belongs to exactly one node, or an
alias that resolves, whole, to that one node; a name that could mean several nodes
is refused), and every value
equals what the graph stores: action type, sponsor's trial count, a trial's phase
set and status, a drug's maximum stage and its number of trials. The answer is then
written from accepted claims in the graph's own labels and values, with the edge id
after each line, so nothing the model typed reaches the answer. Rejected claims are
left out of the answer and listed separately, with the reason, as diagnostics.

This replaced checking the model's prose. Six adversarial rounds against a prose
checker (`src/claims.py`, kept as an auxiliary screen) each found new sentence
shapes that slipped through, because a reader of word order cannot keep up with
English. A closed claim format can be checked exactly. What it cannot judge is
whether the claims chosen answer the question well or leave something important
out: it guarantees what is said is in the graph, not that everything that matters
was said.

With no key, the evidence is rendered directly by a template, and the prose check
reports `applicable: false`, because a template built from the evidence cannot
fail a test against it. The pipeline has no required dependency on a model.

---

## Known defects

Left listed rather than quietly assumed away. Round 2 removed an item here
(`adenovirus` in a vaccine name resolving to an oncolytic product) as no longer
reproducing; round 3 showed it still did, on the sample's longer string. It is
fixed now, and its number has been reused.

1. **The placebo rule needs a separator.** `Placebo Drug: Docetaxel Drug:
   Carboplatin` has no `+` or `and`, so it reads as a reference arm and two
   administered drugs are dropped. Fix: treat a repeated `Drug:` label as a
   separator.
2. **Regimen acronyms are not expanded.** Round 2 stopped them resolving to a
   single member (`CHOP` no longer becomes prednisone), but `HS-20117+FOLFIRI`
   and `+mFOLFOX6` still drop 5-FU, leucovorin, irinotecan, oxaliplatin and
   capecitabine on the floor. They need a regimen expansion table.
3. **The repaired pipeline has no held-out measurement.** The test sample was
   used by three audit rounds; 26 of its 172 rows are stale and they held every
   error, so the 98/98 survivors are not an estimate. The development and
   post-fix samples are in the same position (33 and 5 stale). A new sample, ideally labelled by a
   second annotator, is the only way to put a number on the current pipeline.
4. **Coverage is capped by scope.** The vocabulary holds only drugs Open Targets
   links to NSCLC, so `propranolol` is correctly refused and still counts against
   coverage. Widening to the full ChEMBL drug set would need its own precision
   measurement.
5. **Still one annotator, now with three independent re-scores.** Round 1
   re-scored 62 rows and disagreed on five; round 2 re-scored 58 held-out rows,
   disagreed on two and found a third in the post-fix sample; round 3 re-scored
   47 difficult rows and disagreed on four. All twelve corrections went the same
   way — the author had been lenient. The rounds deliberately picked hard rows,
   so this is not a disagreement rate. That is still not an inter-annotator agreement rate over
   the full sample.
6. **Four tiers were never independently tested.** `CLEANED`, `SALT_STRIPPED`,
   `FUZZY_AUTO` and `FUZZY_REVIEW` have too few distinct values; the development
   sample consumed all of them, so their rates are carried from the data the
   rules were tuned on and are marked `carried` in the evaluation JSON. They
   hold 0.9% of the stratified weight (`carried_tiers_weight_share`).
7. **The post-fix sample confirms nothing about the repairs.** Its interval is
   uninformatively wide and it was scored with the same one annotator; the
   evidence that a repair holds is its regression test, not this sample.
8. **The query layer answers the nearest question it can.** "Is pembrolizumab
   safe in patients with autoimmune disease?" returns a drug profile rather than
   refusing. It refuses only when no entity links at all.
9. **`MEDI4736` stays ambiguous** although it is unambiguously durvalumab,
   because the contaminated synonym blocks the preferred-name rule. Other keys a
   contaminated synonym shares between drugs stay unread the same way in the question
   boxes (`5-fluorouracil` is also filed under capecitabine, `AK112` under two
   antibodies, `PD-1 mAb` under pembrolizumab and camrelizumab); before round 32 the
   question linker chose one of them by spelling. The relation map does not read these
   either: it reads a drug only by its ChEMBL preferred name (defect 15).
10. **A two-word personal name is indistinguishable from a short company name.**
    `Xiuning Le` is a person and `Shanghai Henlius` is a company; only an
    explicit credential (`MD`, `PhD`) is used to separate them, so the 36
    `Investigator` nodes are the credentialed ones and the rest stay `Company`.
    An earlier shape-based guess typed Accuray and Daiichi Sankyo as people.
11. **The registry-synonym rule errs toward refusal.** It removes some correct
    names along with the contaminated ones: misspellings it cannot tell from a
    different ingredient (`terelizumab` for tislelizumab, `slulimumab` for
    serplulimab), code names whose molecule record does not list them
    (`limertinib` for ASK-120067, `pankomab-gex` for gatipotuzumab, four
    variants under disitamab vedotin), and short abbreviations that are
    ambiguous across the vocabulary (`epi`, `hr3`, `il-2`). Each removal is a
    finding in the quality report with its reason, so they can be reviewed.
12. **The corporate map is a dated assertion.** Its 56 parent keys and 8
    same-entity keys were checked for the
    obvious changes (spin-offs, renames, the two Mercks), but continued legal
    existence of every subsidiary is unverified, and nothing re-checks the map
    when ownership changes.
13. **The prose check is an auxiliary screen, not a guarantee.** Answers from the
    model are no longer prose but structured claims checked exactly (see "Asking it
    things"). `src/claims.py`, which reads free prose clause by clause against the
    evidence, is kept for prose from elsewhere (the try-it page's box 4). Six
    adversarial rounds found 33, about 40, about 25, about 20, about 15 and then 8
    sentence shapes that got through it (reversed nouns, clefts, pronouns, counts
    and phases borrowed across entities, headings, relative clauses, kind words),
    and its repairs began to reject faithful answers (only 22 of 38 passed in round 6). Each
    shape found is a regression test, but it reads word order, not meaning, and is
    documented as able to miss unsupported claims and to reject correct ones.
14. **Provenance does not record the code version.** Snapshots carry their
    fetch time, but the graph does not store which revision of the rules built
    it, so a change that arrives with a new snapshot and a code change together
    cannot be separated from the database alone; only git history can.
15. **Refusal in the question boxes rests on markers it recognises.** The question
    boxes (2 to 4) find drug names in a sentence and do not read a name as the
    originator when a biosimilar suffix, an isotope, a label, a conjugated partner or
    a formulation word is attached to it. Those markers are word lists. In 31
    adversarial rounds on the relation map every round found new wording (a phrase
    placed between the joining word and the partner, new dye names); each was fixed
    and kept as a regression test, but wording outside the lists can still read a
    different product as the originator. That is why the relation map draws only an
    input that is, as a whole, one stored name, compared under one rule, and reads a
    drug only by its ChEMBL preferred name. A drug's other stored names are where
    products get filed under a molecule they are not, so the map does not read them
    and asks for the preferred name; the question boxes still read them:
    combination products under one ingredient (`Tobradex` under dexamethasone,
    `Oraqix` under lidocaine), formulations (`Myocet`, `LEP-ETU`), biosimilars under the
    reference molecule (`Inflectra`, `CT-P13`, bevacizumab's biosimilar codes), and wrong
    substances among the synonyms copied from trial registrations (`bupivacaine
    hydrochloride` under antimony, `13-cis retinoic acid` under tretinoin). Trade names
    of that kind found in a review of the dictionary are also refused in the question
    boxes, and a stored name the question linker refuses stays refused in the map
    however it is spelt; that also refuses a preferred name written with the same
    letters as a refused spelling (`CABOZANTINIB S-MALATE` beside `Cabozantinib
    (s)-malate`, which the resolver blocks). The resolver that builds the graph keeps its own lists, so a
    trial naming one of those brands may still be attached to the reference molecule
    in the graph; changing it would change the measured numbers, so it is left for a
    dictionary curation and a new measurement.

---

## Running it

```bash
pip install -r requirements.txt

python src/run_all.py              # fetch, resolve, check, build, score, render
python src/run_all.py --offline    # rebuild from the snapshots in data/raw

python -m pytest tests -q                    # 366 tests
python src/app.py                            # try-it page: http://localhost:8765 (relation map, name resolver, questions, claim check)
python src/curation_effect.py                # resolve twice, with and without curation
python src/apply_label_corrections.py --check
python src/query.py "Which companies are developing osimertinib?"
```

The dashboard is `web/index.html`; serve the folder (`python -m http.server`) or
open the file directly.

Nothing is fetched silently: `data/raw/*.json` are the fetched snapshots, each
stamped with the query that produced it and the time it was fetched. Later
stages read those and each other's outputs (`resolved.json`, the SQLite graph,
the gold CSVs). Keeping a source change and a logic change apart is up to git:
the artifacts do not record which code revision produced them.

---

## Repository

```
src/
  config.py                   disease scope, endpoints, limits
  ingest.py                   public API fetch -> data/raw/*.json snapshots
  textrules.py                named cleaning rules; every rule reports when it fires
  normalize.py                dictionary build, curation, entity resolution
  qc.py                       dictionary, record and graph quality checks
  graph.py                    SQLite knowledge graph, provenance, change history
  query.py                    entity linking, retrieval, answering, groundedness check
  structured.py               model answers as claims, each checked against the graph
  claims.py                   auxiliary clause-by-clause check of free prose
  app.py                      local try-it page (web/try.html)
  make_gold_sample.py         stratified sampling: dev / held-out test / post-fix
  apply_gold_labels*.py       the manual verdicts, with a reason for every "incorrect"
  apply_label_corrections.py  label errors found by independent re-score, with reasons
  curation_effect.py          resolve twice, with and without curation
  evaluate.py                 per-tier rates, Wilson and bootstrap intervals, stale labels
  run_all.py                  the whole pipeline
reports/
  gold_dev.csv                214 hand-scored rows
  gold_test.csv               172 hand-scored rows, held out
  gold_postfix.csv            58 hand-scored rows, after the repairs
  evaluation_*.json           the three scorings, raw and stratified
  curation_effect.json        the before/after of dictionary curation
  quality_report.json         every finding, with its evidence
tests/
  test_pipeline.py            24 tests, each pinning a real failure mode
  test_audit_round2.py        32 tests, one per defect the second and third audits found
codex_report.txt              the second independent audit, verbatim
codex_report_round3.txt       the third, verbatim
CODEX_R2_VERDICT.md           round 2: each finding reproduced, partly wrong, or missed
CODEX_R3_VERDICT.md           round 3, the same
CODEX_MAP_M1_VERDICT.md       the relation-map audit, rounds 1 to 38
audit_evidence_*/             the auditors' evidence files; rounds 20 to 38
                              of the map audit keep only the brief, the
                              report and the log (the replay files, about
                              1.5 GB, stay local; the round-26 log is left
                              out because it quotes a private note)
web/
  index.html                  the dashboard
```

## Sources and limits

Open Targets Platform (GraphQL), ChEMBL via Open Targets, and the
ClinicalTrials.gov API v2 — all public, no licensed dataset. Open Targets
data are released under CC0 1.0, ChEMBL data under CC BY-SA 3.0 (EMBL-EBI),
and ClinicalTrials.gov records are public-domain U.S. government data; the
copies in `data/raw/` keep those terms. Scope is
non-small cell lung cancer (`MONDO_0005233`) and the first 3,000
interventional trials the condition query returns, in the API's default order
— no sort is requested, so these are not necessarily the most recent.

This is a portfolio project. It is not medical advice, not a commercial
intelligence product, and its numbers describe this snapshot of this data only.
