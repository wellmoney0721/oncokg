# Independent isotope adjudication — round 17

**The exact M16 blocker is FIXED; a related originator leak remains.** This independently executed reused m16 adjudicator captures 36 current/HEAD^ pairs, retaining all 17 original m16 adjudication inputs. [Script](adjudicate_tracer.py), [raw stages](adjudication_tracer.json), [adaptation hashes](reuse_manifest.json).

`I-124-labelled trastuzumab`, `trastuzumab labelled with I-124`, `I124 trastuzumab`, `F18 trastuzumab`, and `C14 paclitaxel` now refuse the unlabelled originator; trial and sponsor QA return zero evidence. HEAD^ accepts these cases with originator evidence. `BKM-120NX`, `AZD9291`, and `IL-2` retain BUPARLISIB, OSIMERTINIB, and ALDESLEUKIN respectively. `Y-90 trastuzumab` selects YTTRIUM Y-90 and discloses refusal of trastuzumab; it does not draw TRASTUZUMAB.

The exact M15 controls `89-ZrDFO trastuzumab`, `3hvinblastine`, and `A33124i` remain refused. Both current and HEAD^ refuse them.

## Independent new family

`iodine-I-124-labelled trastuzumab` and `trastuzumab labelled with iodine-I-124` draw **TRASTUZUMAB / CHEMBL1201585**, 13 live trials, no Refused entity, and **12/12** trial/sponsor QA evidence rows. `labelled-with-I124 trastuzumab`, `trastuzumab labelled-with-I124`, `trastuzumab conjugated-with-I-124`, and `trastuzumab labelled-with-C14` give the same originator outcomes. Current and HEAD^ query modules both leak; the test does not establish latest-patch introduction.

For `iodine-I-124-labelled trastuzumab`, the raw resolver yields CONTAINED_ALIAS + UNRESOLVED with no BLOCKED component. `_qualified` is false, `_resolver_blocked` is `{}`, `_marked` returns `None`, `_whole_name` is `None`, and the public linker emits the positive originator only. This is a genuine all-stage miss, not merely a helper discrepancy.

The new reverse one-letter check sees `T.canonical_key(w)` (`src/query.py:164,167`), so `iodine-I-124-labelled` becomes `iodinei124labelled`. `(?<![a-z])` then rejects the I because it now follows the e. In contrast, `I-124-labelled` becomes `i124labelled`, so the helper recognizes it and refuses at `_marked` (`src/query.py:395-397`). The isotope remains wholly within one original word; its preceding hyphen was removed before the boundary test. The two-letter item scan and other mass-first guards do not recover this case. `Engine.explore` selects the surviving drug at `src/app.py:88-95`.

`trastuzumab-I124` and `trastuzumab-[I124]` are not_found, and are explicitly not counted as originator leaks. The root and attack reviewer separately reproduce the promoted family over HTTP.

## Repeated labelled-product qualification

**NOT FIXED, inherited and nonblocking under the explicit labelled-product exception:** `89ZrDFO 18-FDG` refuses, while `89-ZrDFO 18-FDG` and `89Z.rDFO 18-FDG` select FLUDEOXYGLUCOSE F 18 with 1/1 QA evidence. `Cu64 lutathera`, `64-CuDFO lutathera`, and `Ga68 lutathera` select LUTETIUM OXODOTREOTIDE LU-177; `64CuDFO lutathera` refuses. `Cu64 FDG` and `FDG Cu64` select FLUDEOXYGLUCOSE F 18. All match HEAD^. These are recorded as specification/normalization clarifications, not an independently promoted unlabelled-originator blocker.

Counterfactual scope is only HEAD^ query module against current app/rules/data. No complete historical deployment or UI browser execution is implied.
