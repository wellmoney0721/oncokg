# Standards and documentation axis

No separate repository coding-standard source was found. No tracked file was edited; these are behavioral/documentation findings, not invented style violations. Reproduce: `python -B audit_evidence_claims/r2/standards_probe.py`; exact inputs, outputs, linker spans and evidence are in `standards_probe.json`.

## BLOCKERS

**Refused product spans bypass the checker.** Question: `What does osimertinib target?`; sole evidence: `OSIMERTINIB acts on EGFR (inhibitor)`. Each answer returns `grounded=True, unsupported_claims=[]`:

- `osimertinib is liposomal.`
- `osimertinib is a biosimilar.`
- `Osimertinib is not liposomal.`
- `liposomal Tagrisso.`
- `Osimertinib is non-liposomal.`

`src/query.py:128-141` deliberately returns `Refused` spans including adjacent words. `src/claims.py:278-288` turns them into entity placeholders, removing their content (including negation); `src/claims.py:231-240` rejects only `Missing`, not `Refused`. Empty wording checks then pass. The alias exemption (`src/query.py:495-499,543-544`) also admits Tagrisso individually although its enclosing product was refused. This violates the requested unsupported ordinary-word/negation detection.

## SHOULD FIX

1. Faithful aliases remain rejected for the same question: `Osimertinib (Tagrisso) acts on EGFR.` returns False, `wording: tagrisso`; `AZD 9291 acts on EGFR.` returns False, `number: 9291`. Entity dedup loses subsequent alias spans (`src/query.py:163-168`; `src/claims.py:281-288`); numeric overlap does not exempt linked code spans (`src/query.py:506-511`). `Tagrisso acts on EGFR.` and `AZD9291 acts on EGFR.` pass.
2. Documentation still overstates: README.md:508-520 / README.ko.md:354-360 say negations are always reported and describe a narrower residual bypass. Refused-span examples contradict this. Exact sponsorship evidence containing `not evidence of developing the drug` passes; `This graph cannot answer that question.` passes for the France question. Intended exceptions should be stated. `src/query.py:447,461-466`, `web/template.html:263-265`, and `web/try.html:69-71` retain categorical guarantees. `claims.py:21` does disclose verbatim exemption; `web/try.html:142` is improved but still overstates matched values.

## NOTES

Question punctuation remains narrower than claim punctuation: `Which drugs act on ALK!` (also `:` / `;`) returns `intent=unsupported, entities=[]`; `?` works (`query.py:120` versus `claims.py:277`). Of 2,634 stored multiword aliases, 2,566 link their expected ID; five lose it during claim tokenization: two parenthesized chemical names, three overlapping parent/salt aliases. This is a parser discrepancy, not a regression in the original linker gate.
