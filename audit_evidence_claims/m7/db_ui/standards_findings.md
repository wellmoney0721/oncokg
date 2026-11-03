# Standards axis

No documented-standard violation identified. `git ls-files` found no tracked AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or docs/agents instructions. The supplied user evidence and no-tracked-edit instructions govern this audit. No application code was changed, so the conditional KOA Studio / KhOpenApi old/new-code comparison is not triggered.

The app module describes a capped list and All of them; README app command descriptions remain at README.md:566 and README.ko.md:387. No model use occurs in the executed Engine.ask path, which specifies use_llm=False (src/app.py:180-181). Application SQLite opens read/write (src/app.py:41); this audit substitutes read-only production connections and mutates only in-memory fixtures.

Evidence: [standards_evidence.json](standards_evidence.json). Specification findings are separately reported in [REPORT.md](REPORT.md).
