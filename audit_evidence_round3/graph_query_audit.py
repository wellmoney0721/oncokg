import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys, json, sqlite3, copy, subprocess, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'audit_evidence_round3'
sys.path.insert(0,str(ROOT/'src'))
import normalize as N, graph as G, query as Q

def dump(name,x):
    (OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')

db=OUT/'graph_copy.sqlite'
src=sqlite3.connect('file:'+str(ROOT/'data/processed/oncokg.sqlite').replace('\\','/')+'?mode=ro',uri=True)
dest=sqlite3.connect(db); src.backup(dest); src.close(); dest.close()
resolved=OUT/'graph_resolved.json'
shutil.copy2(ROOT/'data/processed/resolved.json',resolved)
con=sqlite3.connect(db); con.row_factory=sqlite3.Row
def rows(sql,params=()): return [dict(r) for r in con.execute(sql,params)]
checks={
 'live_nodes':rows('SELECT type,COUNT(*) n FROM node WHERE retired_at IS NULL GROUP BY type'),
 'live_edges':rows('SELECT rel,COUNT(*) n FROM edge WHERE retired_at IS NULL GROUP BY rel'),
 'null_provenance':rows('SELECT rel,COUNT(*) n,SUM(source_record IS NULL) null_records,SUM(source_fetched_at IS NULL) null_fetch_times,SUM(tier IS NULL) null_tiers FROM edge WHERE retired_at IS NULL GROUP BY rel'),
 'gsk_nodes':rows("SELECT * FROM node WHERE id IN ('ORG:gsk','ORG:glaxosmithkline')"),
 'gsk_edges':rows("SELECT * FROM edge WHERE rel='PARENT_OF' AND (src='ORG:gsk' OR dst='ORG:glaxosmithkline')"),
 'live_edges_with_retired_endpoint':rows('SELECT COUNT(*) n FROM edge e JOIN node s ON s.id=e.src JOIN node d ON d.id=e.dst WHERE e.retired_at IS NULL AND (s.retired_at IS NOT NULL OR d.retired_at IS NOT NULL)'),
 'live_edges_missing_endpoint':rows('SELECT COUNT(*) n FROM edge e LEFT JOIN node s ON s.id=e.src LEFT JOIN node d ON d.id=e.dst WHERE e.retired_at IS NULL AND (s.id IS NULL OR d.id IS NULL)'),
 'derived_missing_evidence':rows("SELECT COUNT(*) n FROM edge WHERE rel='SPONSORS_TRIAL_OF' AND retired_at IS NULL AND (json_array_length(json_extract(props,'$.evidence_trials_all'))<>json_extract(props,'$.evidence_trials') OR json_extract(props,'$.evidence_trials_all') IS NULL)"),
 'target_props':rows("SELECT * FROM node WHERE id='ENSG00000146648'"),
}
con.close()
dump('graph_snapshot_checks.json', checks)

names=['GSK','GlaxoSmithKline','GlaxoSmithKline plc','Daiichi Jitsugyo Co., Ltd.','Daiichi Sankyo','Daiichi Pharmaceutical','Millennium Management','Bayerische Motoren Werke AG','GSK Biologicals','GlaxoSmithKline Biologicals','Hoffmann-La Roche','F. Hoffmann-La Roche Ltd.','Merck & Co., Inc.','Merck KGaA','Juno Therapeutics','Loxo Oncology','Array BioPharma','BeOne Medicines','BeiGene','Hengrui Medicine','Xiuning Le','Dr Xiuning Le','Charles MD','Hospital Dr','MD Anderson Cancer Center']
dump('graph_company_probes.json',[{'name':name,'normalized':N.normalize_company(name),'looks_like_person':N.looks_like_person(name)} for name in names])

kg=Q.OncoKG(db,resolved)
questions=['Which companies are developing osimertinib?','Is pembrolizumab safe in patients with autoimmune disease?','What is the capital of France?','Which companies are developing EGFR inhibitors?','What is GSK running in NSCLC?','What does osimertinib target?']
answers=[kg.answer(q,use_llm=False).to_dict() for q in questions]
dump('query_hostile_answers.json',answers)
evidence=[Q.Evidence('OSIMERTINIB acts on EGFR (inhibitor). AstraZeneca sponsors 47 trials.', 'e1','ACTS_ON','test','NCT02303977','2026-11-03',1.0,detail={'rate':'47.5%'})]
texts=['osimertinib cures cancer.','osimertinib is safe in autoimmune disease.','AstraZeneca has discontinued osimertinib.','osimertinib has a 47.5% response rate.','osimertinib has a 47% response rate.','osimertinib causes death in 47.5% of patients.','osimertinib has a 0.475 response rate.','osimertinib works in 47.5 percent of patients.','osimertinib works in ⅔ of patients.','osimertinib works in 1e6 patients.','Osimertinib and aspirin cure cancer.','aspirin is safe.','xyzabumab cures cancer.','novelumab cures cancer.','osimertinib was tested by astra.','No EGFR activity was observed.','osimertinib is first-line therapy.','osimertinib has a -47.5% response rate.']
dump('query_groundedness_probes.json',{'api_key_present':bool(os.environ.get('ANTHROPIC_API_KEY')),'evidence':evidence[0].__dict__,'probes':[{'text':t,'checks':kg.check_groundedness(t,evidence,[])} for t in texts]})
kg.conn.close()

# Minimal isolated snapshot for disappearance and re-addition.
r=json.loads(resolved.read_text(encoding='utf8'))
mini=copy.deepcopy(r)
mini['trials']=[next(t for t in r['trials'] if t.get('lead_sponsor') and any(c['tier'] in N.ACCEPTED_TIERS and c.get('drug_id') for iv in t['interventions'] for c in iv['components']))]
mini['targets']=[]
ids={c['drug_id'] for iv in mini['trials'][0]['interventions'] for c in iv['components'] if c.get('drug_id')}
mini['dictionary']['drugs']={k:v for k,v in mini['dictionary']['drugs'].items() if k in ids}
micro=OUT/'graph_micro.sqlite'
if micro.exists(): micro.unlink()
states=[]
for buildid, trials in [('one',mini['trials']),('removed',[]),('restored',mini['trials']),('unchanged',mini['trials'])]:
    v=copy.deepcopy(mini); v['trials']=trials
    states.append(G.build(v,db_path=micro,build_id=buildid))
dump('graph_liveness_probes.json',states)

# Source metadata changes are silently overwritten and not recorded in history.
hist=sqlite3.connect(':memory:'); hist.executescript(G.SCHEMA)
for bid,source,fetch in [('a','source A','2025-01-01'),('b','source B','2026-01-01')]:
    w=G.GraphWriter(hist,bid,bid)
    w.node('x','Drug','x'); w.node('y','Target','y')
    w.edge('x','y','ACTS_ON',source=source,source_record='same-record',fetched_at=fetch)
dump('graph_provenance_history_probe.json',{'edge':[dict(zip([d[0] for d in cur.description],row)) for cur in [hist.execute('SELECT * FROM edge')] for row in cur.fetchall()], 'changes':[dict(zip([d[0] for d in cur.description],row)) for cur in [hist.execute('SELECT * FROM edge_change')] for row in cur.fetchall()], 'last_build_stats':w.stats})
print('graph/query audit evidence written')
