# Standards review - round 18

**0 documented-standard violations found.** Fixed point `bfcb83d` through current HEAD `4bed79c1f170ebe1efa3d452ce4398cce17b2113`; inspected `git diff bfcb83d...HEAD -- src/app.py web/try.html` and `git show HEAD -- src/query.py tests/test_app.py`. Both diffs are nonempty. [App/UI diff](review_diff_app_ui.txt), [latest patch](review_diff_latest.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returns no tracked standards files. [Inventory](review_diff_standards.txt). The user's evidence-based, audit-only instructions govern: no tracked changes, fresh outputs only under m18, and FIXED / NOT FIXED for historical findings. Reused scripts preserve fixture logic and exact historical inputs; manifests record source/adapted hashes. Database mutation fixtures are isolated in-memory copies; the snapshot/oracle connection uses SQLite mode=ro. Node VM UI scope is explicitly limited to generated markup and exercised state/callbacks.

No application code was changed, so the user's conditional KOA Studio/KhOpenApi original-versus-modified code comparison does not arise. Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over skill setup guidance.

The latest patch preserves punctuation boundaries for one-letter isotope symbols, and original m17 examples now refuse. A separate specification gap remains for full element names: `trastuzumab labelled with iodine-124` misses every refusal stage and draws the unlabelled originator. This is a specification finding, not an independent standards violation; the attack reviewer owns its severity. [Independent stages](independent_boundary.json).

Inherited README comments still say 317 tests (`README.md:565`, `README.ko.md:386`); adjacent app descriptions remain accurate. This is a documentation should-fix.
