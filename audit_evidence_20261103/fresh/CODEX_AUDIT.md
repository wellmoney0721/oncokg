# Independent audit brief

Run this against this repository with an agent that did **not** write it:

```bash
npm i -g @openai/codex          # or any other independent reviewer
cd <this repo>
codex exec "$(cat CODEX_AUDIT.md)"
```

Paste the output back to whoever is maintaining the project. A previous round
of this exercise found seven real defects, listed at the bottom so you can check
whether the repairs actually hold rather than taking the README's word for it.

---

## Your role

You are auditing a job-application portfolio project. Be skeptical and
adversarial. Your job is to find what is **wrong**, not to confirm it works.
Finding nothing is a failed review. The candidate will be asked to defend every
figure in a technical interview with a domain expert, so a claim that cannot be
reproduced from this repository's own artifacts is a serious finding, and a
claim that is reproducible but misleading is a worse one.

Do not fix anything. Report only, with exact `file:line` or exact JSON field
for every finding.

## What the project is

A Python pipeline over public non-small cell lung cancer (NSCLC) data. It:

1. fetches Open Targets (GraphQL), ChEMBL drug synonyms via Open Targets, and
   ClinicalTrials.gov API v2 interventional studies, snapshotting each to
   `data/raw/*.json`
2. resolves messy free-text intervention strings (`Pembrolizumab 100 mg I.V
   single dose`, `Anlotinib hydrochloride capsule`, `Placebo to Match ZD6474`,
   `[18F]F-AraG PET imaging`) to ChEMBL identifiers through a tiered resolver
   with reason codes
3. curates the reference dictionary *before* matching, because ChEMBL's synonym
   lists are contaminated (atezolizumab's contains avelumab and durvalumab)
4. builds a SQLite knowledge graph with provenance and a change log
5. answers questions with a groundedness self-check
6. scores precision on three hand-labelled samples

Entry points: `python -m pytest tests -q`, `python src/run_all.py --offline`,
`python src/curation_effect.py`, `python src/query.py "<question>"`.

## The central vulnerability

**One annotator.** Every `correct` / `incorrect` verdict in
`reports/gold_dev.csv`, `reports/gold_test.csv` and `reports/gold_postfix.csv`
was assigned by the same person who wrote the matching rules. Five labels were
already found to be leniently wrong (see `src/apply_label_corrections.py`).
Assume there are more.

---

## What to do

### 1. Reproduce

Run `python -m pytest tests -q` and `python src/run_all.py --offline`. Record
exit codes, stderr, and test counts. Before and after, run `git status` and
`git diff --stat`: a rebuild from unchanged snapshots should produce no
substantive diff in any committed artifact. Timestamps are fine; different
counts or different precision figures are a major finding, because it would
mean the committed numbers are not what the code produces.

Then run `run_all.py --offline` a **second** time and confirm
`reports/graph_stats.json` reports `added: 0, changed: 0, retired: 0`.

Unzip a fresh copy into an empty directory and repeat. Report any file the
repository needs that the archive does not contain, and any import that only
resolves because of state in the original working directory.

### 2. Check every number in both READMEs against the artifacts

For each figure in `README.md` and `README.ko.md`, state VERIFIED (with the
exact field and value you found), MISMATCH (claimed X, artifact says Y), or
UNVERIFIABLE (no artifact backs it). The figures include, but are not limited
to:

- dev / held-out test / post-fix: raw precision 92.0% / 91.3% / 97.4% on
  137 / 115 / 38 accepted rows; stratified 97.7% / 96.9% / 99.1%
- coverage 78.2%, 4,969 of 6,351
- 2,742 distinct drug strings; 2,175 distinct condition strings; 3,000 trials
- FUZZY_REVIEW would-have-been-correct 37.5%; placebo guard 8/8 on the held-out
  sample
- curation: ambiguous resolutions 2,193 → 69, exact 1,997 → 4,056
- graph: 6,476 nodes, 17,591 live edges, and the per-relation table
- `SPONSORS_TRIAL_OF`: 3,187 edges, 41.2% industry / 58.8% non-industry
- the dictionary defect table (134 / 124 / 80 / 78 / 47 / 7 / 6)

Sources: `reports/evaluation_dev.json`, `reports/evaluation_frozen_test.json`,
`reports/evaluation_postfix.json`, `reports/curation_effect.json`,
`reports/quality_report.json`, `reports/graph_stats.json`, and the SQLite
database under `data/processed/`.

### 3. Recompute the statistics yourself

Do not trust `src/evaluate.py`. Load `reports/gold_test.csv` directly, count
accepted-tier rows by verdict, and compute the raw precision and a Wilson 95%
interval with your own code. Compare to `evaluation_frozen_test.json`.

Then attack the stratified estimator in `src/evaluate.py`:

- Is weighting by `population_unique` defensible, or does it inflate the result?
  (The sample is drawn by a disproportionate per-tier quota, so *some*
  reweighting is required — the question is whether this is the right one.)
- The interval is built by propagating per-tier Wilson bounds. Is that sound, or
  is it either too conservative or not conservative enough? Would a bootstrap
  over the sampled rows give a materially different answer? Compute one.
- Four tiers carry their rates forward from the dev sample. Quantify exactly how
  much of the headline depends on carried-forward rates, and recompute the
  estimate with those tiers excluded.
- The post-fix interval is 71.5–99.8. Is that figure meaningful at all?

### 4. Re-score the labels

Sample at least 40 rows from `reports/gold_test.csv`, deliberately favouring the
hard ones: `FUZZY_AUTO`, `SALT_STRIPPED`, `PARENTHETICAL`, `CONTAINED_ALIAS`,
combination splits, anything with a development code, anything with a digit,
anything non-English, anything containing "placebo" or "biosimilar".

For each, judge independently from pharmacology/oncology knowledge whether the
resolution is correct. Look things up — ChEMBL, DrugBank, PubChem and
ClinicalTrials.gov are all public. Report every row where you disagree with the
label, with the surface string, the resolved target, the author's verdict, your
verdict and your evidence. Then state what your disagreements do to the
headline figure.

Check `src/apply_label_corrections.py` separately: are those five corrections
themselves right, and is the script's before/after guard sound?

### 5. Attack the domain logic

Read `src/normalize.py` and `src/textrules.py` as a pharma reviewer:

- `SALTS` — does stripping any of these change the molecule? Is the
  salt-vs-free-base distinction ever clinically meaningful here? Are salt forms
  handled consistently, or do some stay as separate nodes while others fold?
- `CLASS_TERMS` and `RE_CLASS_PATTERN` — construct class terms that still fall
  through to `UNRESOLVED` with no reason code. `RE_CLASS_PATTERN_EXEMPT` exempts
  INN stems; find a class term it wrongly exempts, or a real drug it wrongly
  blocks.
- `RE_COMBO` — does splitting on `and` / `or` / `/` break any single product
  whose name legitimately contains one?
- `RE_DISTINCT_PRODUCT` and `DISTINCT_PRODUCT_ALIASES` — find a biosimilar or
  reformulation that still resolves to its originator. Find a legitimate product
  these wrongly refuse.
- `CONTAINED_ALIAS` with `MIN_CONTAINED_LEN = 7` and the greedy segmentation —
  find a false positive.
- `CURATED_PARENTS` — verify every mapping is correct and current. Check whether
  each acquisition closed, whether each subsidiary still operates under that
  name, and whether any company is now independent. Report stale entries.
- `looks_like_person` — find a company it types as `Investigator`, or an
  investigator it leaves as `Company`.

Import the resolver and run it on strings you invent:

```python
import sys; sys.path.insert(0, "src")
import normalize as N, textrules as T
```

### 6. Attack the graph semantics

`src/graph.py` derives `SPONSORS_TRIAL_OF` from `SPONSORS` + `EVALUATES`. An
earlier version called this `DEVELOPS` and was removed as unsound. Check that
the replacement does not smuggle the same claim back in through its properties,
confidence, or the way `query.py` presents it. Query the SQLite database
directly and look for edges that assert something the sources do not support.

Also check: does `retire_unseen` actually retire? Do nodes persist across
rebuilds in a way that leaves stale rows? Does every edge carry complete
provenance, or are there edges with `source_record: null`?

### 7. Attack the retrieval and answering layer

Run `src/query.py` on hostile inputs:

```
python src/query.py "Which companies are developing osimertinib?"
python src/query.py "Is pembrolizumab safe in patients with autoimmune disease?"
python src/query.py "What is the capital of France?"
```

The groundedness check claims to report `applicable: false` on the template path
because checking a template built from the evidence against that evidence is
circular. Verify that is actually what happens. Then, with an API key set if you
have one, try to get a fabricated claim past the check — a false relation, a
lowercase clinical assertion, an invented figure. The function admits it cannot
verify relations; find out what else it cannot verify.

### 8. Overclaims

Quote every sentence in either README that states as a general property
something true only of this snapshot, or that you can construct a counter-example
to. Try to actually construct them.

---

## Report format

Under 1,200 words. No hedging. Structure:

- **BLOCKERS** — factually wrong; must be fixed before this goes to an employer
- **LABEL DISAGREEMENTS** — rows you re-scored, and what they do to the headline
- **DOMAIN ERRORS** — what a pharma expert would catch
- **STATISTICAL OBJECTIONS** — where the method is wrong or oversold
- **OVERCLAIMS** — README sentences to soften, quoted exactly
- **WHAT SURVIVED** — brief and honest; the candidate needs to know what to lean on

---

## Defects found in the previous round

Check whether each repair is real, complete, and did not introduce something
worse. Do not assume a fix works because the README says so.

| # | Defect | Claimed repair |
| --- | --- | --- |
| 1 | Node count stated as 6,481; artifacts said 6,475 | All figures regenerated from artifacts |
| 2 | `class_term_as_synonym` stated as 56; report said 134 | Corrected |
| 3 | Coverage stated as 78.3%; evaluator printed 78.2% | Corrected |
| 4 | Interval was a normal approximation labelled Wilson; collapsed because 88% of weight sat in tiers scoring 100% | Per-tier Wilson bounds propagated |
| 5 | Sample size (172) quoted as the precision denominator (115) | Both reported, with `raw_sample_precision` |
| 6 | "Curation cut ambiguity 2,008 → 66" reproducible from nothing | `src/curation_effect.py` measures it: 2,193 → 69 |
| 7 | `DEVELOPS` edges: 58.8% had non-industry lead sponsors; graph asserted NCI develops paclitaxel | Renamed `SPONSORS_TRIAL_OF`, sponsor class on the edge, no development claim |
| 8 | Groundedness check circular on the default path; numeric match was substring-based | `applicable: false` on template path; tokenised numbers |
| 9 | Dead `break_outer = False` stripped sector words mid-name | Corporate suffixes stripped anywhere, sector words only trailing, academic names exempt |
| 10 | Corporate map stale: Sandoz, BeiGene, Seagen, Mirati; Merck KGaA absent entirely | Updated and split |
| 11 | Bare `platinum` was a confidence-1.00 edge to the element in 7 trials | Blocked |
| 12 | Biosimilars resolved to originators | `BLOCKED_DISTINCT_PRODUCT` tier |
| 13 | Dashboard serialised a `set`, non-deterministic | Sorted |
| 14 | Individual investigators were `Company` nodes | `Investigator` type, credential-based only |
