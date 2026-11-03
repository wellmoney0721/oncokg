"""M4 linker attacks; current data read-only; exact pre-repair globals retained."""
import ast,json,re,sqlite3,subprocess,sys,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
import textrules as T
from app import Engine
OUT=Path('audit_evidence_claims/m5')

def baseline(rev):
    src=subprocess.check_output(['git','show',rev+':src/query.py']).decode('utf8')
    tree=ast.parse(src)
    method=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
    ns=dict(query.__dict__)
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_JOINERS' for t in n.targets):
            ns['_JOINERS']=ast.literal_eval(n.value)
    exec(compile(textwrap.dedent(ast.get_source_segment(src,method)),rev+':src/query.py','exec'),ns)
    e=Engine();e.kg.link_entities=types.MethodType(ns['link_entities'],e.kg)
    return e

cur=Engine(); old=baseline('574097f')
# Counterfactual: same new refusal algorithm, only the matched-span exclusion removed.
relink=Engine()
src=Path('src/query.py').read_text(encoding='utf8')
tree=ast.parse(src);method=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
body=textwrap.dedent(ast.get_source_segment(src,method)).replace('(refused | matched)','refused')
ns=dict(query.__dict__);exec(compile(body,'HEAD-linker-with-relink','exec'),ns)
relink.kg.link_entities=types.MethodType(ns['link_entities'],relink.kg)
for e in (cur,old,relink):
    e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row

inputs=[
 'generic version of the commercially available monoclonal antibody bevacizumab',
 'generic version of the drug bevacizumab',
 'generic version of the anticancer drug bevacizumab',
 'bevacizumab supplied as a newly developed generic version',
 'bevacizumab with a nanoparticle albumin bound formulation',
 'paclitaxel formulated with nanoparticles that are albumin bound',
 'liposomal formulation of doxorubicin',
 'liposomal formulation containing the drug doxorubicin',
 'biosimilar version of bevacizumab',
 'biosimilar to the monoclonal antibody bevacizumab',
 'pegylated formulation of interferon alfa-2b',
 '[89Zr] labelled monoclonal antibody trastuzumab',
 '[89Zr] radiolabelled version of trastuzumab',
 'osimertinib with [89Zr] trastuzumab',
 'generic version of bevacizumab and generic version of osimertinib',
 'generic version of bevacizumab with generic version of osimertinib',
 'liposomal doxorubicin and biosimilar bevacizumab',
 'liposomal formulation of doxorubicin and biosimilar version of bevacizumab',
 'bevacizumab generic version osimertinib',
 'bevacizumab with generic version of osimertinib',
 'osimertinib with generic version of bevacizumab',
 'bevacizumab a generic version of osimertinib',
 'generic version of erlotinib hydrochloride',
 'generic version of Paclitaxel conjugate with poly-l-glutamic acid',
 'Paclitaxel conjugate with poly-l-glutamic acid',
 'EGFR generic version of bevacizumab',
 'EGFR biosimilar bevacizumab',
 'biosimilar bevacizumab EGFR',
 'EGFR liposomal formulation of doxorubicin',
 'AstraZeneca generic version of bevacizumab',
 'AstraZeneca biosimilar bevacizumab',
 'biosimilar bevacizumab AstraZeneca',
 'Roche generic version of bevacizumab',
 'generic version of Roche bevacizumab',
 'osimertinib with biosimilar version of bevacizumab',
 'osimertinib and biosimilar version of bevacizumab',
 'Which trials evaluate liposomal formulation of doxorubicin?',
 'Which trials evaluate biosimilar version of bevacizumab?',
 'Which trials evaluate [89Zr] labelled monoclonal antibody trastuzumab?',
 'Which trials evaluate generic version of the commercially available monoclonal antibody bevacizumab?',
 'Which trials evaluate osimertinib and biosimilar version of bevacizumab?',
 'Which companies sponsor generic version of erlotinib hydrochloride?',
 'What targets does erlotinib hydrochloride act on?',
 'What trials evaluate erlotinib hydrochloride and erlotinib?',
 'Which drugs act on EGFR and which companies sponsor generic version of bevacizumab?',
]

def result(e,s):
    m=e.explore(s)
    return {'linker':e.kg.link_entities(s),'map':{k:v for k,v in m.items() if k!='groups'},'answer':e.ask(s)}

rows=[]
for s in inputs:
    rows.append({'input':s,'distinct':T.is_distinct_product(s),'tracer':T.is_radiotracer(s),'resolver':cur.resolve(s),
                 'current':result(cur,s),'previous':result(old,s),'relink':result(relink,s)})
page=Path('web/try.html').read_text(encoding='utf8')
demo=json.loads(re.search(r'const EX2 = (\[.*?\]);',page,re.S).group(1))
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
for n in ast.walk(main):
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='questions' for t in n.targets):
        demo+=ast.literal_eval(n.value.values[-1])
varied=list(dict.fromkeys(demo+[
 'Which trials evaluate '+x+'?' for x in ['erlotinib hydrochloride','osimertinib mesylate','cisplatin','Paclitaxel conjugate with poly-l-glutamic acid','AstraZeneca','EGFR','MET','Roche','NSCLC','non-small cell lung cancer']
]+[
 'Who sponsors '+x+'?' for x in ['erlotinib hydrochloride','osimertinib mesylate','bevacizumab','Tagrisso','Paclitaxel conjugate with poly-l-glutamic acid']
]+[
 'What targets does '+x+' act on?' for x in ['erlotinib hydrochloride','osimertinib mesylate','bevacizumab','Tagrisso','Paclitaxel conjugate with poly-l-glutamic acid']
]+[
 'Which drugs act on EGFR?', 'Which drugs act on ALK?', 'Which drugs act on KRAS?',
 'Tell me about AstraZeneca', 'Tell me about National Cancer Institute',
 'What trials evaluate erlotinib hydrochloride and osimertinib?',
 'What trials evaluate osimertinib and erlotinib hydrochloride?',
 'Which companies sponsor osimertinib and erlotinib hydrochloride?',
 'Which companies sponsor erlotinib hydrochloride and osimertinib?',
 'Which drugs act on EGFR and ALK?', 'Which trials evaluate osimertinib EGFR?',
]))
qa=[]
for s in varied:
    a,b,c=cur.ask(s),old.ask(s),relink.ask(s)
    qa.append({'input':s,'demo':s in demo,'current':a,'previous':b,'relink':c,
               'same_previous':a==b,'same_relink':a==c})
aliases=[]
for k,hits in cur.dic['index'].items():
    if len({h['drug_id'] for h in hits})!=1:continue
    h=hits[0]
    if re.search(r'\s',h['alias']):
        s=h['alias']
        a,b,c=cur.kg.link_entities(s),old.kg.link_entities(s),relink.kg.link_entities(s)
        aliases.append({'input':s,'stored_hit':h,'current':a,'previous':b,'relink':c})
out={'baseline':'574097f exact link_entities and exact _JOINERS; other code/data current',
     'counterfactual':'HEAD only removes matched indexes from overlap exclusion',
     'cases':rows,'qa':qa,'multi_token_aliases':aliases}
OUT.joinpath('names_attack.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
    print(json.dumps({'input':r['input'],'current':r['current']['linker'],'center':r['current']['map'].get('center',{}).get('id'),'prior_center':r['previous']['map'].get('center',{}).get('id'),'evidence':len(r['current']['answer']['evidence']),'resolver':[(c['tier'],c.get('drug_id')) for c in r['resolver']['components']]},ensure_ascii=False))
print('QA',len(qa),'changed',sum(not r['same_previous'] for r in qa),'relink_changed',sum(not r['same_relink'] for r in qa))
print('ALIASES',len(aliases),'changed',sum(r['current']!=r['previous'] for r in aliases),'relink_changed',sum(r['current']!=r['relink'] for r in aliases))
for e in (cur,old,relink):e.kg.conn.close()
