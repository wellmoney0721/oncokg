# Relation map — Codex review 1 (2026-11-03 KST)

Report: `audit_evidence_claims/m1/REPORT.md`. Verdict: CHANGES REQUIRED. Every finding reproduced before fixing.

| # | Finding | Repair |
| --- | --- | --- |
| B1 | "bevacizumab - awwb", "[89Zr] trastuzumab" drew the originator (linker joined tokens without the refusal checks) | `link_entities` refuses a multi-token window that names a distinct product or tracer, and none of its tokens link (fixes questions too) |
| B2 | a collaborator was labelled the trial's lead sponsor | SPONSORS groups keep `role`; headings say lead sponsor or collaborator |
| B3 | an investigator was labelled an institution | heading uses 연구자 for Investigator groups |
| B4 | a retired node could be explored by name | the centre must be live whatever path resolved it |
| count | drug trial counts included retired trials | counts join live Trial nodes |
| should-fix | ordering wording, ring cut silently, stale trail after errors, out-of-order replies, ambiguous names silent, action/class labels, omitted details, malformed props, `javascript:` URLs, "All three" | each group states its actual sort; ring says drawn/total; trail cleared on refusal/not-found/error; replies older than the latest request are dropped; the reading and other matches (company, target, refused span) are shown; stored action codes shown with a Korean gloss; sponsor class code shown; centre start date, drug count and phase always shown; props that are not objects read as empty; only clinicaltrials.gov links are clickable; docstring fixed |

Tests 321.

Round 2 (audit_evidence_claims/m2) stopped at Codex's usage limit before a report (log.txt ends with the limit error).
Its partial fixtures showed a SPONSORS edge without a role would be labelled collaborator; the page now says
"역할 기록 없음" for any role other than lead_sponsor/collaborator. Groups shown as "이름 순" were sorted Z to A; now A to Z
within equal weight. Round 2 to be re-run when the limit resets (2026-11-04 15:37).

## Round 2 re-run (audit_evidence_claims/m2b) — CHANGES REQUIRED

All m1 reproductions FIXED. New:

| # | Finding | Repair |
| --- | --- | --- |
| R1 | "osimertinib and generic version of bevacizumab": the refusal window swallowed osimertinib and left bevacizumab to link (map and QA switched subject) | a refused product span never crosses a comma or a joining word (and, or, plus, with, vs, …); separately named drugs survive in either order |
| R2 | malformed sponsor props displayed as "0건" | an unrecorded count is `evidence_trials: null`, shown as "기록 없음"; 0 is only a sort weight |
| should-fix | bool scores accepted and crashing render; rounded score; embedded multi-id alias alternatives dropped; "everything" docstring; silent 500-char cut | numbers exclude bool/NaN; score shown as stored; the hit's `also_matching_ids` disclosed; docstring; >500 chars is a 400 error; render errors shown |

Tests 323.

## Round 3 (audit_evidence_claims/m3) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M3-B1 | "with" as a joiner let "paclitaxel with albumin bound nanoparticles" draw PACLITAXEL (and QA answer with it) | refusal is now bound to the drug it qualifies: the shortest span holding that drug and no other drug, inside one list item; "with" is no longer a joiner |
| M3-B2 | "What is the generic version of bevacizumab?" drew BEVACIZUMAB (inherited) | same repair: the span must contain the drug, so the question prefix no longer absorbs the qualifier |
| should-fix | the single-token qualifier pass crossed commas ("osimertinib, liposomal doxorubicin" refused osimertinib) | neighbours are taken only within the same list item and never a joining word |
| found while fixing | words of a longer name were read again ("erlotinib hydrochloride" also listed ERLOTINIB) | a matched span is not re-linked |

Tests 325.

## Round 4 (audit_evidence_claims/m4) — CHANGES REQUIRED

Shortest-span binding kept failing (wrong drug on ties, a six-token reach, qualifiers already consumed by the token pass).
Replaced by a fail-closed rule: text is cut into list items at , ; ， ； 、 and listing words; an item in which any run of
words names a distinct product or tracer has every drug in it refused (which drug the qualifier describes is not guessed);
drugs in other items, and targets/companies in the same item, still link. M4-B1 (both drugs now refused, never
BEVACIZUMAB), M4-B2 (no distance cap), M4-B3 (one pass, no pre-consumed qualifier) and the EGFR/AstraZeneca over-refusal
are covered by tests. Tests 326.

## Round 5 (audit_evidence_claims/m5) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M5-B1 | a glued "/" or "|" ("bevacizumab-awwb/ osimertinib") hid the suffix guard; the alias key dropped the slash and linked BEVACIZUMAB | tokens are stripped of "/" and "|", which end the list item |
| M5-B2 | "liposomal and nanoparticle formulation of doxorubicin": "and" detached the bare qualifier | a qualifier item with no drug carries across a listing word to the next item's drugs; a product named by itself (in the index, or a known biosimilar/reformulation brand such as Mvasi, Abraxane) does not carry |
| M5-S1 | names were built across list items ("biosimilar anastrozole, Arimidex" lost Arimidex; "Erlotinib, hydrochloride ..." became the salt) | drug spans and the positive matcher stay inside one item |
| M5-S3 | the all-runs scan was cubic (1.8 s at 250 words, under the lock) | whole item once for unanchored patterns, runs of at most eight words for anchored ones: 500 words in about 0.03 s |
| M5-S2 | "Pegylated interferon alfa-2a" (a stored alias of the pegylated drug itself) is refused | not changed: the resolver refuses it too, and exempting known aliases from the product guards would reopen M5-B1 (recorded as a known over-refusal) |

Tests 329.

## Round 6 (audit_evidence_claims/m6) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M6-B1 | an interior "/" or "|" ("bevacizumab - awwb/osimertinib") hid the suffix | "/" and "|" split a word wherever they are and end the list item |
| M6-B2 | edge punctuation the guards kept but the alias key dropped ("bevacizumab-awwb。", trailing hyphen) | edge punctuation is stripped before the guards (brackets kept for isotopes) |
| M6-B3 | "and" inside a parenthetical description detached its qualifier from the preceding drug | listing words inside parentheses do not split |
| all | the linker kept re-implementing the resolver's refusals | the intervention resolver now runs on each list piece; a drug inside a piece it refuses as a distinct product or tracer is never linked (unless the same molecule is also accepted in another piece, which the list-item rule then governs) |
| M6-S1 | complete stored names with list punctuation picked another drug | an input that is exactly one stored name (and not refused) is read whole |

Tests 331.

## Round 7 (audit_evidence_claims/m7) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M7-B1 | the whole-name shortcut ran before the list linker and overrode its refusal ("bevacizumab-awwb?") | the shortcut runs last and only if neither the resolver nor the list linker refused anything |
| M7-B2 | wrappers and Unicode hyphens ("(bevacizumab-awwb)", U+2011) defeated both guards | input is NFKC-normalised and every dash folded to "-" before any check; all edge punctuation and wrappers are stripped from words |
| M7-B3 | "89Zr trastuzumab" (space-separated isotope) passed both guards | an isotope label anywhere in a list item qualifies the item |
| M7-S1 | the whole-name shortcut used the aggressive key ("is a", "Erlotinib, hydrochloride") | only a letter-for-letter stored name (after the same normalisation) is read whole |
| M7-S2 | exact stored names with "/" or a listing word were rejected first | the exact-name check no longer pre-rejects them |
| M7-S3 | the resolver ran on every piece | each distinct piece once, only if it holds a drug name, with a per-engine cache |

Tests 334.

## Round 8 (audit_evidence_claims/m8) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M8-B1 | "[89 Zr] trastuzumab": the resolver's tracer refusal was re-tested on its cleaned component and lost | the resolver's `radiotracer_guard` rule is honoured as recorded; an isotope label written as two words ("89 Zr") beside a name qualifies the item |
| M8-B2 | "bevacizumab-(awwb)": interior wrappers defeated the anchored guard while the alias key ignored them | the guards also see each item with every run of punctuation (not spaces) read as one hyphen |
| M8-B3 | dashes outside the hand-written list (U+2E3A, 14 of 26 Pd) | every Pd character and the minus signs fold to "-"; a test covers all 26 |
| M8-S1 | cache rollover cleared the entry it was about to read (KeyError, 400) | the result is kept in a local before the cache is touched |
| M8-S2 | a bare qualifier carried across a comma ("biosimilar, and osimertinib") | carry only within the same comma/semicolon piece |
| M8-S3 | lone stored names shaped like isotopes ("566C", "9-ac", "5ac") refused | a lone stored name in its own piece is not refused by the tracer rule; an isotope qualifies only beside other words |
| M8-S4 | a stored name's final period stripped before comparison | both sides are stripped alike |

Tests 336.

## Round 9 (audit_evidence_claims/m9) — CHANGES REQUIRED

The positive lookup key (letters and digits only) was broader than every refusal check. Refusal now runs on that same form:

| # | Finding | Repair |
| --- | --- | --- |
| M9-B1 | "bevacizumab_awwb", "bevácizumab-awwb" | item guards also see the text accent-stripped and with underscores and punctuation folded; a matched name whose key ends in a known biosimilar suffix (stem = the same drug) is refused |
| M9-B2 | "[89.Zr] trastuzumab", "89:Zr trastuzumab" | an isotope label (one or two letters-and-digits words, any separator) just before or after a matched name refuses that name |
| M9-B3 | "bevacizumab awwb", "bevacizumab (awwb)" (stored alias `Bevacizumab awwb`) | the suffix-key rule above, and a known suffix as the next word |
| M9-S1 | four lone stored names refused | "Theophylline in dextrose 5% in plastic container" fixed (the item-wide isotope rule is gone; isotopes count only beside a name). Still refused, recorded as known over-refusal: `40-o-(2-hydroxyethyl)-rapamycin`, `42-o-(2-hydroxyethyl)rapamycin` (the chemical locant reads as an isotope) and `Trastuzumab--vcmmae conjugate` (an ADC, a different drug). An exact-stored-name exception was not added: 71 stored aliases carry an isotope without a hyphen ("89zr panitumumab", "Lutetium (177lu) dotatate"), and the exception would draw them as the originator. EVEROLIMUS and TRASTUZUMAB VEDOTIN remain reachable by their names and ids. |

Side effect: "osimertinib with [89Zr] trastuzumab" now refuses only trastuzumab (the isotope binds to its neighbour) instead of both. Tests 337.

## Round 10 (audit_evidence_claims/m10) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M10-B1 | a stored alias ending in an isotope ("A33 124i") was accepted | every one- or two-word run inside the matched name is checked for an isotope label |
| M10-B2 | an isotope token stood in for the substance ("18F fluorothymidine" drew FDG) | an isotope-shaped name is accepted only when it is the whole list item ("18f", "566C", "9-ac") |
| M10-B3 | a punctuation-only token used up the two-word budget ("trastuzumab 89 - Zr") | neighbour words are counted after normalisation to letters and digits |
| M10-B4 | respelt qualifiers ("generic-version of", "albumin - bound", "follow-on-biologic") | item guards also see the item with every separator read as one space |

Tests 338.
