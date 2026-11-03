# Standards review — round 16

**No documented-standard violations found.** Reviewed the changed app/UI hunks from fixed point `bfcb83d` through HEAD `8ebd6629b51a474f216457c8c00f20152304bd1d`, plus the latest query/test patch. The fixed-point diff is nonempty. [App/UI diff](review_diff_app_ui.txt), [latest patch](review_diff_latest.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returned no tracked standards files. [Inventory](review_diff_standards.txt). The user's instructions therefore govern: evidence-based independent review, no tracked edits, scratch only under m16, and a disposition for each earlier reproduction. The review uses original fixture logic, records source/adapted hashes, preserves raw outputs, compares current responses against stored data, and identifies the limits of simulated UI tests. Mutation fixtures change only in-memory database copies.

No application code was changed. The user's conditional requirement to compare original and modified application code against KOA Studio/KhOpenApi therefore does not arise. Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over optional workflow setup.

**Judgment rather than a standards violation:** the new isotope helper still misses an element-first one-letter label, while `_labelled` has a separate reverse-label implementation. The independent `I-124 trastuzumab` reproduction is a specification defect, not a style or documented-standard violation. The labelled-product exception also leaves a paired punctuation discrepancy for an already-labelled centre; that is recorded separately as a nonblocking clarification because the brief explicitly permits labelled products. [Independent staged evidence](adjudication_tracer.json).

The stale 317-test README comments are inherited documentation should-fix items (`README.md:565`, `README.ko.md:386`). App descriptions at lines 566 and 387 remain accurate. No extra coding convention has been invented as a blocker.
