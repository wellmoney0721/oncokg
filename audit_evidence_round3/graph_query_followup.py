import os,sys,json,sqlite3,copy,subprocess,shutil
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/'audit_evidence_round3'
sys.path.insert(0,str(ROOT/'src'))
import query as Q,normalize as N,graph as G
def dump(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
r=json.loads((OUT/'graph_resolved.json').read_text(encoding='utf8'))
kg=Q.OncoKG(OUT/'graph_copy.sqlite',OUT/'graph_resolved.json')
cases=[]
for s in ['Mvasi','Alymsys','Zirabev','bevacizumab-awwb','platinum','tobramycin','corticosteroid','liposomal doxorubicin','NanoPac','CC-486']:
    cases.append({'surface':s,'pipeline_resolution':N.resolve_drug_string(s,r['dictionary'],list(r['dictionary']['index'])),'query_link':kg.link_entities(s),'query_answer':kg.answer('What trials evaluate '+s+'?',use_llm=False).to_dict()})
dump('query_resolution_bypass.json',cases)
c=kg.conn
actual={'parents':[dict(x) for x in c.execute("SELECT * FROM edge WHERE rel='PARENT_OF' AND retired_at IS NULL")],
 'known_person_typed_company':[dict(x) for x in c.execute("SELECT * FROM node WHERE label LIKE '%Xiuning%' OR id='ORG:xiuningle'")],
 'target_rows_original':r['targets'],
 'targets_with_metadata_lost':[dict(x) for x in c.execute("SELECT n.* FROM node n JOIN edge e ON e.src=n.id WHERE e.rel='ASSOCIATED_WITH' AND n.props='{}' AND e.retired_at IS NULL")],
 'duplicate_sponsor_role_rows':[t for t in r['trials'] if t.get('lead_sponsor') and any(x['key']==t['lead_sponsor']['key'] for x in t['collaborators'])]}
dump('graph_additional_snapshot_checks.json',actual)
kg.conn.close()

# Entire CLI in an isolated tree; each requested command writes only its copy.
cli=OUT/'query_cli'; (cli/'src').mkdir(parents=True,exist_ok=True); (cli/'data/processed').mkdir(parents=True,exist_ok=True)
for f in (ROOT/'src').glob('*.py'): shutil.copy2(f,cli/'src'/f.name)
shutil.copy2(OUT/'graph_copy.sqlite',cli/'data/processed/oncokg.sqlite')
shutil.copy2(OUT/'graph_resolved.json',cli/'data/processed/resolved.json')
commands=[]
for i,q in enumerate(['Which companies are developing osimertinib?','Is pembrolizumab safe in patients with autoimmune disease?','What is the capital of France?']):
    cmd=[sys.executable,'-B','src/query.py',q]
    cp=subprocess.run(cmd,cwd=cli,text=True,encoding='utf8',capture_output=True,env={**os.environ,'PYTHONIOENCODING':'utf-8'})
    (OUT/f'query_cli_{i}.stdout.txt').write_text(cp.stdout,encoding='utf8');(OUT/f'query_cli_{i}.stderr.txt').write_text(cp.stderr,encoding='utf8')
    commands.append({'command':cmd,'cwd':str(cli.relative_to(ROOT)),'exit_code':cp.returncode,'answer_json':json.loads((cli/'reports/query_examples.json').read_text(encoding='utf8'))})
dump('query_cli_execution.json',commands)

# Default build IDs collide within one second.
mini=copy.deepcopy(r); mini['targets']=[]; mini['trials']=[];mini['dictionary']['drugs']={}
p=OUT/'graph_default_buildid.sqlite'
if p.exists():p.unlink()
a=G.build(mini,db_path=p); b=G.build(mini,db_path=p)
cx=sqlite3.connect(p)
dump('graph_default_buildid_collision.json',{'first':a,'second':b,'build_row_count':cx.execute('SELECT count(*) FROM build').fetchone()[0]})
cx.close()
print('follow-up completed')
