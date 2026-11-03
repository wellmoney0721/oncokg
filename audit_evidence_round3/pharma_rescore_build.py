import csv,json,math
from pathlib import Path
base=Path('audit_evidence_round3/original/reports')
rows={int(r['id']):r for r in csv.DictReader((base/'gold_test.csv').open(encoding='utf-8'))}
selected=[1,2,3,4,6,7,8,12,13,16,18,19,22,23,24,29,30,*range(51,59),66,67,68,85,90,91,92,*range(133,148)]
sources={
'ateganosine':'https://precision.fda.gov/uniisearch/srs/unii/KR0RFB46DF',
'zimberelimab':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/zimberelimab',
'Abraxane':'https://www.accessdata.fda.gov/drugsatfda_docs/label/2020/021660s047lbl.pdf',
'retlirafusp':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/retlirafusp-alfa',
'catequentinib':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/catequentinib-hydrochloride',
'rivoceranib':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/rivoceranib-mesylate',
'Onureg':'https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=0e95e33f-8aba-4f19-b332-2416580d358b&type=display',
'serplulimab':'https://precision.fda.gov/uniisearch/srs/unii/S3GQZ2K36V',
'cixutumumab':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/cixutumumab',
'volociximab':'https://www.ncbi.nlm.nih.gov/mesh/67516631',
'osimertinib':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/osimertinib',
'cofetuzumab':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/cofetuzumab-pelidotin',
'cobolimab':'https://www.cancer.gov/research/participate/clinical-trials-search/v?id=NCI-2022-02774',
'vandetanib':'https://clinicaltrials.gov/study/NCT00445549',
'HLX04':'https://www.henlius.com/en/newsd/0/31147.html',
'Pfizer_bevacizumab':'https://cdn.clinicaltrials.gov/large-docs/99/NCT02364999/Prot_001.pdf',
'savolitinib':'https://dctd.cancer.gov/drug-discovery-development/reagents-materials/formulary/about/agents/savolitinib',
'pexmetinib':'https://aacrjournals.org/cancerres/article/76/16/4841/543854/Pexmetinib-A-Novel-Dual-Inhibitor-of-Tie2-and-p38',
'FLT':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/fluorothymidine-f-18',
'avb6':'https://clinicaltrials.gov/study/NCT05452005',
'F-AraG':'https://cdn.clinicaltrials.gov/large-docs/40/NCT04678440/Prot_SAP_000.pdf',
'cisplatin':'https://www.bccancer.bc.ca/drug-database-site/Drug%20Index/Cisplatin_monograph.pdf',
'DN101':'https://pubmed.ncbi.nlm.nih.gov/16278401/',
'DN101_full':'https://aacrjournals.org/clincancerres/article/11/21/7794/194150/Pharmacokinetics-and-Tolerability-of-a-Single-Dose',
'Keytruda':'https://www.cancer.gov/about-cancer/treatment/drugs/pembrolizumab',
'NanoPac':'https://pmc.ncbi.nlm.nih.gov/articles/PMC8421313/',
'bortezomib':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/bortezomib',
'JS001':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/toripalimab',
'Doxil':'https://www.accessdata.fda.gov/drugsatfda_docs/label/2016/050718s051lbl.pdf',
'ABI007':'https://www.accessdata.fda.gov/drugsatfda_docs/nda/2005/21660_ABRAXANE_biopharmr.PDF',
'interferon':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/recombinant-interferon-alfa'
}
notes={
1:('correct',['ateganosine'],'FDA GSRS explicitly lists 6-Thio-2-deoxyguanosine as ateganosine synonym.'),
2:('correct',['zimberelimab'],'AB122 is the development code of zimberelimab.'),
3:('incorrect',['Abraxane'],'Albumin-bound paclitaxel is a distinct formulation; FDA says not to substitute for other paclitaxel products.'),
4:('correct',['retlirafusp'],'SHR-1701 is retlirafusp alfa; only that component is scored.'),
6:('correct',['catequentinib'],'Anlotinib is the former name of catequentinib; AP/PC is outside this scored component.'),
7:('correct',['catequentinib'],'Anlotinib is catequentinib; the osimertinib component is not this row.'),
8:('correct',['catequentinib'],'Same former-name mapping; combination does not change anlotinib identity.'),
12:('correct',['rivoceranib'],'Apatinib is rivoceranib; camrelizumab misspelling elsewhere does not change this component.'),
13:('incorrect',['Onureg'],'CC-486 is oral azacitidine; label explicitly forbids substitution for IV/SC products.'),
16:('correct',['serplulimab'],'FDA GSRS lists HLX10 under serplulimab.'),
18:('correct',['cixutumumab'],'IMC-A12 and cixutumumab denote the same antibody.'),
19:('correct',['volociximab'],'NLM MeSH explicitly lists M200 under volociximab.'),
22:('incorrect',['Abraxane'],'The scored Nab-Paclitaxel component loses its albumin-bound formulation; paclitaxel alternative is a separate row.'),
23:('correct',['osimertinib'],'AZD9291 is osimertinib, not MEDI4736.'),
24:('correct',['cofetuzumab'],'PF-06647020 is the ADC cofetuzumab pelidotin; Q3W is a schedule.'),
29:('correct',['cobolimab'],'NCI trial names TSR-022 (cobolimab).'),
30:('correct',['vandetanib'],'Trial title and intervention identify ZD6474 as vandetanib.'),
66:('correct',['rivoceranib'],'Apatinib single-agent arm still names rivoceranib.'),
67:('incorrect',['HLX04'],'Manufacturer identifies HLX04 as its own bevacizumab biosimilar, not originator product.'),
68:('incorrect',['Pfizer_bevacizumab'],'Trial protocol identifies Bevacizumab-Pfizer as PF-06439535 biosimilar.'),
85:('correct',['savolitinib'],'NCI gives AZD6094 as savolitinib; Japan qualifier does not change molecule.'),
90:('correct',['pexmetinib'],'Original pharmacology research identifies ARRY-614 as pexmetinib.'),
91:('correct',['pexmetinib'],'Same ARRY-614 identity in RCC cohort; this is not the nivolumab/ipilimumab row.'),
92:('incorrect',['FLT'],'18F-FLT is fluorothymidine tracer, not unlabelled thymidine/doxribtimine.'),
133:('incorrect',['avb6'],'Trial separately describes avb6-binding peptide and FDG imaging; sharing isotope does not make them identical.'),
134:('incorrect',['F-AraG'],'F-AraG is a distinct radiotracer, not FDG.'),
135:('incorrect',['F-AraG'],'Capitalization does not change F-AraG identity.'),
136:('incorrect',['F-AraG'],'PET imaging qualifier does not make F-AraG FDG.'),
137:('incorrect',[],'Snapshot NCT07848243 lists 18F-FDG and [18F]F-PDL1-3 as two distinct interventions; isotope-only match is wrong.'),
138:('correct',['cisplatin'],'CDDP is established abbreviation for cisplatin.'),
139:('incorrect',['DN101','DN101_full'],'Under the repository criterion that distinct reformulations such as NanoPac must retain product identity, DN-101 is also a distinct proprietary oral formulation. Original human PK study documents different absorption characteristics from commercial calcitriol. This is a product-level disagreement, not a claim that its active molecule differs; DN-101 was investigational, not separately approved.'),
140:('correct',['Keytruda'],'KEYTRUDA names the pembrolizumab component, not GV20-0251.'),
141:('incorrect',['NanoPac'],'Intratumoral submicron paclitaxel formulation loses its product identity when mapped to conventional paclitaxel.'),
142:('correct',['Keytruda'],'KEYTRUDA names pembrolizumab; NGM707 is another component.'),
143:('correct',['Keytruda'],'KEYTRUDA names pembrolizumab; NGM831 and NGM438 are other components.'),
144:('correct',[],'Dexamethasone is explicitly one allowed steroid mouthwash in source trial. This verifies a possible named intervention, not proof every participant received it. Product granularity remains underspecified.'),
145:('correct',['JS001'],'JS001 identifies toripalimab; injection and chemotherapy qualifiers do not change that component.'),
146:('correct',['bortezomib'],'Velcade and PS-341 are bortezomib names.'),
147:('correct',['bortezomib'],'Former code PS-341 and brand Velcade identify bortezomib despite trademark characters.')
}
for i in range(51,59): notes[i]=('correct',[],'Scored component is the placebo/reference control, so withholding active-drug identity is correct. For coadministration strings this verdict applies only to placebo component, not the separately named active drug.')
tr=json.load(open('data/raw/trials.json',encoding='utf-8'))['data'];index={x['protocolSection']['identificationModule']['nctId']:i for i,x in enumerate(tr)}
out=[]
for i in selected:
 r=rows[i];v,keys,note=notes[i];out.append({'file':'reports/gold_test.csv','line':i+1,'id':i,'tier':r['tier'],'surface':r['raw'],'component':r['component'],'resolved_id':r['drug_id'],'resolved_target':r['resolved_name'],'author_verdict':r['verdict'],'audit_verdict':v,'disagreement':v!=r['verdict'],'reason':note,'web_evidence':[sources[k] for k in keys],'source_trial_url':'https://clinicaltrials.gov/study/'+r['example_nct'],'snapshot_field':f"data/raw/trials.json.data[{index[r['example_nct']]}].protocolSection.armsInterventionsModule"})
extras=[]
for sample,rid,keys,reason in [('dev',180,[],'Genexol-PM polymeric micelle is a different trial arm from conventional Genexol in the source trial.'),('dev',181,['Doxil'],'PLD is explicitly Doxil in source NCT04244552 and must not be substituted for conventional doxorubicin.'),('postfix',1,['ABI007','Abraxane'],'ABI-007 is Abraxane, already labelled incorrect for the same parent mapping in test and postfix id8.')]:
 r=next(r for r in csv.DictReader((base/f'gold_{sample}.csv').open(encoding='utf-8')) if int(r['id'])==rid)
 extras.append({'file':f'reports/gold_{sample}.csv','line':rid+1,'row':r,'audit_verdict':'incorrect','reason':reason,'evidence':[sources[k] for k in keys],'source_trial_url':'https://clinicaltrials.gov/study/'+r['example_nct'],'snapshot_field':f"data/raw/trials.json.data[{index[r['example_nct']]}].protocolSection.armsInterventionsModule"})
def wilson(k,n):
 z=1.959963984540054;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;rad=z*((p*(1-p)/n+z*z/(4*n*n))**0.5)/den;return [mid-rad,mid+rad]
summary={'held_out_rows_rescored':len(out),'sampling':'purposive, enriched for codes, digits, parentheticals, combinations, isotopes, biosimilars, and all placebo rows; no extrapolation of disagreement frequency','tiers_absent_from_gold_test':['FUZZY_AUTO','SALT_STRIPPED','CLEANED','FUZZY_REVIEW'],'held_out_disagreements':[x for x in out if x['disagreement']],'cross_sample_disagreements':extras,'corrected_as_labelled_raw':{'test':{'correct':102,'n':115,'precision':102/115,'wilson95':wilson(102,115)},'dev':{'correct':124,'n':137,'precision':124/137},'postfix':{'correct':35,'n':38,'precision':35/38}},'criterion':'Use repository product-identity criterion already applied to Abraxane/CC486/NanoPac consistently, not a molecular-structure-only criterion.'}
Path('audit_evidence_round3/pharma_rescore.json').write_text(json.dumps({'summary':summary,'rows':out},ensure_ascii=False,indent=2),encoding='utf-8')
Path('audit_evidence_round3/pharma_sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
