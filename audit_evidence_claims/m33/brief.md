# Round 33 of the relation-map review

Read the brief for round 32 at `audit_evidence_claims/m32/brief.md` (scope, guarantees, the approval bar) and its report at `audit_evidence_claims/m32/REPORT.md`. Repairs since then are in `CODEX_MAP_M1_VERDICT.md`, in the sections "Round 32" and "pre-33". Review the latest commit on HEAD. Run tests with `python -m pytest tests -q -p no:cacheprovider` (expect 362). Start the page with `python src/app.py <port>` (not 8765).

## What changed since round 32

The map no longer compares the input with the linker's window. It looks the input up in its own index of stored names. Everything is in `src/app.py` `Engine.__init__` and `Engine.explore`, plus `_sig` and `_add_name`.

- **The comparison rule.** `_sig` drops trademark signs before NFKC, then applies casefold, strips accents, and drops categories P/Z/C. Every other letter (any script), digit and symbol is kept. Every name source is indexed by `_sig`.
- **Sources the map reads:**
  - a drug's ChEMBL preferred name and trade names
  - a small molecule's ChEMBL synonyms
  - every node's own label
  - target symbols
  - company and disease keys, matched only when `_sig(text)` equals the dictionary key (letters and digits only)
- **Sources the map does not read, each with its own reply:**
  - `registry_name`: synonyms found only in trial registrations (AACT). These are the sources of the round-32 data findings D1 to D3, and of 13-cis retinoic acid → tretinoin.
  - `biologic_synonym`: an antibody's or protein's ChEMBL synonyms. These mix the originator's codes with biosimilar codes and brands filed under the reference molecule (CT-P13 and Zessly under infliximab, ABP 980 under trastuzumab, the bevacizumab codes).
- **Choosing and refusing:**
  - All live candidates under one signature are collected. More than one gives `choose`; exactly one is drawn.
  - The linker still runs first, and any refused part refuses the whole input.
- **Brand list, in the question linker (`src/query.py`).** `_OTHER_PRODUCT_NAMES` holds trade names that ChEMBL files under a molecule although they name another product: European biosimilar brands and formulations such as Myocet, Fyarro, Megace ES, Jelmyto and Locteron. Both the map and the question boxes refuse them. The list was built by reviewing every biologic trade name in the dictionary; see the comment in the code.
- **Misfiled brand.** `_MISFILED` in `src/app.py`: Kadcyla is also filed under trastuzumab; the map reads it only as trastuzumab emtansine.
- **Question linker.** In a question, a key shared by several drugs is read as the drug whose own preferred name it is, letter for letter. This fixes the inherited "What trials evaluate NICOTINE?" case.
- **Docs:** README defects 9 and 15 (both languages) and section 0 of `web/try.html`.

## What to do

1. Re-run every round-32 finding: M32-B1 to B4, D1 to D3 and the should-fix items. Mark each FIXED or NOT FIXED with exact inputs. Also re-run the earlier historical replays (m1 to m31) against the map.
2. Attack the new design:
   - any input drawn for a node of which it is not, as a whole, one stored name under `_sig`
   - a stored name the map still reads (ChEMBL preferred name, trade name, small-molecule synonym, node label, target symbol, company or disease key) that denotes a different product than the node drawn
   - inconsistency between the name sources
   - Unicode, symbols, invisible characters
   - the `choose`, `registry_name` and `biologic_synonym` replies, including their markup safety
   - retired nodes
   - the id path
3. Check the question linker changes (`_OTHER_PRODUCT_NAMES`, the shared-key preferred-name rule) for regressions in the question boxes and the demo examples.
4. Re-check guarantees A to G briefly.

Report data problems (a stored name the map still reads, with a wrong identity) separately from code problems. Give the exact input, the source record (alias, source, alias_type) and an independent identity reference.

Recorded and not blockers:
- Leaks of free text in the question boxes (README defect 15).
- The resolver that builds the graph keeps its own brand lists, so a trial naming a biosimilar brand may be attached to the reference molecule in the graph (README defect 15).
- Known over-refusals: the list in `CODEX_MAP_M1_VERDICT.md`, registry-only names, antibody development codes, and two tracer drugs refused by their own labels.

Write scratch files only under `audit_evidence_claims/m33/`. Put the report in `audit_evidence_claims/m33/REPORT.md`. Do not edit tracked files. End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.
