"""Manual verdicts for the post-fix confirmation sample.

Drawn after the two defects the held-out test exposed were repaired, with every
development and test row excluded. Its job is narrow: check that the repairs
hold on rows nobody has looked at, and surface whatever the repairs did not
cover.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

INCORRECT = {
    18: "'Placebo Drug: Docetaxel Drug: Carboplatin' has no combination separator, "
        "so the reference-arm rule blocked two genuinely administered drugs",
    22: "'adenovirus' is a vector word; matching it to tasadenoturev invents a product",
}

NOTES = {
    39: "'erlotinib [Tarceva]' now parses: square brackets were added to the "
        "parenthetical rule after the development pass",
    52: "'Diklofenak Sodyum' is diclofenac sodium in Turkish; a coverage gap, not an error",
    56: "class term safely left unresolved",
}


def main() -> None:
    path = C.REPORTS / "gold_postfix.csv"
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
    print(f"labelled {len(rows)} post-fix rows: {len(rows)-bad} correct, {bad} incorrect")


if __name__ == "__main__":
    main()
