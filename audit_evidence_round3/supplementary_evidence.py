import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; E=ROOT/'audit_evidence_round3'
sys.path.insert(0,str(ROOT/'src'))
import normalize as N, textrules as T
d=N.build_drug_dictionary(N._load('drugs')[0]); N.curate_dictionary(d)
out=[]
for s in ['DCVAC/LuCa','pembrolizumab new XYZ','pembrolizumab and X','pegylated recombinant human hyaluronidase','paclitaxel and cisplatin (liposomal doxorubicin)','paclitaxel (liposomal doxorubicin and cisplatin)','platelet derived growth factor receptor tyrosine kinase inhibitor']:
    out.append(dict(input=s,split=T.split_combination(s),result=N.resolve_drug_string(s,d,list(d['index']))))
(E/'domain_supplementary_probes.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
entries=[]
def quote(file,start,end,objection,evidence):
    lines=(ROOT/file).read_text(encoding='utf-8').splitlines()
    entries.append(dict(file=file,line_start=start,line_end=end,verbatim='\n'.join(lines[start-1:end]),objection=objection,evidence=evidence))
quote('README.md',85,92,'Neither weighted Wilson bounds nor a degenerate empirical bootstrap establishes a calibrated uncertainty range; conservatism is not proved.','stats_numbers_results.json')
quote('README.ko.md',65,71,'Same interval claim; the observed spread is not a confidence statement.','stats_numbers_results.json')
quote('README.md',141,145,'GSK and GlaxoSmithKline still produce an ownership edge for a legal rename.','graph_snapshot_checks.json; graph_company_probes.json')
quote('README.ko.md',110,113,'Same rename/ownership contradiction.','graph_company_probes.json')
quote('README.md',169,172,'The registry screen still accepts ICE as IFOSFAMIDE and removes a correct alias of PEGVORHYALURONIDASE ALFA beyond the stated known examples.','domain_probes.json; pharma_late_probes.json')
quote('README.ko.md',131,133,'Same registry-screen generalization.','domain_probes.json; pharma_late_probes.json')
quote('README.md',255,260,'A reference-placebo marker anywhere blocks active cisplatin in cisplatin + placebo to match pembrolizumab despite the combination separator.','domain_probes.json')
quote('README.md',271,276,'Residues shorter than five alphabetic characters and not a dev code disappear; pembrolizumab new XYZ loses both tokens.','domain_supplementary_probes.json')
quote('README.ko.md',207,209,'Same all-components/all-residues claim.','domain_supplementary_probes.json')
quote('README.md',282,287,'Known biosimilar FDA suffixes outside regex stems bypass blocking, uppercase originator suffix is blocked, nested conjunction prevents raw-part match.','pharma_product_probes.json; domain_probes.json; domain_supplementary_probes.json')
quote('README.ko.md',213,217,'Same broad product-protection claim.','pharma_product_probes.json; domain_supplementary_probes.json')
quote('README.md',299,301,'Pattern qualifier is capped at40 characters, so longer real qualifiers are unguarded; INN-like tokens exempt classes such as pembrolizumab-like antibodies.','domain_supplementary_probes.json; domain_probes.json')
quote('README.ko.md',227,228,'Same qualifier-pattern scope limitation.','domain_supplementary_probes.json')
quote('README.md',380,381,'Query directly looks up aliases without resolver refusal rules; Mvasi and bare platinum bypass protections.','query_resolution_bypass.json')
quote('README.md',404,407,'Checker also misses names and figures: aspirin,1e6,and Unicode fraction all pass.','query_groundedness_probes.json')
quote('README.md',414,417,'The autologous-prefixed exact sample still creates a live TASADENOTUREV edge.','graph_ccl21_edges.json; pharma_late_probes.json')
quote('README.ko.md',291,293,'Same live vaccine error falsely declared gone.','graph_ccl21_edges.json')
quote('README.md',423,426,'ICE is still one member IFOSFAMIDE; additionally FOLFIRI/mFOLFOX6 do not include capecitabine.','domain_probes.json')
quote('README.ko.md',297,299,'Same regimen generalization.','domain_probes.json')
quote('README.md',446,448,'The wide interval cannot confirm repairs; test coverage and independent relabeling are separate evidence.','stats_numbers_results.json; pharma_rescore.json')
quote('README.ko.md',312,313,'Same inference that interval confirms repairs.','stats_numbers_results.json; pharma_rescore.json')
quote('README.md',461,464,'The asserted name/number floor is breached by lowercase aspirin,scientific notation1e6,and Unicode fractions.','query_groundedness_probes.json')
quote('README.ko.md',330,331,'Same name/number floor counterexamples.','query_groundedness_probes.json')
quote('README.md',495,498,'Later stages also read resolved.json,gold CSVs,and persistent SQLite; provenance stores fetched_at but no code revision, so concurrent source+logic changes are not disentangled.','src/run_all.py:3; src/evaluate.py; src/graph.py')
quote('README.ko.md',349,351,'Same source-versus-logic provenance guarantee.','src/run_all.py; src/graph.py')
(E/'overclaims_inventory.json').write_text(json.dumps(entries,indent=2,ensure_ascii=False),encoding='utf-8')
sources=[
 dict(claim='ICE is a multiple-agent regimen, not an alias for ifosfamide alone.',url='https://www.cancer.gov/publications/dictionaries/cancer-drug/def/ice-regimen'),
 dict(claim='Zr89-pembrolizumab is a radiolabeled imaging agent distinct from unlabeled pembrolizumab.',url='https://www.cancer.gov/publications/dictionaries/cancer-drug/def/zirconium-zr-89-pembrolizumab'),
 dict(claim='Etoposide phosphate is a covalent prodrug converted by dephosphorylation.',url='https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7499fc35-fae8-44ad-bbab-9a1a589bf3ee'),
 dict(claim='DN101 is a new calcitriol formulation with different systemic exposure.',url='https://pubmed.ncbi.nlm.nih.gov/16278401/'),
 dict(claim='Tasadenoturev is the oncolytic adenovirus Ad5-DNX2401, not a CCL21-transduced dendritic cell vaccine.',url='https://www.cancer.gov/publications/dictionaries/cancer-drug/def/tasadenoturev'),
]
(E/'domain_primary_sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
