Spec source: the user's Round 17 brief and original relation-map guarantees; baseline `bfcb83d` to HEAD `4df54ae7f8bd16babc4ccb2dd0e8d4ce0314098b`.

The round requires "element-first one-letter isotopes inside one word (I-124, F18, C14, Y-90) count". The original approval bar forbids a refused tracer being drawn as the originator.

**Wrong/partial behavior, P1:** `trastuzumab labelled-I-124` contains I-124 inside one original word, visibly separated from the preceding letters by a hyphen. Every refusal stage misses, and the actual HTTP map draws unlabelled TRASTUZUMAB / CHEMBL1201585 with 13 clinical trials. Trial and sponsor QA each return 12 originator evidence rows. `trastuzumab labelled-124I`, `I-124-labelled trastuzumab`, and `trastuzumab labelled with I-124` refuse. In `src/query.py:164-169`, punctuation is removed before the negative letter lookbehind, so the hyphen-delimited I becomes a letter inside the flattened run `labelledi124`. This is an inherited gap present in HEAD^, newly reproduced here, rather than a demonstrated newly introduced leak. New stage captures, exact HTTP requests, and paired counterfactuals are in [new_results.json](new_results.json) / [new_http.json](new_http.json).

**Repair success:** the 42 original m16 attack/control cases were rerun, and original M16-B1 forms now refuse. Original M15 chelator/lowercase cases remain refused. Ordinary BKM120/AZD9291, dose/schedule, and bare-drug controls survive. The 428 transformed aliases over 104 keys have zero changed centre/refusal outcomes from m16. Cached item-state performance is measured separately by the root.

**Scope:** no tracked edits or missing spec were observed. Recorded over-refusals and ChEMBL biosimilar-code curation are outside blocker scope. No independent additional blocker is inferred from the same-family corroborations.

Specification: **one newly promoted P1 family**, sufficient for CHANGES REQUIRED.
