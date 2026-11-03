# Codex review brief — resume text (Korean), human voice and accuracy

You are an independent reviewer acting as (a) a Korean hiring manager at a pharma-bio AI startup who reads hundreds of
사람인 applications, and (b) a fact checker. Do NOT edit any tracked file. Write your report to
`audit_evidence_claims/resume1/REPORT.md` (in Korean). End with exactly one line: `VERDICT: APPROVE` or
`VERDICT: CHANGES REQUIRED`.

The text under review is `audit_evidence_claims/resume1/resume.md`: an applicant's 사람인 resume prose for the role
Scientific AI Engineer (제약바이오 LLM Agent·RAG·지식그래프·동의어 딕셔너리·엔티티 정규화·데이터 파이프라인) at
(주)바이오리서치에이아이. It was just rewritten because the applicant felt it "read like an AI wrote it". The applicant
is a bio major with 4 years 10 months in cell-therapy process development; the OncoKG project in this repository is
theirs.

## Review

1. **AI-written feel.** Point to the exact sentences that still read as machine-written to a Korean reader: stock
   contrasts ("A가 아니라 B"), aphorisms, triads, over-parallel structure, translated phrasing, unnatural word choice,
   too-even rhythm, abstract nouns piled up, symbols (—, ·) in prose. For each, propose a concrete replacement sentence in
   natural Korean that a real applicant would write. Do not make it casual or emotional; it is still a job application.
2. **Hiring-manager read.** What is unclear, too long, repetitive across sections (e.g. the same Abraxane/HLX04 example
   appearing several times), or likely to be skipped? What is missing that this role would look for? Is anything
   likely to hurt (over-claiming, self-deprecation, jargon)?
3. **Facts about OncoKG.** Check every OncoKG number and claim against this repository (README.md, README.ko.md,
   CODEX_*_VERDICT.md, outputs/, tests): 3,000 trials, ChEMBL synonyms 28% from trials, dexamethasone/tobramycin and
   cisplatin/carboplatin, 2,187 → 65 ambiguous, 347 rows scored, 12 labels corrected over three audits, 99.1% → 88.7%
   (102/115 holdout), 58.8% non-industry sponsors, the 'no longer reproduces' defect, six rounds on the prose checker
   then structured claims approved, 14 unfixed defects, 317 tests. Flag anything wrong, overstated or unsupported.
   Claims about the separate automation system and the applicant's employment cannot be checked here; say so, do not
   judge them.
4. **Length.** 사람인 자기소개서 items are usually read in under a minute each; say which items should be shorter and
   where to cut.

Give the report in this order: overall impression (3–5 lines), then a table of sentence-level fixes (원문 → 제안 → 이유),
then fact-check results, then length cuts.
