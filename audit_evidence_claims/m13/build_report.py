"""Assemble only freshly verified m13 evidence into the requested report."""
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent

def adapted(text, prefix):
    return re.sub(r'\]\(([^)]+)\)', lambda m: '](' + prefix + '/' + m.group(1) + ')', text)

def section(text, heading):
    content = text.split(heading, 1)[1]
    return content.split('\n## ', 1)[0].strip()

names = (OUT / 'names/FINDINGS.md').read_text(encoding='utf8')
db = (OUT / 'db_ui/FINDINGS.md').read_text(encoding='utf8')
cost = (OUT / 'cost/FINDINGS.md').read_text(encoding='utf8')
name_table = '\n'.join(line for line in names.splitlines() if line.startswith('|'))
db_table = '\n'.join(line for line in section(db, '## Historical findings: individual dispositions').splitlines() if line.startswith('|'))

report = """# Independent relation-map review - round 13

Reviewed **`481100c584ec772cc2332960ba5d3b28ba36ae6f`**. **Changes required: one P1 blocker, M13-B1.** The exact blocking inputs reported in m1-m12 are fixed, including M12's split-symbol/chelator aliases. A different spelling of that same refused stored tracer alias still passes every refusal stage and draws DARATUMUMAB. This is an inherited, newly demonstrated boundary, not a regression introduced by the latest commit.

No tracked file was edited. New scripts and outputs are confined to `audit_evidence_claims/m13/`; existing brief/log files were preserved. Known over-refusals and performance concerns are reported separately and do not determine the verdict.

## Verification and scope

- **340 passed in 28.95 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled; temporary paths confined to m13. [Output](root_checks/pytest.txt), [execution/hash record](root_checks/pytest_summary.json).
- Reused the cumulative original HTTP runners: six original/cumulative runners, four M6 runners, M8/M9 confirmations, M10 confirmations, M11 exact HTTP and M12 exact HTTP plus the inherited supplementary probe. All exit 0. Inputs were preserved; output locations and owned ports changed. [Manifest](reuse_manifest_root.json), [main batches](root_checks/execution_all.json), [M6](root_checks/execution_m6_http.json), [remaining](root_checks/execution_remaining.json), [M12](root_checks/execution_m12_extra.json).
- **44 reused name leaf scripts** (from 52 reused scripts) ran with exit 0, covering **62 individual finding rows**, including the original M1 files, cumulative m2b-m12 matrices, **7,511-key** alias sweeps and **1,648-question** frozen no-relink counterfactual. The alias loss set and frozen counts are unchanged from m12: **70** prior-method positives without a current Drug; **68 identical / 1,556 metadata-only / 24 semantic / zero errors** in the frozen QA comparison. These are same-data method counterfactuals, not whole-deployment comparisons. [Name execution and individual findings](names/FINDINGS.md), [reuse manifest](names/reuse_manifest.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions**, **24/24 UI assertions**, and **4/4 self-loop/unknown-type/retirement fixture checks** pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 page demos and all six map callbacks pass.** Every full demo response equals m7-m12; all 36 actual CLI HTTP requests return 200 and equal direct Engine responses. The seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparison](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- New attacks compare **27 inputs** with current and HEAD^ query modules and reuse the **41-input** m12 attack matrix. **184 attack HTTP requests**, plus **60 root-independent HTTP requests** and **56 exact m12 root replay requests**, all returned 200. Servers closed; served pages match `web/try.html`. [Stages](attacks/fresh_results.json), [reused attack stages](attacks/focused_results.json), [attack execution](attacks/execution.json), [independent HTTP](root_checks/independent_m13_http.json), [independent lifecycle](root_checks/independent_m13_lifecycle.json), [M12 lifecycle](root_checks/independent_m12_lifecycle.json).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They verify generated markup and exercised state/callback behavior, not browser painting or browser-executed XSS. Real HTTP checks use unmodified `src/app.py` or its handler with isolated in-memory fixtures. No audit used port 8765. No model was called. No external pharmacology assumption is used: identity evidence comes from the repository dictionary, canonical key, predicates and refused controls.

## M13-B1 - P1: removing an isotope/chelator separator bypasses every refusal

Exact request: `POST /api/explore` with `{"text":"89ZrDFO-daratumumab"}`.

**Actual:** HTTP 200, centre **DARATUMUMAB / CHEMBL1743007**, matched alias **`89zr-dfo-daratumumab`**, **2 live trials**, no Refused entity or refusal notice. `Which trials evaluate 89ZrDFO-daratumumab?` and `Who sponsors trials of 89ZrDFO-daratumumab?` each return **2 originator evidence rows**. Fully glued `89zrdfodaratumumab` does the same. Appending `, osimertinib` still selects DARATUMUMAB. [Root HTTP evidence](root_checks/independent_m13_http.json), [separate worker adjudication](db_ui/adjudication.md).

**Control and identity proof:** `[89Zr]-DFO-daratumumab`, `89Zr-dfo-daratumumab` and the repaired `[89Z.r]-DFO-daratumumab` refuse, with no centre and zero qualified trial/sponsor evidence. Bare `daratumumab` works. The leaking spelling and refused control share **canonical key `89zrdfodaratumumab`**, mapped uniquely to the AACT synonym `89zr-dfo-daratumumab` for DARATUMUMAB. Thus the positive lookup recognizes the very stored tracer identity whose refusal is lost; this is not a guess about an unrelated unknown name. [Dictionary evidence](attacks/dictionary_evidence.json).

| Stage for `89ZrDFO-daratumumab` | Observed result |
|---|---|
| Raw resolver | `ALIAS` to CHEMBL1743007; no blocked component |
| Resolver veto | `{}` |
| Item linker | Drug DARATUMUMAB; no Refused |
| Whole-name shortcut | `None`; it does not override an existing refusal |
| Public linker | Drug DARATUMUMAB; no Refused |
| Map / trial QA / sponsor QA | Originator centre / 2 evidence rows / 2 evidence rows |

The tested hypothesis is that the latest scan closes split symbols but still relies on input word boundaries. The evidence supports it:

1. Positive lookup deletes separators (`src/textrules.py:339-346`) and matches the complete alias (`src/query.py:413-426`).
2. `_alnum_words` splits only at non-ASCII-letter/digit separators (`src/query.py:111-113`). The candidate produces `['89ZrDFO', 'daratumumab']`; `89Zr` is not a separate word. The new scan at `src/query.py:258-267` glues complete words but never separates an isotope from an already joined word. The first word has seven characters and exceeds its six-character bound.
3. All isotope text is inside the consumed alias, so outside-neighbour checks cannot recover it (`src/query.py:273-289`).
4. The key-prefix fallback isolates `89zr` but requires `dfodaratumumab` to be a same-drug dictionary key (`src/query.py:291-295`). It is absent; only the shorter `daratumumab` key exists. The same failure affects the fully glued alias.
5. Raw tracer predicates also miss this boundary (`src/textrules.py:303-314`; `src/normalize.py:740-745`); the item guard returns false (`src/query.py:119-141`). With all guards silent, `Engine.explore` selects the surviving hit (`src/app.py:87-95`).

Current and exact HEAD^ (`d9260a1ea544cf7bb80415383667784e0aba146a`) query modules both reproduce the leak against the same current app/rules/database. This identifies an **inherited unclosed boundary**, while exact M12-B1 inputs now refuse. [Current/previous comparison](attacks/fresh_results.json), [independent comparison](db_ui/adjudication_tracer.json).

**Required outcome:** positive alias normalization must preserve refusal of a stored tracer identity even when the isotope is joined to its chelator or another alias component. Refusal must not require an independently stored isotope-stripped remainder. No fix was implemented in this audit.

`A33124I` is an additional example of the same boundary: stored alias `A33 124i` refuses, but the glued spelling maps to ADAKITUG / CHEMBL5314551 because remainder `a33` is not a standalone key. It has zero trial/sponsor evidence; it is corroboration of M13-B1, not a second counted blocker. [Root HTTP](root_checks/independent_m13_http.json), [dictionary evidence](attacks/dictionary_evidence.json).

## Earlier reproductions - FIXED / NOT FIXED per finding

These tables classify exact historical reproductions, not an entire input family. M12-B1 can therefore be FIXED while M13-B1 remains a blocker. m2 ended without a completed report; its partial role/order fixtures and the completed m2b findings are included. Earlier script bodies and historical read-only comparison sources were reused, not historical result files presented as new evidence.

### Name resolution, m1-m12

"""
report += adapted(name_table, 'names')
report += "\n\n### Relations, stored values, UI, server and wording\n\n"
report += adapted(db_table, 'db_ui')
report += """

### Supplemental cases and accepted over-refusals

The explicitly accepted M5-S2, `40-o-(2-hydroxyethyl)-rapamycin`, `42-o-(2-hydroxyethyl)rapamycin`, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra`, and `TAK-659F` remain **NOT FIXED / known over-refusals**, not blockers. M12-S1 `rad001c` remains refused; `RAD001`, EVEROLIMUS and its ID still work. It remains the earlier recorded nonblocking alias loss, not a new m13 regression. [Name controls](names/FINDINGS.md), [root HTTP](root_checks/independent_m13_http.json).

`99MTc trastuzumab` and `[99MTc] trastuzumab` remain **FIXED**: both refuse with no centre in the inherited probe. [Exact replay](root_checks/fresh_probe.json).

M11/M12 supplementary descriptive-distance isotope forms and punctuated lexical qualifiers remain **NOT FIXED**, as individually recorded in the fresh reused matrix; they are not counted as new regressions or additional blockers. The M12 supplementary `Lutetium (177L.u) dotatate` now refuses (**FIXED**); its previous centre was already isotope-labelled and was not an unlabelled-originator blocker. [Exact supplementary dispositions](attacks/FINDINGS.md), [original-case replay](attacks/focused_results.json), [inherited probe](root_checks/fresh_probe.json).

## Cost and performance reproductions

"""
report += adapted(cost.split('\n', 1)[1].strip(), 'cost')
report += """

## Standards and specification

**Standards: zero documented violations found.** The app/UI diff from `bfcb83d` and latest query/test patch were examined. No tracked repository AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or issue-tracker instructions were found. User-supplied evidence-based, m13-only, no-tracked-edit instructions govern. The KOA Studio/KhOpenApi original-versus-modified-code instruction is conditional on changing application code; no such change was made. [Independent standards record](db_ui/standards_review.json).

**Specification: one P1 blocker, M13-B1.** Exact earlier blocking reproductions are fixed, but a normalization-equivalent refused tracer alias still draws its originator without any refusal. Live/correct edges surrounding a wrongly selected centre do not meet the name-refusal guarantee. Known over-refusals and measured costs do not determine the verdict.

README descriptions for app.py are accurate (`README.md:566`, `README.ko.md:387`); nearby test-count comments still say 317, **NOT FIXED**, a nonblocking documentation-only stale count. Actual current tests are 340. [DB/UI source assessment](db_ui/FINDINGS.md).

## Integrity and reproduction

Snapshot: **7 retired nodes, 142 retired edges, zero real self-loops, zero live edges with retired endpoints**. All six live node types and 22 relation combinations were exercised. Self-loop/unknown-type behavior was tested in memory, not claimed to exist in the snapshot. [Snapshot](db_ui/db_snapshot_facts.json), [fixture](db_ui/self_loop_unknown.json).

`Engine.ask` sets `use_llm=False` (`src/app.py:180-181`). Explore follows SELECT paths; mutation fixtures use in-memory databases. The app does not globally enforce a read-only SQLite handle, so no-write evidence rests on source, executed paths and unchanged bytes rather than a database-permission guarantee.

Final verification compares **4,176 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, database bytes, report links and owned-port cleanup. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR inside each script family's m13 `tmp/` directory. Shared-port HTTP scripts run sequentially; benchmarks run after the other suites finish. The setup script records the original hashes and adapted script provenance; do not replace that original snapshot when rerunning checks.

```text
python -B audit_evidence_claims/m13/root_checks/run_all.py
python -B audit_evidence_claims/m13/root_checks/fresh_probe.py
python -B audit_evidence_claims/m13/root_checks/independent_m12_http.py
python -B audit_evidence_claims/m13/root_checks/independent_m13_http.py
python -B audit_evidence_claims/m13/names/run_round9.py
python -B audit_evidence_claims/m13/names/run_completion.py
python -B audit_evidence_claims/m13/names/joined_label_probe.py
python -B audit_evidence_claims/m13/db_ui/run_db.py
python -B audit_evidence_claims/m13/db_ui/run_ui.py
python -B audit_evidence_claims/m13/attacks/run.py
python -B audit_evidence_claims/m13/cost/run_isolated.py
```

VERDICT: CHANGES REQUIRED
"""
(OUT / 'REPORT.md').write_text(report, encoding='utf8')
print(f'Report written: {len(report.splitlines())} lines, {len(report)} characters')
