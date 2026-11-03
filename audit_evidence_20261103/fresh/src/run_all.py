"""Run the whole pipeline end to end.

    python src/run_all.py            # rebuild everything from the network
    python src/run_all.py --offline  # rebuild from the snapshots already on disk

Each stage reads the previous stage's artefact from disk, so a stage can be
re-run on its own and the run stays reproducible.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parent
STAGES = [
    ("ingest", "fetch public records and snapshot them", True),
    ("normalize", "build the dictionary, curate it, resolve every record", False),
    ("qc", "run the quality checks", False),
    ("curation_effect", "resolve twice, with and without curation", False),
    ("graph", "build the knowledge graph with provenance", False),
    ("evaluate", "score the held-out sample", False),
    ("make_dashboard_data", "assemble the dashboard payload", False),
    ("build_dashboard", "render the dashboard", False),
]


def run(module: str, args: list[str] | None = None) -> None:
    cmd = [sys.executable, str(SRC / f"{module}.py"), *(args or [])]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=SRC)
    if proc.returncode != 0:
        sys.exit(f"\nstage '{module}' failed with exit code {proc.returncode}")
    print(f"  [{module} finished in {time.time() - t0:.1f}s]\n")


def main() -> None:
    offline = "--offline" in sys.argv
    for name, what, needs_network in STAGES:
        if offline and needs_network:
            print(f"== skipping {name} (offline): {what}\n")
            continue
        print(f"== {name}: {what}")
        run(name, ["test"] if name == "evaluate" else None)
    # the dev and post-fix reports are written by the same scorer
    for which in ("dev", "postfix"):
        run("evaluate", [which])
    print("done. open web/index.html, or run: python -m pytest tests -q")


if __name__ == "__main__":
    main()
