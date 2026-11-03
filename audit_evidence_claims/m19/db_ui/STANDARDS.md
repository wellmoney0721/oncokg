# Standards axis — round 19

**0 documented-standard violations found.** The fixed point is `4bed79c1f170ebe1efa3d452ce4398cce17b2113`; current HEAD is `c476d9d559ce5e723c6f5d91fad5e6c3599cfe93`. The nonempty reviewed diff is `git diff 4bed79c1f170ebe1efa3d452ce4398cce17b2113...HEAD -- src tests web README.md README.ko.md CODEX_MAP_M1_VERDICT.md`. It changes the isotope helper, its regression test, and repair notes. [Latest diff](review_diff_latest.txt). The cumulative application/UI diff from original `bfcb83d` was also inspected. [App/UI diff](review_diff_app_ui.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returns no tracked standards sources. [Inventory](review_diff_standards.txt). The user's supplied instructions govern: evidence-based independent review; no tracked edits; scratch only under m19; fresh FIXED / NOT FIXED dispositions for historical reproductions. The reused harnesses retain original inputs and fixture logic, redirecting only scratch paths and the owned CLI port. [Manifest](reuse_manifest.json).

SQLite mutation fixtures are isolated in memory. The all-node oracle connects with `mode=ro`. Actual page JavaScript runs in a Node VM with controlled DOM/fetch stubs: findings concern generated markup and exercised state, not browser painting or browser-executed XSS. CLI HTTP demos use port 9221 and clean up their process. The application connection is not globally read-only; write claims rely on executed paths and integrity checks. `Engine.ask` explicitly sets `use_llm=False` at `src/app.py:181`.

Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over skill setup guidance. No application code was changed, so the conditional KOA Studio/KhOpenApi original-versus-modified code comparison does not arise.

Inherited README test-count comments still say 317 (`README.md:565`, `README.ko.md:386`); adjacent application descriptions remain accurate. This is a documentation should-fix, not a new documented coding-standard violation. New refusal gaps, if reproduced, belong to the independent specification axis.
