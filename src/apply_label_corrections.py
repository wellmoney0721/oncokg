"""Corrections to the author's own gold labels, after an adversarial re-score.

The three gold samples were labelled by one annotator -- the same person who
wrote the matching rules. The Known Defects list said so from the start, but
saying it is not the same as testing it, so the labels were handed to an
independent reviewer with instructions to disagree.

Round 1: a reviewer re-scored 62 rows and disagreed on five. On inspection all five
disagreements were right and the original labels were wrong, every one of them
*leniently* wrong -- which is the direction a self-scoring annotator fails in,
and the reason the exercise was worth doing.

Round 2: a Codex audit re-scored 58 held-out rows and disagreed on three,
each an application of the criterion round 1 had already set. All three were
again lenient.

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

# (sample, row id, raw string, component, resolved drug_id, old verdict,
#  new verdict, reason)
#
# The raw string, component and drug id pin each correction to the row it was written
# for. Checking the id and verdict alone would let a regenerated sample with
# different rows under the same ids absorb a correction meant for another row.
CORRECTIONS = [
    # -- round 1: independent re-score of 62 rows, five disagreements --------
    ("test", "3", "Abraxane (Maintenance)", "Abraxane", "CHEMBL428647", "correct", "incorrect",
     "Abraxane is nab-paclitaxel (albumin-bound), a separate product with its "
     "own approval and label. It is not interchangeable with solvent-based "
     "paclitaxel and resolving it to CHEMBL428647 asserts an exposure that "
     "did not happen."),
    ("test", "22", "Paclitaxel or Nab-Paclitaxel", "Nab-Paclitaxel", "CHEMBL428647", "correct", "incorrect",
     "'Paclitaxel or Nab-Paclitaxel' names two products the investigator may "
     "choose between (NCT07318883 is an HLX07-versus-placebo trial; the "
     "taxane is the backbone, not the comparison). Resolving the second to "
     "PACLITAXEL records nab-paclitaxel as solvent-based paclitaxel and "
     "duplicates the first component's edge."),
    ("test", "67", "Bevacizumab Biosimilar HLX04", "Bevacizumab Biosimilar", "CHEMBL1201583", "correct", "incorrect",
     "HLX04 is Henlius's bevacizumab biosimilar, a distinct asset. Mapping it "
     "to CHEMBL1201583 makes the graph assert that Henlius sponsors trials of "
     "Genentech's molecule, and the asset under study disappears entirely."),
    ("test", "68", "Bevacizumab-Pfizer", "Bevacizumab", "CHEMBL1201583", "correct", "incorrect",
     "'Bevacizumab-Pfizer' is Zirabev (PF-06439535), a biosimilar. Same "
     "defect as HLX04: the originator gets credit for a competitor's product."),
    ("dev", "139", "Cisplatin, Gemcitabine, Interferon-a", "Interferon-a", "CHEMBL2108494", "correct", "incorrect",
     "CHEMBL2108494 'INTERFERON' is a class node -- its aliases are 'ifn', "
     "'interferon alfa-2b', 'pegasys', 'pegylated interferon'. Accepting it "
     "is the same error as 'Epothilone' -> EPOTHILONE D, which this same "
     "annotator scored incorrect three rows earlier. The inconsistency is "
     "the tell."),
    # -- round 2: Codex audit of 58 held-out rows, two disagreements (CC-486,
    # NanoPac), plus one post-fix row it found by the same criterion -------
    # All three apply the criterion round 1 already set with Abraxane: a
    # separately approved, non-substitutable product is a different product,
    # even when the active molecule is the same.
    ("test", "13", "CC-486", "CC-486", "CHEMBL1489", "correct", "incorrect",
     "CC-486 is oral azacitidine (Onureg). Its label states it must not be "
     "substituted for intravenous or subcutaneous azacitidine, so by the "
     "Abraxane criterion it is a distinct product, not AZACITIDINE."),
    ("test", "141", "NanoPac (sterile nanoparticulate paclitaxel) Powder for Suspension", "sterile nanoparticulate paclitaxel",
     "CHEMBL428647", "correct", "incorrect",
     "NanoPac is a nanoparticulate paclitaxel formulation for local "
     "administration with its own development programme -- the same class "
     "of error as Abraxane, resolved through its parenthetical."),
    ("postfix", "8", "Nab-paclitaxel", "Nab-paclitaxel", "CHEMBL428647", "correct", "incorrect",
     "Nab-paclitaxel was corrected to incorrect in the test sample (rows 3 "
     "and 22) but left correct here. The same surface cannot be right in "
     "one sample and wrong in another."),
    # -- round 3: Codex audit of 47 difficult rows, four disagreements -------
    # The same product-level criterion again. Two of these sat in the dev
    # sample and one in post-fix; round 2 had cleaned only the rows it read.
    ("test", "139", "DN-101 (calcitriol) - Drug", "calcitriol", "CHEMBL846", "correct", "incorrect",
     "DN-101 is a high-dose calcitriol formulation developed under its own "
     "code (Asentar) and studied as a distinct investigational product; "
     "resolving it through its bracketed ingredient loses the product, the "
     "same error as NanoPac."),
    ("dev", "180", 'Paclitaxel loaded polymeric micelle (Genexol-PM®)', 'Genexol-PM®', "CHEMBL428647", "correct", "incorrect",
     "Genexol-PM is polymeric-micelle paclitaxel, a separate product; its "
     "trial compares it against conventional Genexol in separate arms."),
    ("dev", "181", "Pegylated liposomal doxorubicin (PLD)", "PLD", "CHEMBL53463", "correct", "incorrect",
     "Pegylated liposomal doxorubicin is Doxil/Caelyx, whose label forbids "
     "substituting it for conventional doxorubicin."),
    ("postfix", "1", "ABI-007 (Abraxane) and Carboplatin", "ABI-007", "CHEMBL428647", "correct", "incorrect",
     "ABI-007 is the development code of Abraxane; post-fix row 8 "
     "(Nab-paclitaxel) was already corrected for the same product."),
]

FILES = {"dev": "gold_dev.csv", "test": "gold_test.csv",
         "postfix": "gold_postfix.csv"}


def main() -> None:
    check_only = "--check" in sys.argv
    applied = skipped = pending = 0

    for sample in sorted({c[0] for c in CORRECTIONS}):
        path = C.REPORTS / FILES[sample]
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        fields = list(rows[0].keys())
        by_id = {r["id"]: r for r in rows}

        for s, rid, raw, component, drug_id, old, new, reason in CORRECTIONS:
            if s != sample:
                continue
            row = by_id.get(rid)
            if row is None:
                sys.exit(f"{path.name}: no row with id {rid}")
            if (row["raw"] != raw or row["drug_id"] != drug_id
                    or row.get("component") != component):
                sys.exit(f"{path.name} id {rid}: correction written for "
                         f"{raw!r} -> {drug_id}, row holds {row['raw']!r} -> "
                         f"{row['drug_id']} - refusing to apply")
            if row["verdict"] == new:
                # a reason corrected after it was applied is re-written into
                # the note, so the CSV never carries a superseded rationale
                prefix = "corrected after independent re-score: "
                note = row.get("reviewer_note") or ""
                if prefix in note and not note.endswith(prefix + reason):
                    if check_only:
                        pending += 1
                        print(f"PENDING {sample}#{rid}: reviewer note out of date")
                    else:
                        row["reviewer_note"] = note[:note.index(prefix)] + prefix + reason
                        applied += 1
                        print(f"{sample}#{rid}: reviewer note re-synced")
                    continue
                skipped += 1
                continue
            if row["verdict"] != old:
                sys.exit(f"{path.name} id {rid}: expected verdict {old!r}, "
                         f"found {row['verdict']!r} - refusing to overwrite")
            if check_only:
                pending += 1
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

    if check_only:
        # A check that prints PENDING and then reports success is a check that
        # always passes. Pending corrections are a failure, with a non-zero exit.
        print(f"pending {pending}, already applied {skipped}")
        if pending:
            sys.exit(1)
        print("all corrections are already in the labels")
    else:
        print(f"applied {applied}, already correct {skipped}")


if __name__ == "__main__":
    main()
