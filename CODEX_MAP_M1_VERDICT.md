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

## Round 11 (audit_evidence_claims/m11) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M11-B1 | punctuation inside the element symbol ("[89Z.r] trastuzumab") | neighbour words are glued as the key glues them (up to the length of a label) and compared with isotope labels; a matched name whose key is an isotope label plus a key of the same drug ("89zr" + "trastuzumab") is refused |
| M11-B2 | a suffix spelt in pieces beyond the five-token window ("bevacizumab a - w w b") | the words after a name are glued the same way and compared with the known biosimilar suffixes |
| M11-S1 | further lone-alias losses (`9-amino-20(s)-camptothecin`, `il-6ra`, `TAK-659F`) | recorded as known over-refusals: their keys end or contain what reads as an isotope label; refusing never draws a wrong drug |

Dose and schedule text after a name is unaffected ("osimertinib 80 mg", "paclitaxel 2 cycles", "cisplatin 75 mg/m2 day 1"). Tests 339.

## Round 12 (audit_evidence_claims/m12) — CHANGES REQUIRED (one blocker)

| # | Finding | Repair |
| --- | --- | --- |
| M12-B1 | "[89Z.r]-DFO-daratumumab": inside a consumed stored alias the split symbol was checked only as space-joined words, and the chelator kept the remainder from being a same-drug key | every run of the matched name's words is also glued (as the key glues them, up to a label's length) and compared with isotope labels |

A sweep of every unambiguous stored alias run alone (before and after this change) shows no newly refused or changed names. Tests 340.

## Round 13 (audit_evidence_claims/m13) — CHANGES REQUIRED (one blocker)

| # | Finding | Repair |
| --- | --- | --- |
| M13-B1 | "89ZrDFO-daratumumab": no separator between the isotope and the chelator | a name's key that starts (ends) with a two-letter-element isotope label and whose rest ends (starts) with any key of the same drug is refused, whatever lies between; a neighbouring word with a label fused to its start or end ("DFO89Zr") also refuses, one-letter elements only where case marks the boundary |

Kept narrow on purpose: lower-case chemistry and dose text are not read as isotopes ("13-cis retinoic acid", "paclitaxel 2 cycles", "BKM-120NX"). The stored-alias sweep shows no newly refused names (one formerly refused name, `rad001c`, now resolves). Tests 341.

## Round 14 (audit_evidence_claims/m14) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M14-B1 | "3HVINBLASTINE": a one-letter element in an all-capitals name escaped the case rule (regression of round 13) | in the name's own key a one-letter element counts wherever it is written upper-case |
| M14-B2 | "89Zrpanitumumab-PET-CT": a trailing marker kept the drug's key from ending the rest | the same drug's name may sit anywhere after (before) the label |
| M13 residual | "A33124I" | a label closing a stored name of the drug counts when its mass is one used in medicine (I-124); development codes ending in a salt letter ("NSC-118218H", "DX-8951F", "GW572016F") are not labels |

Stored-alias sweep: no newly refused names. Tests 342.

Known data limitation found while fixing, not changed here: ChEMBL lists bevacizumab biosimilar development codes as synonyms of bevacizumab (HLX04, HLX-04, HLX04-O, BAT1706, SB8, MB02, FKB238, BI 695502), so these draw BEVACIZUMAB. Fixing it belongs in the dictionary curation step (resolver and graph), with a re-measurement, not in the map.

## Round 15 (audit_evidence_claims/m15) — CHANGES REQUIRED

Each round found another spelling of an isotope. The rule is now one check on the run-together key, using a table of
radioactive masses used in medicine (H-3, C-11/14, N-13, O-15, F-18, Cu-61..67, Ga-67/68, Zr-89, Y-86/90, Tc-99,
In-111, I-123..131, Lu-177, Ra-223, ...; stable 2H/13C/15N excluded so "13-cis" is chemistry):

| # | Finding | Repair |
| --- | --- | --- |
| M15-B1 | "89-ZrDFO trastuzumab" | a medical isotope anywhere in the list item (two-letter elements across words; one-letter elements within a word) refuses an unlabelled drug |
| M15-B2 | "3hvinblastine" (lower case) | same rule; the mass table, not the case, decides |
| — | — | a drug whose own preferred name carries a label (LUTETIUM ... LU-177, FLUDEOXYGLUCOSE F 18, RADIUM RA 223) is the labelled product and is not refused |

Same list item, fail closed: "osimertinib with [89Zr] trastuzumab" refuses both; "osimertinib, [89Zr] trastuzumab" keeps
osimertinib. Additional known over-refusals: `GS-11CAL-101`, `3en3hg4wsw` (codes that read as C-11 / H-3). Tests 343.

## Round 16 (audit_evidence_claims/m16) — CHANGES REQUIRED (one blocker)

| # | Finding | Repair |
| --- | --- | --- |
| M16-B1 | "I-124-labelled trastuzumab": element-first one-letter isotope | a lone letter followed by a medical mass inside one word ("I-124", "F18", "C14", "Y-90") counts; a letter inside a letter run ("BKM120", "AZD9291") does not |
| M16-S1 | the item's isotope state was recomputed for every match (seconds under the lock) | computed once per item (cached) |

Stored-alias sweep: no change. Tests 344.

## Round 17 (audit_evidence_claims/m17) — CHANGES REQUIRED (one blocker)

| # | Finding | Repair |
| --- | --- | --- |
| M17-B1 | "trastuzumab labelled-I-124": punctuation was removed before the letter-boundary check, gluing the I to "labelled" | each word is also checked as its punctuation-separated pieces and every neighbouring pair glued ("I"+"124") |

Stored-alias sweep: no change. Tests 345.

## Round 18 (audit_evidence_claims/m18) — CHANGES REQUIRED (one blocker)

| # | Finding | Repair |
| --- | --- | --- |
| M18-B1 | "trastuzumab radiolabelled with iodine-124": element names written out | element names (iodine, fluorine, zirconium, lutetium, gallium, technetium-99m, ...) beside a medical mass, in either order, count as the isotope; words that say the substance is labelled ("radiolabelled", "tritiated", "radiotracer", "radioligand", "radiopharmaceutical", ...) refuse an unlabelled drug in the item |

A drug whose own name carries the label is still allowed ("fluorine-18 fluorodeoxyglucose"). Stored-alias sweep: no change. Tests 346.

## Round 19 (audit_evidence_claims/m19) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M19-B1 | "radio-labelled trastuzumab" | labelling words are also checked on each neighbouring pair of words glued |
| M19-B2 | "trastuzumab labelled with 99m-technetium" | a mass beside a written-out element may carry the metastable "m", in either order |

"radiotherapy plus cisplatin" and "cisplatin and radiation" still draw cisplatin. Stored-alias sweep: no change. Tests 347.

## Round 20 (audit_evidence_claims/m20) — CHANGES REQUIRED (one blocker)

| # | Finding | Repair |
| --- | --- | --- |
| M20-B1 | "trastuzumab labelled with terbium-161", "[161Tb] trastuzumab" (also 227Th, 213Bi): therapy nuclides missing from the isotope tables | Tb, Th, Bi, Sc, Ho, Tl, Xe, Au, Pd, Ir, Ag, Sn, Dy, Pt added (symbols, masses, element names); Er, Se, Cr, Co, Ce, La, Fe, Cs, Mn only beside the written-out element name, because their symbols begin ordinary words ("75 several", "51 criteria") |
| inherited | "radioactively labelled", "radioconjugated", "iodine124", "99mtechnetium", "technetium99m", "radio-immuno-conjugate" | label stems read on one to three glued neighbouring words; element name and mass also read glued in one word |
| M20-S1 | "non-radio-labelled trastuzumab" over-refused | a label run right after "non"/"not"/"no"/"un"/"without" does not count |

Stored-alias sweep: no change. Tests 348.

## Round 21 (audit_evidence_claims/m21) — CHANGES REQUIRED (two blockers)

| # | Finding | Repair |
| --- | --- | --- |
| M21-B1 | "trastuzumab labelled with Ce-134", "[134Ce] trastuzumab" (also Mn-52): name-only elements written as symbols | a two-letter symbol beside its mass counts inside one written word ("Ce-134", "134Ce") and across a space ("Ce 134"), except CR/CO/SE/LA across a space (everyday abbreviations) |
| M21-B2 | "radioisotope-labelled trastuzumab", "labelled with a radioisotope" | label stems radioisotop, radiometal, radiochelat, radiohalogen, radiotheranost |

"75 several", "51 criteria", "trastuzumab CR 51" still draw the drug. Stored-alias sweep: no change. Tests 349.

## Round 22 (audit_evidence_claims/m22) — CHANGES REQUIRED (three blockers)

| # | Finding | Repair |
| --- | --- | --- |
| M22-B1 | "trastuzumab labelled with 52Mn": the metastable "m" swallowed manganese's first letter | a fused mass and symbol is read both ways (with and without the "m") |
| M22-B2 | "134CeDOTA trastuzumab", "134CeIII-DOTA", "trastuzumab DOTA134Ce": a symbol fused to its mass inside a longer word | mass then symbol, or symbol then mass, anywhere inside one word |
| M22-B3 | "astatinated", "radioastatinated", "radiofluorinated", "radiobrominated trastuzumab" | every "radio..." word is a label (fail closed) except treatment and method words (radiotherapy, radiation, radiology, radiofrequency, radiochemotherapy, ...); "astatinated"; "labelled"/"labeled"/"tagged" on their own ("isotope-labelled", "FITC-labelled") |

A negation covers only the label word it negates ("non-labelled", "non-radio-labelled"), not a later label in the same item. Stored-alias sweep: no change. Tests 350.

## Round 23 (audit_evidence_claims/m23) — CHANGES REQUIRED (two blockers)

| # | Finding | Repair |
| --- | --- | --- |
| M23-B1 | "DOTACe134 trastuzumab", "trastuzumab DOTAMn52": symbol-first pair inside a longer word | symbol then mass is read at any position in a word |
| M23-B2 | "trastuzumab conjugated to IRDye800CW", "trastuzumab conjugated to DM1" (and covalently linked, ... conjugate) | conjugat-, covalently, "linked to/with" in the item refuse a drug, unless the joining word is part of the matched name ("cbr96 - doxorubicin immunoconjugate") or the drug's own name carries a payload (TRASTUZUMAB EMTANSINE, ... DERUXTECAN) |
| M23-S1 | "non-radio-astatinated" refused; "not radioactively labelled" refused | a negation covers a bare "radio" with the word it prefixes, and a label word after its adverb |
| M23-D1 | "13-cis retinoic acid" draws TRETINOIN: an AACT synonym in the dictionary maps 13-cis-retinoic acid and isotretinoin to CHEMBL38 | data limitation, recorded; needs dictionary curation and remeasurement (owner's decision, with the bevacizumab synonyms) |

Stored-alias sweep: no change. Tests 351.

## Round 24 (audit_evidence_claims/m24) — CHANGES REQUIRED (two blockers)

| # | Finding | Repair |
| --- | --- | --- |
| M24-B1 | "irinotecan conjugated to polyethylene glycol": IRINOTECAN contains "tecan", so the payload exemption let it through (also topotecan, tasidotin) | a drug counts as the conjugate only when a later word of its name is a payload (TRASTUZUMAB EMTANSINE, ETIRINOTECAN PEGOL) or the name says conjugate |
| M24-B2 | "trastuzumab coupled to IRDye800CW", "linked via a linker to", "chemically attached to" | coupled/coupling/attached/tethered/crosslinked/chemically; "linked" followed by via or linker, or "linked to/with" a code or named reagent (DM1, IRDye800CW, PEG) |
| M24-S1 | "not covalently linked to DM1", "non-radio-immuno-conjugated", "osimertinib linked to resistance" refused | a negation covers the joining phrase it starts (three words); "linked to" an ordinary word is a relation, not a conjugate |

Stored-alias sweep: no change. Tests 352.

## Round 25 (audit_evidence_claims/m25) — CHANGES REQUIRED (two blockers)

| # | Finding | Repair |
| --- | --- | --- |
| M25-B1 | "trastuzumab not radiolabelled but conjugated to DM1": the three-word negation reached the later affirmative "conjugated" | a negation covers the one word it negates, carried on only through an adverb or a prefix piece (radio, immuno, ...) |
| M25-B2 | "trastuzumab linked to a DM1 payload", "linked to polyethylene glycol": only the word right after "to" was tested | up to three words after to/with (articles skipped) are tested for a code or a reagent noun (polyethylene glycol, payload, dye, toxin, chelator, ...) |

"osimertinib linked to drug resistance", "linked with poor prognosis" still draw the drug. Stored-alias sweep: no change. Tests 353.

## Round 26 (audit_evidence_claims/m26) — CHANGES REQUIRED (two blockers)

| # | Finding | Repair |
| --- | --- | --- |
| M26-B1 | "trastuzumab is not only conjugated to DM1 but also purified": "only" ends in -ly, so the negation carried through to "conjugated" | "not only" does not start a negation |
| M26-B2 | "trastuzumab linked to a derivative of the toxin DM1": articles were dropped after the word window was cut; also the reverse "polyethylene glycol linked to irinotecan" | "linked" counts when a payload, dye, carrier or chelator (reagent nouns and codes: DM1, MMAE, SN-38, PEG, DOTA, FITC, IRDye...) is named anywhere in the item, in either order |
| M26-S1 | "osimertinib linked to longer PFS", "... 3-year survival", "... response in 2026", "... resistance in EGFR" refused (capital/digit heuristic) | the capital/digit heuristic is gone; only named reagents count |

Stored-alias sweep: no change. Tests 354.

## Round 27 (audit_evidence_claims/m27) — incomplete (Codex stopped at model capacity before REPORT.md); its recorded findings repaired

| # | Finding (attacks/FINDINGS.md) | Repair |
| --- | --- | --- |
| M27-B1 | "trastuzumab linked to SN-38", "DM-1", "Alexa Fluor 488": the hyphen split the code; Alexa not named | payload codes are also read on each neighbouring pair glued (sn+38, dm+1); alexa, rhodamine, cyanine dyes |
| M27-B2 | "trastuzumab not merely / solely / exclusively conjugated to DM1 but also purified" | focus words after "not" (only, merely, solely, exclusively, just, simply, purely) do not start a negation |

"not directly conjugated to DM1" still draws trastuzumab. Stored-alias sweep: no change. Tests 355.
