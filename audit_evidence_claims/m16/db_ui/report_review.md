# Final evidence-only report review

Reviewed assembled `../REPORT.md` against the fresh DB/UI artifacts, new attack stage captures, helper source lines and historical disposition summaries. No execution workloads were rerun.

**The P1 conclusion is supported.** The exact `I-124-labelled trastuzumab` and `124I-labelled trastuzumab` stage-table entries agree with `attacks/new_results.json`; the former has 13 live trials and 12/12 QA rows, while the control refuses with zero evidence. Source references for the mass table, element-first two-letter regex, `_labelled` asymmetry and item-level check are correct. The report correctly calls this inherited and newly reproduced, rather than a demonstrated latest-patch originator regression.

**DB/UI and demo claims are supported.** 6,469 centres, 22 combinations, zero oracle errors, 19 DB assertions, 24 UI assertions, 4 fixture assertions, 36/36 demos and six map callbacks match the fresh evidence. The report accurately limits the Node VM checks to generated markup and exercised state, and does not claim browser-executed XSS verification. Fixed exact M15 cases, accepted over-refusals and the already-labelled-product ambiguity are kept distinct.

Two wording adjustments were sent to the root reviewer:

1. The M16-B1 paragraph immediately following the main example says `I-124-labelled trastuzumab, osimertinib` leaks and then says “reversing the list” retains the tracer as another drug. The exact reversed labelled spelling is not among the 42 `new_results.json` cases. The recorded reverse is `osimertinib, trastuzumab I-124` (and root has a shorter I-124 reversal). Name that exact observed reverse instead of implying the same full labelled string was rerun. The substantive behavior and verdict are unchanged.
2. The cost summary must distinguish newly measured repeated-match overhead from inherited concerns: current/HEAD^ repeated-`isa` medians are 4.37413/1.01015 seconds. Calling every cost “inherited” understates this observed difference. Root is already doing a bounded attribution/HTTP follow-up; incorporate that result rather than inferring significance solely from three timing samples.

The external medical sources were already verified by the root/attack reviewer; this pass checked that the report confines their claims to identity and notation. It did not repeat internet retrieval.

No other factual inconsistency found in the reviewed sections. No tracked file or REPORT.md was edited by this pass.
