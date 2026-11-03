# Standards axis

Reviewed HEAD `b7a00f9` against `bfcb83d4320877ffad47083c102ba1c38f691bba` using `git diff bfcb83d...HEAD -- src/app.py src/query.py web/try.html tests README.md README.ko.md`. Commit list and discovered rule files are in [standards_evidence.json](standards_evidence.json).

**0 documented standards violations.** `git ls-files` found no tracked AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or docs/agents rules. The supplied user rules require evidence-based conclusions, no tracked-file edits, and all new scratch under m6; those govern this audit. All this sub-review's new files are under `audit_evidence_claims/m6/db_ui/`; fixture mutations affect only memory databases. Reused script adjustments change their output directory and root-path depth, not application code or fixture expectations.

The KOA Studio / KhOpenApi code-change comparison instruction is inapplicable: this task forbids application-code changes and none were made. No issue-tracker setup or other out-of-scope writes were performed. `src/app.py` and `web/try.html` are unchanged from round-five HEAD `514929c`, but their current behavior was rerun rather than inferred from that fact.

Specification findings are separate: database/UI results appear in [REPORT.md](REPORT.md), and a newly confirmed refused-product leak is explicitly reported there. A standards pass does not resolve that specification blocker.
