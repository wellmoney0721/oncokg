"""Manual verdicts for the held-out test sample.

Scored after the rules were frozen. The development sample had already been used
for tuning, so only these numbers are an honest estimate of behaviour on records
the rules were not shaped around.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

INCORRECT = {
    92: "'18F-thymidine (FLT)' is a PET tracer; thymidine-as-a-drug is the wrong entity",
    133: "'18F' is the isotope label on a different tracer, not FDG",
    134: "'18F' is the isotope label on a different tracer, not FDG",
    135: "'18F' is the isotope label on a different tracer, not FDG",
    136: "'18F' is the isotope label on a different tracer, not FDG",
    137: "'18F' is the isotope label on a different tracer, not FDG",
    159: "'Q.D' is a dosing-schedule abbreviation that leaked through as a residue",
}

NOTES = {
    31: "safe; 5-FU is resolvable in principle, so this is a recall gap not an error",
    54: "placebo split now keeps erlotinib as a separate resolved exposure",
    57: "placebo split now keeps docetaxel as a separate resolved exposure",
    67: "biosimilar mapped to its reference molecule; the HLX04 identity is not retained",
    161: "a class term; safely unresolved, though BLOCKED_CLASS_TERM would be more precise",
    171: "a gene symbol; safely unresolved, though BLOCKED_TARGET_TERM would be more precise",
}


def main() -> None:
    path = C.REPORTS / "gold_test.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for r in rows:
        i = int(r["id"])
        r["verdict"] = "incorrect" if i in INCORRECT else "correct"
        r["reviewer_note"] = INCORRECT.get(i) or NOTES.get(i, "")
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    bad = sum(1 for r in rows if r["verdict"] == "incorrect")
    print(f"labelled {len(rows)} test rows: {len(rows)-bad} correct, {bad} incorrect")


if __name__ == "__main__":
    main()
