import json,sys
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'audit_evidence_claims/s4/faithful'
sys.path.insert(0,str(ROOT/'src'));from query import OncoKG
kg=OncoKG();kg.conn.execute('PRAGMA query_only=ON')
p=OUT/'historical_input_comparison.json'; data=json.loads(p.read_text(encoding='utf-8'))
for case in data['selected_original_false_rejections']:
    entities=kg.link_entities(case['question']);ev=kg.retrieve(kg.classify(case['question'],entities),entities)
    case['individual_output']=kg.verify_structured(case['input'],ev)
    assert case['individual_output']['verified']
p.write_text(json.dumps(data,indent=2),encoding='utf-8')
alias=json.loads((ROOT/'audit_evidence_claims/s4/identity/replay_s3/identity_attack_results.json').read_text(encoding='utf-8'))
for c in alias['cases']:
    if c['tag'] in ['constructor_company_collision:AstraZeneca!','constructor_company_collision:other_org_edge']:
        print(json.dumps(c,indent=2))
