# Round 12 independent refusal attacks

Reviewed HEAD `d9260a1ea544cf7bb80415383667784e0aba146a`. One confirmed P1 blocker remains: a punctuated isotope embedded in a stored chelator-bearing tracer alias maps to the unlabelled originator. It is inherited from HEAD^; it is not introduced by this commit. The newly added immediate-neighbour controls themselves work.

## M12-B1 — a stored tracer alias with a chelator escapes all refusal stages

**Exact HTTP input:** `POST /api/explore`, JSON `{"text":"[89Z.r]-DFO-daratumumab"}`.

**Actual:** HTTP 200, centre **DARATUMUMAB / CHEMBL1743007**, matched alias **`89zr-dfo-daratumumab`**, **2 live trials**, with no refusal. Trial and sponsor questions each return **2 originator evidence rows**. The spelling `89Z_r-dfo-daratumumab` also leaks, as do `89Z.r-dfo-daratumumab`, `89Z.r-dfo daratumumab`, and `89Z.r dfo daratumumab`. Appending `, osimertinib` still chooses DARATUMUMAB as the centre. [Current and predecessor stages](focused_results.json), [compact results](focused_summary.json), [actual CLI HTTP](new_leaks_http.json).

Controls **`89Zr-dfo-daratumumab`** and **`[89Zr]-DFO-daratumumab`** refuse and return zero trial/sponsor evidence. Bare `daratumumab` remains available. These are the same stored tracer name, differing only in the punctuation that positive lookup discards. No outside pharmacology assumption is needed to establish the identity: the repository's index maps `89zrdfodaratumumab` to the single AACT synonym `89zr-dfo-daratumumab` for CHEMBL1743007; both candidate and refused control have exactly that key. [Dictionary and predicate evidence](dictionary_evidence.json).

| Stage | `[89Z.r]-DFO-daratumumab` |
|---|---|
| Raw resolver | `CONTAINED_ALIAS` to CHEMBL1743007; no blocked component |
| Resolver veto | `{}` |
| Item linker | Drug DARATUMUMAB; no Refused entity |
| Whole-name shortcut | `None`; no refusal is overridden |
| Public linker | Drug DARATUMUMAB; no Refused entity |
| Map / QA | Originator centre; 2 trial rows / 2 sponsor rows |

For the underscore variant the raw resolver reports `ALIAS`, also without a blocked component. This is specifically an all-stage miss, not a flaw where the map disregards a correctly refused entity.

**Cause, by code path:**

1. Positive lookup erases punctuation and resolves the complete key at `src/query.py:404-417`; `canonical_key` is `src/textrules.py:339-346`.
2. `_alnum_words` instead separates the candidate into `['89Z', 'r', 'DFO', 'daratumumab']` (`src/query.py:111-113`). `_marked`'s inside-name checks still test one- or two-word runs, joined with a space (`src/query.py:258,277-279`). Both `is_isotope_label('89Z')` and `is_isotope_label('89Z r')` are false, although `is_isotope_label('89Zr')` is true (`src/textrules.py:289-298`).
3. The new glued-neighbour checks examine only words outside the consumed name (`src/query.py:264-276`). The full alias is already the matched name, leaving no isotope neighbour to examine.
4. The new isotope-plus-same-drug-key check sees prefix `89zr`, but requires the remainder `dfodaratumumab` to be an independently stored key for this same drug (`src/query.py:282-286`). That remainder has **no index entry**. The unqualified key `daratumumab` exists, but the chelator sits between it and the isotope.
5. `_qualified` supplies punctuation-to-hyphen and punctuation-to-space variants, not an inside-element glued variant (`src/query.py:125-141`). The raw tracer pattern likewise cannot read `89Z.r` (`src/textrules.py:303-313`; raw resolver guard `src/normalize.py:740-745`). The surviving positive hit is then selected normally by `Engine.explore` (`src/app.py:87-95`).

**Required outcome:** preserve tracer identity across punctuation accepted by positive alias lookup when an isotope is within a consumed stored name, including a chelator between the isotope and the bare drug. This should not depend on the isotope-stripped remainder being another alias. Keep the explicitly accepted lone-name/over-refusal controls separate. No source edits are proposed or made by this audit.

## Other attacks and scope

The direct probe covers **41** candidate/control inputs against current Engine and the exact HEAD^ query module. Only query.py is swapped for that comparison; app, normalization, rules and database remain current. It is a module counterfactual, not a reconstructed old deployment. The DFO failure occurs in both versions. [Probe](focused.py), [comparison outputs](focused_results.json).

The immediate-neighbour fixes remain effective in these controls: `[89Z.r] trastuzumab`, `trastuzumab [89Z.r]`, and `bevacizumab a - w w b` refuse; the latter followed by `, osimertinib` selects only OSIMERTINIB and discloses the refusal. `osimertinib 80 mg`, `paclitaxel 2 cycles`, and `cisplatin 75 mg/m2 day 1` retain their expected drugs. Historical exhaustive replays are the other worker's responsibility.

Additional exploratory observations are retained but **not counted as separate blockers**:

- `[89Z.r]-labelled trastuzumab` has the same key as refused `[89Zr]-labelled trastuzumab` yet draws TRASTUZUMAB with 12/12 QA evidence. Ordinary `trastuzumab labelled with [89Zr]` and parenthesized descriptor forms also leak. Similar non-punctuated descriptor-distance forms already existed in m11/root_checks/fresh_probe.json and were explicitly left unpromoted in m11/attacks/FINDINGS.md. These are inherited observations, not newly introduced regressions. [Prior observation comparison](dictionary_evidence.json).
- `lip.osomal doxorubicin` and `b.i.o.similar bevacizumab` bypass lexical qualifier recognition while their conventional spellings refuse. These unusual respellings are supplementary evidence, not necessary to the verdict.
- `Lutetium (177L.u) dotatate` bypasses the refusal of its unpunctuated alias. Its selected centre is already **LUTETIUM OXODOTREOTIDE LU-177**, so it is **not claimed as an unlabelled-originator leak**. Other internal-isotope inventory entries include chemical locants. [Internal inventory](inside_alias_inventory.json), [prefix inventory](prefix_alias_inventory.json). The inventory was used to find and distinguish the DFO/daratumumab case, not to count every isotope-shaped alias as a defect.

The CLI HTTP confirmation issued **76 requests**, all HTTP 200. Served page bytes match `web/try.html`; database bytes were unchanged; the owned server on **8962** was terminated and its port is closed. [Lifecycle](new_leaks_lifecycle.json). Direct stage probes reopen SQLite with `mode=ro`; all answer calls use the no-model Engine path. All scripts/results are under m12/attacks. [Reuse manifest](reuse_manifest.json).

## Spec axis

The exact m11 repairs work for their tested immediate-neighbour cases, but the original guarantee still fails: a normalized spelling of the repository's own refused `89zr-dfo-daratumumab` tracer is drawn as DARATUMUMAB. Every refusal stage misses it; the complete positive alias match consumes the isotope, and the final repair depends on a nonexistent `dfodaratumumab` key. The live relationships and stored counts can be internally correct while describing the wrong entity. This is one P1 blocker under “a refused product drawn as the originator.” It is not a claim of stale graph data, new scope creep, or a new regression caused by HEAD. Known accepted over-refusals and the lexical exploratory cases above do not determine this conclusion.

## Reproduction

```text
python -B audit_evidence_claims/m12/attacks/focused.py
python -B audit_evidence_claims/m12/attacks/http_probe.py
python -B audit_evidence_claims/m12/attacks/evidence.py
```

Run from repository root. HTTP runner uses port 8962 and verifies it is unused before starting the original `src/app.py` CLI. Bytecode is disabled; its temporary directories point into this output directory.
