# Standards review — round 17

**No documented-standard violation found.** Reviewed fixed point `bfcb83d` through HEAD `4df54ae7f8bd16babc4ccb2dd0e8d4ce0314098b`, using `git diff bfcb83d...HEAD -- src/app.py web/try.html`, and the latest query/test patch. Both diffs are nonempty. [App/UI diff](review_diff_app_ui.txt), [latest patch](review_diff_latest.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returned no tracked standard files. [Inventory](review_diff_standards.txt). The user's audit instructions govern: independent evidence-based review, no tracked-file changes, new scratch files only under m17, and FIXED / NOT FIXED per earlier finding. Reproductions preserve original fixture logic, record source/adapted hashes, and compare API output against stored rows. Mutation fixtures use isolated in-memory databases; UI test limitations are explicit.

No application code was edited. The user's conditional instruction to compare original/modified code against KOA Studio and KhOpenApi references therefore does not arise. Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over skill setup guidance.

**Specification defect, not a standards violation:** the new one-letter reverse-isotope check operates after punctuation removal. `iodine-I-124-labelled trastuzumab` loses the boundary before I and passes every refusal stage, drawing unlabelled TRASTUZUMAB. The separate attack/specification review owns severity and verdict. [Independent stages](adjudication_tracer.json).

Inherited README comments still say 317 tests (`README.md:565`, `README.ko.md:386`); nearby app descriptions remain accurate. This is a documentation should-fix, not a new documented coding-standard violation.
