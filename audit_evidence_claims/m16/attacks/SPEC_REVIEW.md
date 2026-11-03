# Specification assessment (attack axis)

Spec source: the user's Round 16 brief and original approval bar; baseline `bfcb83d` to current HEAD `8ebd6629b51a474f216457c8c00f20152304bd1d`.

The current round says: "a medical isotope anywhere in the list item (two-letter elements across words, one-letter within a word) refuses an unlabelled drug". The original approval bar includes "a refused product drawn as the originator" among prohibited outcomes.

**Wrong behavior, P1:** `I-124-labelled trastuzumab` and `trastuzumab labelled with I-124` name one radiolabelled product, with the one-letter isotope wholly inside a word. Every refusal stage misses; HTTP map selects unlabelled TRASTUZUMAB / CHEMBL1201585, 13 trials, and both trial/sponsor QA paths return 12 originator rows. The mass-first controls refuse. The new helper's element-first branch accepts only two-letter symbols, despite the companion `_labelled` helper recognizing one-letter element-first names. Full stages and 168 HTTP responses are in `new_results.json` / `new_http.json`. Both current and HEAD^ query modules leak, so this is an inherited failure, not a demonstrated latest-patch regression.

**Repair success:** exact M15-B1 punctuation/chelator and M15-B2 lower-case vinblastine cases now refuse. A33 lower-case residual also refuses. The reused 97 m14 and 29 m15 attack cases completed. Approved dose/development-code controls remain available.

**Nonblocking limitation:** two fully collapsed systematic SIROLIMUS alias variants now over-refuse; their literal stored alias is still accepted. Accepted user-listed over-refusals and the known ChEMBL bevacizumab-code limitation are not blockers. Explicitly excluded cross-word one-letter exploratory cases are not promoted.

No tracked code was changed and no repair is proposed as implemented. The P1 originator leak is sufficient for CHANGES REQUIRED independently of any other reviewer findings.
