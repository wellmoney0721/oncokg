"""Corrections to the author's own gold labels, after an adversarial re-score.

The three gold samples were labelled by one annotator -- the same person who
wrote the matching rules. The Known Defects list said so from the start, but
saying it is not the same as testing it, so the labels were handed to an
independent reviewer with instructions to disagree.

The reviewer re-scored 62 rows and disagreed on five. On inspection all five
disagreements were right and the original labels were wrong, every one of them
*leniently* wrong -- which is the direction a self-scoring annotator fails in,
and the reason the exercise was worth doing.

Each correction is recorded here with its reason rather than quietly edited
into the CSV, so the published precision figures can be traced to the labels
that produced them, before and after.

    python src/apply_label_corrections.py          # apply and report
    python src/apply_label_corrections.py --check  # verify already applied

Re-score afterwards: python src/evaluate.py test (and dev, postfix).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

# (sample, row id, old verdict, new verdict, reason)
CORRECTIONS = [
    ("test", "3", "correct", "incorrect",
     "Abraxane is nab-paclitaxel (albumin-bound), a separate product with its "
     "own approval and label. It is not interchangeable with solvent-based "
     "paclitaxel and resolving it to CHEMBL428647 asserts an exposure that "
     "did not happen."),
    ("test", "22", "correct", "incorrect",
     "'Paclitaxel or Nab-Paclitaxel' names two distinct products. Resolving "
     "the second to PACLITAXEL as well emits the same EVALUATES edge twice "
     "for a trial whose whole point is the comparison between them."),
    ("test", "67", "correct", "incorrect",
     "HLX04 is Henlius's bevacizumab biosimilar, a distinct asset. Mapping it "
     "to CHEMBL1201583 makes the graph assert that Henlius sponsors trials of "
     "Genentech's molecule, and the asset under study disappears entirely."),
    ("test", "68", "correct", "incorrect",
     "'Bevacizumab-Pfizer' is Zirabev (PF-06439535), a biosimilar. Same "
     "defect as HLX04: the originator gets credit for a competitor's product."),
    ("dev", "139", "correct", "incorrect",
     "CHEMBL2108494 'INTERFERON' is a class node -- its aliases are 'ifn', "
     "'interferon alfa-2b', 'pegasys', 'pegylated interferon'. Accepting it "
     "is the same error as 'Epothilone' -> EPOTHILONE D, which this same "
     "annotator scored incorrect three rows earlier. The inconsistency is "
     "the tell."),
]

FILES = {"dev": "gold_dev.csv", "test": "gold_test.csv",
         "postfix": "gold_postfix.csv"}


def main() -> None:
    check_only = "--check" in sys.argv
    applied = skipped = 0

    for sample in sorted({c[0] for c in CORRECTIONS}):
        path = C.REPORTS / FILES[sample]
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        fields = list(rows[0].keys())
        by_id = {r["id"]: r for r in rows}

        for s, rid, old, new, reason in CORRECTIONS:
            if s != sample:
                continue
            row = by_id.get(rid)
            if row is None:
                sys.exit(f"{path.name}: no row with id {rid}")
            if row["verdict"] == new:
                skipped += 1
                continue
            if row["verdict"] != old:
                sys.exit(f"{path.name} id {rid}: expected verdict {old!r}, "
                         f"found {row['verdict']!r} - refusing to overwrite")
            if check_only:
                print(f"PENDING {sample}#{rid}: {old} -> {new}")
                continue
            row["verdict"] = new
            note = (row.get("reviewer_note") or "").strip()
            row["reviewer_note"] = (
                f"{note} | " if note else "") + f"corrected after independent re-score: {reason}"
            applied += 1
            print(f"{sample}#{rid}: {old} -> {new}\n    {reason}\n")

        if not check_only:
            with path.open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)

    print(f"applied {applied}, already correct {skipped}")
    if check_only and applied == 0:
        print("all corrections are already in the labels")


if __name__ == "__main__":
    main()
