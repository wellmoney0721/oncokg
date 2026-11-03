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

Precision was measured **three times, on three disjoint hand-scored samples**,
because a number measured on the data you tuned against is not a measurement.

| sample | rows | accepted rows | raw precision | stratified estimate |
| --- | --- | --- | --- | --- |
| development | 214 | 137 | 92.0% (86.2–95.5) | 97.7% (86.7–99.3) |
| **held-out test** | **172** | **115** | **91.3% (84.7–95.2)** | **96.9% (85.7–99.0)** |
| post-fix | 58 | 38 | 97.4% (86.5–99.5) | 99.1% (71.5–99.8) |

Two numbers, because **the sample size is not the precision denominator.** Only
rows in an accepting tier can be right or wrong about a match; the rest are
refusals, scored separately. Of the 172 held-out rows, 115 assert a match and
105 of those are correct. Quoting 172 as the denominator overstates the
evidence, and an earlier version of this file did exactly that.

The stratified estimate is the higher of the two and it is **not** the raw
number dressed up. The sample is drawn by a disproportionate per-tier quota, so
reweighting by each tier's share of the population is required, not optional —
the raw mean is the biased figure. But reweighting is also what lifts the result
to 96.9%, so both are reported side by side and neither travels alone.

Intervals are propagated from per-tier **Wilson** bounds. An earlier version
used a normal approximation on the stratified mean and published
`99.1% [98.4, 99.8]`. Because 88% of the weight sat in tiers that scored 100%,
the binomial variance term was exactly zero for those tiers and the interval
collapsed to a width no sample of this size can support. A tier with 40 of 40
correct is not known to be 100% accurate.

Coverage of substance-like strings is **78.2%** (4,969 of 6,351). Precision and
coverage are reported separately on purpose: coverage can always be bought by
lowering a threshold, and one number hides that trade.

Two more figures matter as much as the headline:

* **37.5%** — how often a proposal the pipeline *held back for review* would
  actually have been right. A low number here is the evidence that the automatic
  threshold is not set too low.
* **100%** (8/8, Wilson 67.6–100) — the placebo guard on the held-out sample,
  after the development sample showed it was over-blocking combination arms.

---

## What an independent review found

The labels in all three samples were assigned by one annotator — the same person
who wrote the matching rules. Saying so in a limitations section is not the same
as testing it, so the project was handed to independent reviewers with
instructions to disagree, and they did. Everything below is a defect they found
and this repository now carries the fix.

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
response rate" passed against an NCT id containing `47`; it is tokenised now.
What the check still cannot do is verify a *relation* — "AstraZeneca has
discontinued this drug" passes because both tokens are present — and that limit
is now stated in the function rather than implied away.

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
free while its competitor was fully mapped. The two Mercks are different
companies; the map now says so, and the bare key `merck` is deliberately absent
because an unqualified "Merck" is genuinely ambiguous.

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
extracts every component, and whatever is left over is emitted as an explicit
unresolved residue rather than dropped.

**A biosimilar is not its originator.** `Bevacizumab Biosimilar HLX04` and
`Bevacizumab-Pfizer` name separate regulatory products. Resolving them to
BEVACIZUMAB puts a competitor's asset on Genentech's molecule and makes the
asset under study vanish. There is no identifier for these in the vocabulary, so
they are refused with a reason code. The same rule covers liposomal and
albumin-bound reformulations, and `abraxane`, `doxil`, `caelyx` and `onivyde`
are removed from the synonym index before any record is matched.

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
errors. ChEMBL's synonym list for **atezolizumab** contains `avelumab`,
`durvalumab`, `adebrelimab` and `medi4736` — four other molecules. Durvalumab's
contains `atezolizumab`, `toripalimab` and `durvalumab placebo`.

So the dictionary is curated before any record is matched against it, by rules
that each record what they changed:

| defect | found | what the rule does |
| --- | --- | --- |
| `class_term_as_synonym` | 134 | `anti-PD-L1`, `ICI`, `pd-l1 blockade` removed from the lookup index |
| `genuinely_ambiguous_alias` | 124 | kept ambiguous; records matching it go to review |
| `cross_drug_synonym` | 80 | an alias that is another molecule's **preferred name** is bound to that molecule; the records listing it carry a suspected upstream error |
| `parent_child_collapse` | 78 | salt and child forms folded into the parent |
| `suspected_duplicate_entity` | 47 | two identifiers that look like one substance — reported, never auto-merged |
| `distinct_product_alias` | 7 | `abraxane`, `doxil`, `caelyx` dropped: same moiety, different product |
| `placebo_string_in_synonym_list` | 6 | `durvalumab placebo` dropped before indexing |

Measured by resolving the corpus twice, curation cuts ambiguous resolutions from
**2,193 to 69** and raises exact matches from **1,997 to 4,056**
(`reports/curation_effect.json`).

---

## The graph

6,476 nodes and 17,591 live edges over `Company`, `Investigator`, `Drug`,
`Target`, `Disease` and `Trial`.

| relation | edges |
| --- | --- |
| `SPONSORS` | 4,652 |
| `EVALUATES` | 4,449 |
| `SPONSORS_TRIAL_OF` *(derived)* | 3,187 |
| `STUDIES` | 2,774 |
| `ACTS_ON` | 2,186 |
| `ASSOCIATED_WITH` | 300 |
| `PARENT_OF` | 43 |

Every edge carries its **source**, the **source record**, the **fetch
timestamp**, the **resolution tier** that produced it and a **confidence**. Only
accepted resolutions become edges — ambiguous, blocked and unresolved components
stay in the quality report, because the graph is the part that claims to be true.

The one derived relation says only what the evidence shows. Of its 3,187 edges,
41.2% have an industry lead sponsor and 58.8% do not; the class rides on the
edge so a consumer can filter, and no confidence is manufactured from the trial
count.

Re-running against a newer snapshot **retires** edges instead of deleting them
and writes every attribute change to a change log, so "when did this relationship
appear, and on what evidence?" stays answerable. Rebuilding from unchanged
sources records zero changes.

A corporate parent is modelled as a `PARENT_OF` **relationship**, not as a
rename. An earlier version renamed MedImmune to "AstraZeneca" and produced two
nodes with one label, after which a lookup by name silently picked whichever one
it found first.

---

## Asking it things

Questions are linked against the same dictionary the pipeline uses, so a question
naming a trade name finds a graph that stores a ChEMBL id.

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

With `ANTHROPIC_API_KEY` set, a language model writes the prose from the
retrieved evidence and nothing else, and the result is checked back against that
evidence: entities and tokenised numbers in the generated text must appear in
the retrieved set. With no key, the same evidence is rendered directly and the
check reports `applicable: false`, because a template built from the evidence
cannot fail a test against it. The facts are identical either way; only the
prose changes. The pipeline has no required dependency on a model.

---

## Known defects

Left listed rather than quietly assumed away.

1. **The placebo rule needs a separator.** `Placebo Drug: Docetaxel Drug:
   Carboplatin` has no `+` or `and`, so it reads as a reference arm and two
   administered drugs are dropped. Fix: treat a repeated `Drug:` label as a
   separator.
2. **Regimen acronyms are neither resolved nor blocked.** `HS-20117+FOLFIRI`
   and `+mFOLFOX6` drop 5-FU, leucovorin, irinotecan, oxaliplatin and
   capecitabine on the floor. They need a regimen expansion table.
3. **Vector words match as products.** `adenovirus` inside `dendritic
   cell-adenovirus CCL21 vaccine` resolves to a specific oncolytic product.
4. **Coverage is capped by scope.** The vocabulary holds only drugs Open Targets
   links to NSCLC, so `propranolol` is correctly refused and still counts against
   coverage. Widening to the full ChEMBL drug set would need its own precision
   measurement.
5. **Still one annotator, now with one independent re-score.** Five labels were
   corrected after review; the other 62 re-scored rows agreed. That is better
   than the previous "one annotator, unchecked", and it is still not an
   inter-annotator agreement rate over the full sample.
6. **Four tiers were never independently tested.** `CLEANED`, `SALT_STRIPPED`,
   `FUZZY_AUTO` and `FUZZY_REVIEW` have too few distinct values; the development
   sample consumed all of them, so their rates are carried from the data the
   rules were tuned on and are marked `carried` in the evaluation JSON. They
   hold about 1% of the stratified weight.
7. **The post-fix interval is uninformatively wide** (71.5–99.8). With only 10
   EXACT rows in a 58-row sample, no stratified interval over that weight can be
   tight. It confirms the repairs; it does not re-measure the pipeline.
8. **The query layer answers the nearest question it can.** "Is pembrolizumab
   safe in patients with autoimmune disease?" returns a drug profile rather than
   refusing. It refuses only when no entity links at all.
9. **`MEDI4736` stays ambiguous** although it is unambiguously durvalumab,
   because the contaminated synonym blocks the preferred-name rule.
10. **A two-word personal name is indistinguishable from a short company name.**
    `Xiuning Le` is a person and `Shanghai Henlius` is a company; only an
    explicit credential (`MD`, `PhD`) is used to separate them, so the 36
    `Investigator` nodes are the credentialed ones and the rest stay `Company`.
    An earlier shape-based guess typed Accuray and Daiichi Sankyo as people.

---

## Running it

```bash
pip install -r requirements.txt

python src/run_all.py              # fetch, resolve, check, build, score, render
python src/run_all.py --offline    # rebuild from the snapshots in data/raw

python -m pytest tests -q                    # 24 tests
python src/curation_effect.py                # resolve twice, with and without curation
python src/apply_label_corrections.py --check
python src/query.py "Which companies are developing osimertinib?"
```

The dashboard is `web/index.html`; serve the folder (`python -m http.server`) or
open the file directly.

Nothing is cached silently: `data/raw/*.json` are the fetched snapshots, each
stamped with the query that produced it and the time it was fetched, and every
later stage reads only from those files. A changed result can always be traced to
either the source changing or the logic changing, never both at once.

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
  make_gold_sample.py         stratified sampling: dev / held-out test / post-fix
  apply_gold_labels*.py       the manual verdicts, with a reason for every "incorrect"
  apply_label_corrections.py  label errors found by independent re-score, with reasons
  curation_effect.py          resolve twice, with and without curation
  evaluate.py                 per-tier rates, Wilson intervals, stratified precision
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
web/
  index.html                  the dashboard
```

## Sources and limits

Open Targets Platform (GraphQL), ChEMBL via Open Targets, and the
ClinicalTrials.gov API v2 — all public, no licensed dataset. Scope is
non-small cell lung cancer (`MONDO_0005233`) and the most recent 3,000
interventional trials the condition query returns.

This is a portfolio project. It is not medical advice, not a commercial
intelligence product, and its numbers describe this snapshot of this data only.
