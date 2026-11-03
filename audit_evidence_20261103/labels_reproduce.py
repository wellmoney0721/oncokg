"""Read-only reproduction of independent drug/label audit. Writes only audit evidence."""
import csv, json, sys, tempfile, io, contextlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
import normalize as N, textrules as T, apply_label_corrections as A
OUT=Path(__file__).resolve().parent
sources={
 'ateganosine':'https://cdn.who.int/media/docs/default-source/international-nonproprietary-names-%28inn%29/pl130.pdf',
 'zimberelimab':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/zimberelimab',
 'retlirafusp':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/retlirafusp-alfa',
 'abraxane':'https://www.cancer.gov/about-cancer/treatment/drugs/nanoparticlepaclitaxel',
 'onureg':'https://www.accessdata.fda.gov/drugsatfda_docs/label/2020/214120s000lbl.pdf',
 'cc486':'https://www.cancer.gov/news-events/cancer-currents-blog/2020/cc-486-aml-improves-survival-maintenance-therapy',
 'nanopac':'https://nanology.us/wp-content/uploads/2020/06/Nanology_Nanopac_lung_cancer_IND.pdf',
 'nanopac_trial':'https://pmc.ncbi.nlm.nih.gov/articles/PMC8421313/',
 'hlx04':'https://www.henlius.com/en/newsd/0/31147.html',
 'zirabev':'https://www.accessdata.fda.gov/drugsatfda_docs/nda/2019/761099Orig1s000SumR.pdf',
 'mvasi':'https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/761028s011lbl.pdf',
 'interferon':'https://www.ama-assn.org/about/united-states-adopted-names-usan/interferons',
 'apatinib':'https://precision.fda.gov/uniisearch/srs/unii/5s371k6132',
 'cisplatin':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/cisplatin',
 'savolitinib':'https://dctd.cancer.gov/drug-discovery-development/reagents-materials/formulary/about/agents/savolitinib',
 'pexmetinib':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/pexmetinib',
 'flt':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/fluorothymidine-f-18',
 'farag':'https://cdn.clinicaltrials.gov/large-docs/40/NCT04678440/Prot_SAP_000.pdf',
 'calcitriol':'https://clinicaltrials.gov/study/NCT00182741',
 'keytruda':'https://www.cancer.gov/about-cancer/treatment/drugs/pembrolizumab',
 'js001':'https://cdn.clinicaltrials.gov/large-docs/40/NCT03474640/Prot_000.pdf',
 'bortezomib':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/bortezomib',
 'etoposide_phosphate':'https://www.accessdata.fda.gov/drugsatfda_docs/label/2019/020457s019lbl.pdf',
 'prednisolone_phosphate':'https://www.accessdata.fda.gov/drugsatfda_docs/nda/pre96/019157_PEDIAPRED_ORIGINAL_AP.pdf',
 'tobramycin':'https://www.fda.gov/drugs/development-resources/fda-rationale-recognition-decision-gentamicin-tobramycin-and-amikacin-enterobacterales-and-p',
 'cemiplimab':'https://www.fda.gov/drugs/drug-approvals-and-databases/fda-approves-cemiplimab-rwlc-metastatic-or-locally-advanced-cutaneous-squamous-cell-carcinoma',
 'amivantamab':'https://www.cancer.gov/about-cancer/treatment/drugs/amivantamab-vmjw',
 'db1303':'https://www.cancer.gov/research/participate/clinical-trials-search/v?id=NCI-2024-07665'
}
sources.update({'gv20':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/anti-igsf8-monoclonal-antibody-gv20-0251','ngm707':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/anti-ilt2-anti-ilt4-monoclonal-antibody-ngm707','ngm831':'https://www.cancer.gov/research/participate/clinical-trials-search/v?id=NCI-2022-01100&r=1','ngm438':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/anti-lair1-monoclonal-antibody-ngm438'})
# Each entry is an explicit independent judgement; no author verdict is used to assign it.
reviews={
1:('correct','2-prime-deoxy-6-thioguanosine is ateganosine.',['ateganosine']),
2:('correct','AB122 is zimberelimab.',['zimberelimab']),
3:('incorrect','Abraxane is the albumin-bound nanoparticle product; collapse loses product identity under the declared audit criterion.',['abraxane']),
4:('correct','SHR-1701 is retlirafusp alfa; this component is one member of the combination.',['retlirafusp']),
13:('incorrect','CC-486 is oral azacitidine, not substitutable for IV/SC azacitidine. This trial contains a separate Vidaza intervention; same-molecule collapse loses the tested product distinction.',['cc486','onureg']),
51:('correct','Only the placebo component is blocked; AZD9291 exposure belongs to the other component.',[]),
52:('correct','The explicitly separated placebo is not camrelizumab or chemotherapy.',[]),
53:('correct','Blinded placebo names a control intervention, not a drug.',[]),
54:('correct','Placebo component is blocked; the combined erlotinib is a separate exposure.',[]),
55:('correct','Placebo component is not the separately co-administered rhG-CSF.',[]),
56:('correct','Placebo Erlotinib describes a matching placebo, not erlotinib exposure.',[]),
57:('correct','Placebo is blocked and co-administered docetaxel remains separate.',[]),
58:('correct','Matching placebo is not zipalertinib.',[]),
63:('correct','Alpelisib is explicitly named in the combination phrase.',[]),
64:('correct','Alecensa and alectinib refer to the same active moiety; hydrochloride is a counterion form.',[]),
65:('correct','Amrubicin is explicit; hydrocloride is a misspelling of hydrochloride.',[]),
66:('correct','Apatinib is rivoceranib.',['apatinib']),
67:('incorrect','HLX04 is the Henlius biosimilar, not the originator product.',['hlx04']),
68:('incorrect','Pfizer bevacizumab is PF-06439535/Zirabev, a biosimilar.',['zirabev']),
69:('correct','The named component is carboplatin; chemotherapy does not change its identity.',[]),
70:('correct','The named component is cisplatin; for injection specifies presentation.',['cisplatin']),
71:('correct','Cisplatinum is cisplatin; schedule fragments do not change molecule.',['cisplatin']),
72:('correct','Carboplatin is a named component of the carboplatin/paclitaxel combination.',[]),
73:('correct','Sorafenib is explicitly named alongside everolimus.',[]),
74:('correct','Carboplatin is one of the two hyphen-joined medicines.',[]),
75:('correct','Gefitinib group names gefitinib.',[]),
76:('correct','Gemcitabine is a named component before subsequent docetaxel.',[]),
77:('correct','Cisplatin is a named component before subsequent docetaxel.',['cisplatin']),
78:('correct','Gemcitabine is a named regimen component; semicolons do not negate it.',[]),
79:('correct','Dasatinib is explicitly present in the regimen.',[]),
80:('correct','Oxaliplatin is explicitly listed between irinotecan and Neulasta.',[]),
81:('correct','Lenvatinib pill identifies lenvatinib.',[]),
82:('correct','Necitumumab is an explicit member of the three-drug regimen.',[]),
83:('correct','Pembrolizumab is an explicit regimen component.',['keytruda']),
84:('correct','Paclitaxel is explicitly one allowed chemotherapy option; this does not mean every patient receives it.',[]),
85:('correct','AZD6094 is savolitinib; Japan only describes cohort geography.',['savolitinib']),
86:('correct','Carboplatin is an explicit component; the pegylated qualifier applies to endostatin.',[]),
87:('correct','Paclitaxel is an explicit component; the pegylated qualifier applies to endostatin.',[]),
88:('correct','Pembrolizumab is explicitly administered after randomization.',['keytruda']),
89:('correct','Pemetrexed is an explicit component with bevacizumab.',[]),
90:('correct','ARRY-614 is pexmetinib; melanoma is cohort context.',['pexmetinib']),
91:('correct','ARRY-614 is pexmetinib; RCC is cohort context.',['pexmetinib']),
92:('incorrect','FLT is fluorine-18 fluorothymidine, not unlabelled thymidine/doxribtimine.',['flt']),
133:('incorrect','An isotope label on alpha-v-beta-6-binding peptide is not FDG.',[]),
134:('incorrect','F-AraG is a distinct tracer, not FDG.',['farag']),
135:('incorrect','F-AraG is a distinct tracer, not FDG.',['farag']),
136:('incorrect','F-AraG is a distinct tracer, not FDG.',['farag']),
137:('incorrect','F-PDL1-3 is a labelled PD-L1 tracer, not FDG.',[]),
138:('correct','CDDP is cisplatin; the full chemical descriptor agrees.',['cisplatin']),
139:('correct','DN-101 is high-dose calcitriol; a dose distinction alone is not another molecule.',['calcitriol']),
140:('correct','KEYTRUDA is a genuine pembrolizumab mention in the raw intervention, so retain the emitted-resolution verdict. Separately, tracing proves the parser used its parenthesis to replace GV20-0251; that is a provenance/segmentation bug, not an unqualified false target at whole-string scope.',['gv20','keytruda']),
141:('incorrect','NanoPac is a manufactured nanoparticle intratumoral formulation, so collapsing to conventional paclitaxel violates the same product-identity rule used to reject Abraxane.',['nanopac','nanopac_trial']),
142:('correct','KEYTRUDA genuinely names pembrolizumab in the raw intervention. Tracing separately proves NGM707 was replaced by that unrelated parenthesis; record the provenance bug without changing the whole-string emitted-target label.',['ngm707','keytruda']),
143:('correct','KEYTRUDA genuinely names pembrolizumab in the raw intervention. Parser separately replaces NGM831 and NGM438 with that unrelated parenthesis, producing duplicates and hiding unresolved agents. Treat as parser/unit ambiguity, not a definite whole-string target label error.',['ngm831','ngm438','keytruda']),
144:('correct','Dexamethasone is explicitly an allowed steroid-mouthwash option; an EVALUATES edge can represent that option, not proof every patient received it.',[]),
145:('correct','JS001 is toripalimab.',['js001']),
146:('correct','Velcade and PS-341 are bortezomib.',['bortezomib']),
147:('correct','Velcade and PS-341 are bortezomib.',['bortezomib'])}
rows=list(csv.DictReader((ROOT/'reports/gold_test.csv').open(encoding='utf-8')))
ledger=[]
for line,row in enumerate(rows,2):
 rid=int(row['id'])
 if rid in reviews:
  verdict,reason,keys=reviews[rid]
  ledger.append(dict(row,source_file='reports/gold_test.csv',line=line,audit_verdict=verdict,audit_reason=reason,disagrees=verdict!=row['verdict'],external_sources=[sources[k] for k in keys],snapshot_source=f"data/raw/trials.json:data[protocolSection.identificationModule.nctId={row['example_nct']}].protocolSection.armsInterventionsModule.interventions"))
assert len(ledger)>=40
summary={'reviewed_count':len(ledger),'selected_ids':sorted(reviews),'tiers':dict(Counter(r['tier'] for r in ledger)),'test_absent_tiers':['FUZZY_AUTO','SALT_STRIPPED','CLEANED','FUZZY_REVIEW'],'criterion':'Molecule identity plus the repository explicitly declared preservation of distinct regulatory/formulation products. Under an active-moiety-only ontology, product-collapse labels and all earlier corrections need redefinition.','disagreement_ids':[r['id'] for r in ledger if r['disagrees']],'headline_after_two_changes':{'raw_correct':103,'raw_total':115,'raw_precision':103/115,'author_current_weight_stratified_precision':0.9600915331807781},'postfix_additional_disagreement':{'file':'reports/gold_postfix.csv','line':9,'id':'8','surface':'Nab-paclitaxel','target':'CHEMBL428647 PACLITAXEL','author':'correct','audit':'incorrect','reason':'Exact same product-collapse as corrected test id22; unchanged lenient postfix label.','source':sources['abraxane'],'raw_after':36/38}}
summary['component_binding_sensitivity_not_main_headline']={'ids':[140,142,143],'raw_if_a_different_pre_parenthetical_binding_metric_is_used':100/115,'scope_caveat':'Not a definite correction to the repository emitted-target precision: KEYTRUDA is present in each raw intervention. Actual resolver branch binds unknown agents to unrelated parentheses, drops their residue and duplicates pembrolizumab. Retain current labels and report parser/provenance defect separately.'}
(OUT/'labels_rescore.json').write_text(json.dumps({'summary':summary,'rows':ledger,'sources':sources},indent=2,ensure_ascii=False),encoding='utf-8')
D=N.build_drug_dictionary(json.loads((ROOT/'data/raw/drugs.json').read_text(encoding='utf-8'))['data']);N.curate_dictionary(D)
texts=['tobramycin','corticosteroid','corticosteroids','prednisolone phosphate','etoposide phosphate','Leucovorin calcium','Leucovorin','Mvasi','Alymsys','Zirabev','Bevacizumab biosimilars','NanoPac (sterile nanoparticulate paclitaxel) Powder for Suspension','CC-486','Liposomal Doxorubicin and cisplatin','paclitaxel liposome','paclitaxel polymeric micelles','cemiplimab-rwlc','amivantamab-vmjw','tarlatamab-dlle','Injection of pembrolizumab','pembrolizumab antibody','mab inhibitor','Antineoplastic agents','No pembrolizumab','pembrolizumab without paclitaxel','DrugX and pembrolizumab (Keytruda)','pembrolizumab + placebo to match docetaxel','DB-1303/BNT323','trastuzumab deruxtecan/T-DXd']
texts += [r['raw'] for r in rows if r['id'] in ['140','142','143']]
probes=[N.resolve_drug_string(x,D,list(D['index'])) for x in texts]
(OUT/'labels_domain_probes.json').write_text(json.dumps({'reproduction':'python audit_evidence_20261103/labels_reproduce.py','probes':probes,'line_references':{'salt':'src/textrules.py:41-49; src/normalize.py:572-579','class':'src/textrules.py:97-117','distinct':'src/textrules.py:123-149; src/normalize.py:467-469,509,525','containment':'src/normalize.py:424-458,590-625','global_parenthetical':'src/normalize.py:559-570','combo':'src/textrules.py:155-159,283-294'},'sources':sources},indent=2,ensure_ascii=False),encoding='utf-8')
with tempfile.TemporaryDirectory() as t:
 for f in ('gold_dev.csv','gold_test.csv'):
  rs=list(csv.DictReader((ROOT/'reports'/f).open(encoding='utf-8')))
  if f=='gold_test.csv': next(r for r in rs if r['id']=='3')['verdict']='correct'
  with (Path(t)/f).open('w',encoding='utf-8',newline='') as h:
   w=csv.DictWriter(h,fieldnames=rs[0].keys());w.writeheader();w.writerows(rs)
 old_reports=A.C.REPORTS;old_argv=sys.argv;A.C.REPORTS=Path(t);sys.argv=['apply_label_corrections.py','--check'];buf=io.StringIO()
 with contextlib.redirect_stdout(buf): A.main()
 A.C.REPORTS=old_reports;sys.argv=old_argv
 check_output=buf.getvalue()
corrections=[{'sample':s,'id':rid,'audit_of_new_verdict':'valid under product-preserving ontology' if s=='test' else 'valid: class name cannot identify a molecular product','source_urls':[sources[x] for x in ({'3':['abraxane'],'22':['abraxane'],'67':['hlx04'],'68':['zirabev'],'139':['interferon']}[rid])]} for s,rid,old,new,why in A.CORRECTIONS]
(OUT/'labels_corrections_check.json').write_text(json.dumps({'five_corrections':corrections,'one_pending_check_stdout':check_output,'one_pending_check_exit_code':0,'guard_defects':['--check prints all corrections applied while pending; applied cannot increment on check path.','Identity guard uses row id plus verdict only; no raw or drug_id assertion.','Per-file writes before later sample validation make operation non-atomic.'],'rationale_error':{'file':'src/apply_label_corrections.py','lines':[38,41],'claim':'trial whose whole point is the comparison between them','evidence':'NCT07318883 is HLX07 versus placebo atop chemotherapy; paclitaxel/nab-paclitaxel are permitted chemotherapy options in all arms, not the primary comparison.','snapshot_field':'data/raw/trials.json:data[protocolSection.identificationModule.nctId=NCT07318883].protocolSection.identificationModule.officialTitle'}},indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2));print(check_output)
print('Probe outputs:')
for r in probes: print(r['raw'],[(c['component'],c['tier'],c['drug_id']) for c in r['components']])
