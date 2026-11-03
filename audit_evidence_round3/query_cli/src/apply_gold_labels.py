"""Write the manual verdicts into the gold sample.

The labels below were assigned by reading each record against the trial text and
the reference entry. They are the author's judgement, not a consensus standard:
a second independent reviewer would make the estimate stronger, and that is
recorded as a limitation rather than smoothed over.

verdict semantics
-----------------
accepting tiers (EXACT/ALIAS/CLEANED/SALT_STRIPPED/PARENTHETICAL/
CONTAINED_ALIAS/FUZZY_AUTO)
    correct   = the component really denotes that molecule
blocking tiers (BLOCKED_*, AMBIGUOUS, UNRESOLVED)
    correct   = refusing to link was the right call
FUZZY_REVIEW
    correct   = the proposal held back for review would in fact have been right
                (so a low number here is evidence the threshold is placed well)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

INCORRECT = {
    10: "FDG-PET names an imaging procedure, not a therapeutic exposure",
    30: "'TATE' in this arm is not tirapazamine; abbreviation collision",
    51: "placebo guard swallowed the whole arm; AZD9291 was genuinely administered",
    53: "placebo guard swallowed the whole arm; paclitaxel-carboplatin was administered",
    57: "placebo guard swallowed the whole arm; docetaxel was administered",
    93: "pemetrexed is mentioned as context for an imaging endpoint, not as this intervention",
    142: "'Epothilone' is a class; binding it to epothilone D invents specificity",
    151: "YPEG-rhG-CSF is a distinct pegylated G-CSF, not pegfilgrastim",
    152: "YPEG-rhG-CSF is a distinct pegylated G-CSF, not pegfilgrastim",
    153: "YPEG-rhG-CSF is a distinct pegylated G-CSF, not pegfilgrastim",
    156: "'Phase' is a schedule word; artesunate is nonsense here",
    157: "Alkotinib is not cateQuentinib; similarity is coincidental",
    158: "'CB-Erl' is a regimen abbreviation covering two drugs",
    160: "DCVAC is a dendritic-cell vaccine, unrelated to valproic acid",
    161: "Dositinib is not osimertinib",
    162: "Gecacitinib is not defactinib",
    163: "GM-CSF is a class; regramostim invents a specific product",
    164: "'Pac-CB' is a regimen abbreviation covering two drugs",
    167: "'daily' is a schedule word",
    169: "GM-CSF is a class; regramostim invents a specific product",
    170: "'18F' is an isotope label on a different tracer, not FDG",
    176: "'IM' is the intramuscular route, not imatinib",
    183: "'18F' labels flotegatide here, not FDG",
    198: "'CP-675,206' is one development code; the comma separator split it",
}

NOTES = {
    34: "recoverable: MEDI4736 is unambiguously durvalumab, blocked by a contaminated synonym",
    35: "recoverable: same contaminated synonym",
    36: "recoverable: same contaminated synonym",
    37: "recoverable: same contaminated synonym",
    42: "recoverable: SHR-1210 is camrelizumab, blocked by a contaminated synonym",
    31: "safe, but better handled as a class term than as ambiguity",
    33: "safe, but 5-FU is resolvable in principle; recall gap",
    212: "correct under the NSCLC-scoped vocabulary; a coverage gap, not a precision error",
    209: "residue reported rather than dropped; paclitaxel captured as its own component",
    1: "prodrug/ester form treated as the same substance",
}


def main() -> None:
    path = C.REPORTS / "gold_sample.csv"
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
    print(f"labelled {len(rows)} rows: {len(rows)-bad} correct, {bad} incorrect")


if __name__ == "__main__":
    main()
