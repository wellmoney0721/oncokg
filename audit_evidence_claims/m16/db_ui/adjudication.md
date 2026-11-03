# Independent staged adjudication — round 16

Current HEAD is `8ebd6629b51a474f216457c8c00f20152304bd1d`. [Reused stage script](adjudicate_tracer.py) captures current and HEAD^ query modules against the same current app/rules/data. This is a method comparison, not a reconstruction of an entire prior deployment. [Raw stages](adjudication_tracer.json).

## Independently confirmed unlabelled-originator bypass

`I-124 trastuzumab` draws **TRASTUZUMAB / CHEMBL1201585**, with **13 live trials**. Both trial and sponsor QA return **12 evidence rows**. The raw resolver emits CONTAINED_ALIAS for trastuzumab plus UNRESOLVED for I-124; `_qualified` is false, resolver veto is `{}`, `_marked` returns `None` during the real `_link` call, the whole-name shortcut is `None`, and the public linker emits Drug without Refused. HEAD^ has the same behavior.

The mass table includes I-124 (`src/query.py:123-127`). `_medical_isotope_in` recognizes mass-first labels, but its element-first expression requires two letters (`src/query.py:139-150`), so `i124` is not recognized. The selected TRASTUZUMAB preferred name is not labelled; the problem is missed input recognition, not exemption. `_marked` therefore reaches its end (`src/query.py:371-409`), and the map selects the surviving Drug (`src/app.py:88-95`). Parent review separately confirms the failure over HTTP.

The old exact cases `89-ZrDFO trastuzumab`, `3hvinblastine`, and `A33124i` now refuse and produce zero trial/sponsor QA rows. The same HEAD^ query module accepted them. `A33124I` refuses on both versions. These repairs are **FIXED for their exact reproductions**, despite the separate element-first gap.

## Already-labelled product: nonblocking ambiguity and normalization discrepancy

`89ZrDFO 18-FDG` refuses, but `89-ZrDFO 18-FDG` and `89Z.rDFO 18-FDG` draw **FLUDEOXYGLUCOSE F 18 / CHEMBL2030434**, with one live trial and **1/1** trial/sponsor QA evidence rows. The first two have the identical canonical key `89zrdfo18fdg`.

The raw resolver is UNRESOLVED for both forms; `_qualified` is false and the veto is empty. The unpunctuated form returns `18-FDG (89ZrDFO)` from `_marked`; the hyphenated form returns `None`. The word-fragment mechanism of M15 remains in the earlier checks (`src/query.py:324-364`), while `_labelled` exempts this preferred name from the new item-wide rule (`src/query.py:153-163,375-379`). Both forms behave identically under HEAD^, so this discrepancy is inherited.

`Cu64 lutathera`, `Ga68 lutathera`, and `64-CuDFO lutathera` likewise retain LUTETIUM OXODOTREOTIDE LU-177, while `64CuDFO lutathera` refuses; `Cu64 FDG` and `FDG Cu64` retain the F18 product. These inputs introduce another isotope around an already-labelled product. They warrant clarification and consistency work, but are **not promoted to an unlabelled-originator blocker**: the brief expressly permits labelled products, and no external chemical-identity claim is needed for this audit verdict. The clean I-124/TRASTUZUMAB bypass independently fails the approval bar.

The dictionary contains **14 preferred names** classified by `_labelled`; all visibly carry explicit isotope designations. No obvious preferred-name false positive was found in that scan. [Names](labelled_preferred_names.json), [focused outputs](labelled_product_probe.json).
