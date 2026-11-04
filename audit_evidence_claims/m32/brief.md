# Round 32 of the relation-map review

Previous rounds: `audit_evidence_claims/m1` to `m31` (`REPORT.md`; m27 and m29 stopped early, so their `attacks/` folders are the record). All repairs are in `CODEX_MAP_M1_VERDICT.md`. Review the latest commit on HEAD. Run the tests with `python -m pytest tests -q -p no:cacheprovider`; expect 361. Start the page with `python src/app.py <port>` on a port other than 8765 and exercise it over HTTP.

## What changed since round 31: a design change, not another word-list repair

Rounds 20 to 31 each found new wording that the question linker's product markers did not cover. The relation map no longer depends on those markers. See the section "Before round 32" in `CODEX_MAP_M1_VERDICT.md`, and `src/app.py` `Engine.explore`, `_sig`, `_latin`.

- **P32-1.** `explore` draws only when the whole input is one name. The linker must read exactly one entity, and its matched text must have the same letters, digits and symbols as the input (`_sig`: NFKC, casefold, any script). Case, spaces, punctuation and ®/™/© do not count. Anything else returns `not_one_name`, and the page asks for the name alone.
- **P32-2.** If any part of the input is refused, the whole input is refused.
- **P32-3.** A name stored for several live nodes is not drawn. The reply is `choose`: the nodes are listed and the reader clicks one, which loads it by id.
- **P32-4.** Lower-case `nct`/`chembl`/`ensg` ids are read. The whole input can be a company key or target name when `_latin(text)` equals the dictionary key, so a symbol the key would drop still blocks it (for example "Merck & Co").
- **P32-5.** This change is in the question linker, `src/query.py` `_whole_name` and the end of `_link`. A canonical key shared by several drugs is no longer decided by its spelling; only a drug's own preferred name chooses it. Inside such a key, a shorter name is not read either. Before, "medi4736" read as atezolizumab and "5-fluorouracil" as capecitabine.
- **New tests:** `tests/test_app.py::test_the_map_draws_only_a_whole_stored_name` and `test_a_key_shared_by_several_drugs_is_not_decided_by_spelling`. Older map tests that drew a centre from a longer input now go through `_page`: the map must not draw, and the question linker's reading is checked instead.
- **Docs:** README defect 15 (both languages) records that the question boxes still rely on the linker's markers for free text. Defect 9 records the shared keys. Section 0 of `web/try.html` states the one-name rule.

## Scope and approval bar

The subject is the relation map: section 0 of `web/try.html`, `POST /api/explore`, `Engine.explore`. The guarantees are those in the original brief below, with guarantee 3 now read as follows: the map draws a node only for an input that is, as a whole, one stored name of that node (or its id). It never draws a refused product, tracer or conjugate as the originator, and never draws one of several nodes that share a name.

1. Re-run every earlier reproduction from m1 to m31 against the map, and mark each finding FIXED or NOT FIXED. Reuse the earlier scripts. Inputs that were longer than a name should now be refused, `not_one_name`, `choose` or `not_found`, never a drawn originator.
2. Attack the new rule:
   - any input that draws a node the input does not name as a whole
   - a whole stored name that is in fact a different product (a data problem; say so, and separate it from code problems)
   - Unicode, symbols and invisible characters that `_sig`/`_latin` mishandle
   - the id path
   - the `choose` reply (live nodes only, injection-safe page markup, click-through)
   - company/target whole-name reads
   - retired nodes
   - anything the page text claims that the code does not do
3. Check P32-5 for regressions in the question boxes (2 to 4) and the demo examples. Report over-refusals as should-fix, not blockers.
4. Re-check guarantees A to G of the original brief briefly; earlier rounds approved them.

### Out of scope as blockers (recorded)

- The question boxes' free-text refusal relies on word lists (README defect 15). A leak there is a note, not a map blocker.
- Known data limitations, awaiting the owner's curation decision:
  - ChEMBL lists bevacizumab biosimilar development codes as bevacizumab synonyms.
  - An AACT synonym maps 13-cis-retinoic acid to CHEMBL38 tretinoin (M23-D1).
  - "Roche" is stored as a folic acid alias. The map now asks the reader to choose.
- Known over-refusals listed in `CODEX_MAP_M1_VERDICT.md` (M5-S2, rapamycin forms, Trastuzumab--vcmmae conjugate, 9-amino-20(s)-camptothecin, il-6ra, TAK-659F, GS-11CAL-101, 3en3hg4wsw, an ADC named with its own payload beside it). A longer input not being drawn is the new rule, not an over-refusal.

Approval bar: no known way for the map to draw a node for an input that is not, as a whole, one stored name or id of it. That includes a refused product drawn as the originator, one of several same-named nodes drawn without the reader's choice, a wrong relation or direction, a value that differs from the stored one, and script injection. Report should-fix items separately from blockers.

Write scratch files only under `audit_evidence_claims/m32/`. Put the report in `audit_evidence_claims/m32/REPORT.md`. Do not edit tracked files. End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.

--- original brief (round 1) ---
Read `audit_evidence_claims/m1/brief.md` for the original guarantees 1 to 5 and the checks A to G.
