import collections, copy, json, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
E=ROOT/'audit_evidence_round3'
sys.path.insert(0,str(ROOT/'src'))
import normalize as N, textrules as T

raw=json.loads((ROOT/'data/raw/drugs.json').read_text(encoding='utf-8'))['data']
d=N.build_drug_dictionary(raw); findings=N.curate_dictionary(d); keys=list(d['index'])
names=lambda out:[dict(tier=c['tier'],drug_id=c.get('drug_id'),name=d['drugs'].get(c.get('drug_id'),{}).get('name'),component=c['component'],rules=c.get('rules'),note=c.get('note')) for c in out['components']]
cases=[
 'VEGF blockers','cytotoxic agents','DNA damaging agents','platinum salts',
 'small molecule kinase inhibitors','TNF-alpha blockers','anti-cancer agents',
 'immune checkpoint blockers','pembrolizumab-like antibodies','pembrolizumab inhibitor',
 'paclitaxel chemotherapy','osimertinib chemotherapy','cisplatin chemotherapy',
 'pembrolizumab-free regimen','Arm A without pembrolizumab','treatment without pembrolizumab',
 'No pembrolizumab or chemotherapy','pembrolizumab omitted','pembrolizumab resistance assay',
 'cisplatin-resistant cell line','pembrolizumab test kit','paclitaxel allergy test',
 'pembrolizumab 100 mg/mL','pembrolizumab (MK-3475/MK3475)',
 'cisplatin and/or pemetrexed','pemetrexed and vitamin B12','paclitaxel/albumin',
 'dexamethasone acetate','prednisone acetate','cortisone acetate','megestrol acetate',
 'abiraterone acetate','hydrocortisone butyrate','prednisolone hemisuccinate',
 'dexamethasone sodium phosphate','dexamethasone phosphate','dexamethasone 21-phosphate',
 'etoposide phosphate','fludarabine phosphate', 'erlotinib hydrochloride','Tarceva','erlotinib HCl',
 'Cemiplimab-RWLC','cemiplimab-rwlc','pembrolizumab-qwert','pembrolizumab-abcd',
 'bevacizumab-bvzr 10 mg','bevacizumab-bvzr','pegfilgrastim-jmdb',
 'bevacizumab biosimilars','biosimilar of bevacizumab','injection of pembrolizumab',
 'Genexol','Genexol-PM','Paclitaxel (Taxol) and Nab-paclitaxel (Abraxane)',
 'cisplatin + placebo to match pembrolizumab','placebo to match pembrolizumab + cisplatin',
 'placebo + docetaxel','docetaxel (with or without pembrolizumab)',
 'limertinib','ASK-120067','pankomab-gex','gatipotuzumab','pegylated filgrastim',
 'cyclophosphamide methotrexate fluorouracil','FOLFOX','CHOP','ICE',
 'BMS-936558-99','AZD9291-123','AZD9291-99','MK-3475-99',
 '[89Zr]pembrolizumab','89Zr-pembrolizumab','[89Zr]-pembrolizumab',
]
probes=[dict(input=s,cleaned=T.clean_surface(s),parts=T.split_combination(T.clean_surface(s)['cleaned']),result=names(N.resolve_drug_string(s,d,keys))) for s in cases]
(E/'domain_probes.json').write_text(json.dumps(probes,indent=2,ensure_ascii=False),encoding='utf-8')
print('probes written',flush=True)

# Disable ONLY the registry rule for a paired counterfactual; all other curation stays.
origforeign=N._foreign_registry_alias; origshort=N._ambiguous_short_alias
N._foreign_registry_alias=lambda *args:None
N._ambiguous_short_alias=lambda *args:False
without=N.build_drug_dictionary(raw); nofindings=N.curate_dictionary(without); oldkeys=list(without['index'])
N._foreign_registry_alias=origforeign; N._ambiguous_short_alias=origshort
resolved=json.loads((E/'original/data/processed/resolved.json').read_text(encoding='utf-8'))
surfaces=collections.Counter(i['raw'] for t in resolved['trials'] for i in t['interventions'])
accepted=lambda o:sum(c['tier'] in N.ACCEPTED_TIERS for c in o['components'])
sig=lambda o:[(c['tier'],c.get('drug_id'),c['component']) for c in o['components']]
stats=collections.Counter(); changes=[]
for idx,(s,freq) in enumerate(surfaces.items()):
    current=N.resolve_drug_string(s,d,keys)
    prior=N.resolve_drug_string(s,without,oldkeys)
    stats['current_accepted']+=accepted(current)*freq
    stats['without_registry_rule_accepted']+=accepted(prior)*freq
    stats['current_total_components']+=len(current['components'])*freq
    stats['without_registry_rule_total_components']+=len(prior['components'])*freq
    if sig(current)!=sig(prior):
        changes.append(dict(raw=s,occurrences=freq,current=names(current),without_registry_rule=names(prior)))
        stats['changed_distinct_surfaces']+=1; stats['changed_occurrences']+=freq
        stats['accepted_components_lost']+=max(accepted(prior)-accepted(current),0)*freq
        stats['accepted_components_gained']+=max(accepted(current)-accepted(prior),0)*freq
    if idx%500==0:print('registry comparison',idx,'/',len(surfaces),flush=True)
result=dict(method='Paired primary intervention surfaces with same code and snapshots; only _foreign_registry_alias and _ambiguous_short_alias disabled in counterfactual curation. Counts weighted by trial-intervention occurrence.',distinct_surfaces=len(surfaces),occurrences=sum(surfaces.values()),stats=dict(stats),changes=changes)
(E/'registry_coverage_counterfactual.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(dict(stats)),flush=True)
