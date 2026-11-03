[Full round-2 report](<C:/Users/geoum/Dropbox/GY's Formal Workspace/2026 Job recruting/바이오리서치에이아이/oncokg/audit_evidence_claims/r2/r2_report.md>) contains exact inputs, outputs, evidence, code references, and reproduction commands.

## BLOCKERS

Nine blocker groups remain. Examples returning **`grounded=True`, `unsupported_claims=[]`**:

| Question | Unsupported answer |
|---|---|
| `What does osimertinib target?` | `EGFR is an osimertinib inhibitor.` |
| `What does osimertinib target?` | `Osimertinib acts on EGFR and on ALK.` |
| `What does fulvestrant target?` | `Fulvestrant activates ESR1.` |
| `What is the capital of France?` | `This trial is phase 4.` |

Other confirmed failures involve stale pronouns, numeric ownership, passive direction, discarded headings, verbatim exemptions, refused product spans, and citation stripping.

## SHOULD FIX

Faithful-answer rejections improved from **10/30 to 1/30**; **2/6 refusals** still fail. Additional faithful inline-pronoun and alias forms fail. Documentation still overstates the guarantees.

## NOTES

- R1 finding **1: NOT FIXED**.
- R1 findings **2–8: FIXED for their exact reproductions**.
- Paired-clause and distinct-sentence dedup findings: **FIXED**.
- Faithful-paraphrase and documentation findings: **NOT FIXED**.
- All six original probes rerun: **142 cases**, plus dictionary/template checks.
- Regression suite: **128 passed**. Evidence template prose: **5/5 passed**.
- Tracked and staged diffs are empty. All scratch artifacts remain under `audit_evidence_claims/r2/`.

VERDICT: CHANGES REQUIRED