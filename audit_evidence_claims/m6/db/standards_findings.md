# Standards axis — round 6

Reviewed the cumulative application diff with `git diff bfcb83d...HEAD -- src/app.py src/query.py web/try.html tests/test_app.py`, now at `b7a00f9c14e5ee0447601795d0c0f4535c2f0376`. Application repairs run from `9db058c`, `c64f433`, `574097f`, `bf436c6`, `514929c`, through `595f5f9` and `c43f911`; `b7a00f9` adds the round-six brief. The latest functional changes are in `src/query.py` and `tests/test_app.py`; `src/app.py` and `web/try.html` retain the reviewed implementation.

`git ls-files '*AGENTS*' '*CONTRIBUT*' '*STANDARD*' 'docs/agents/*'` returned no tracked standards source. Accordingly, there are **0 repository-documented coding-standard violations** to cite. This does not certify specification correctness; that axis has independent reproduction and approval criteria.

The user-supplied evidence, immutable tracked-file, and scratch-location requirements govern this audit. This sub-review writes only under `audit_evidence_claims/m6/db/`, disables Python bytecode, reads production data without mutation, and confines corruptions/retirements to isolated SQLite memory databases. Source/adaptation hashes and fresh output hashes are recorded. The KOA Studio / KhOpenApi original-versus-modified-code instruction does not trigger: no application code is changed. No tracker setup or repository standards files were created.
