import ast,json,sys,sqlite3,threading,urllib.request,urllib.error,subprocess,textwrap,types,time
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
from app import Engine,make_handler
from http.server import ThreadingHTTPServer
import textrules as T
OUT=Path('audit_evidence_claims/m5')
oldsource=subprocess.check_output(['git','show','bfcb83d:src/query.py']).decode('utf-8')
method=next(n for n in ast.walk(ast.parse(oldsource)) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
oldglobals=dict(query.__dict__)
exec(compile(textwrap.dedent(ast.get_source_segment(oldsource,method)),'bfcb83d:src/query.py','exec'),oldglobals)
oldmethod=oldglobals['link_entities']
E=Engine(); old=Engine(); old.kg.link_entities=types.MethodType(oldmethod,old.kg)
servers=[]
def post(index,path,text):
    text=text.strip()
    if len(text)>500:return {'status':400,'body':{'error':'input is longer than 500 characters'}}
    e=[E,old][index]
    return {'status':200,'body':getattr(e,path)(text)}

def map_summary(r):
    return {'status':r['status'],'body':{k:v for k,v in r['body'].items() if k!='groups'},'group_totals':[(g['rel'],g['dir'],g.get('role'),g['total']) for g in r['body'].get('groups',[])]}
inputs=[]
for name in ['names_probe.py','names_extra_probe.py','names_product_probe.py']:
    source=Path('audit_evidence_claims/m1',name).read_text(encoding='utf-8-sig')
    for n in ast.walk(ast.parse(source)):
        if isinstance(n,ast.List):
            try:vals=ast.literal_eval(n)
            except (ValueError,TypeError):continue
            if vals and all(isinstance(x,str) for x in vals) and len(vals)>5:
                inputs+=vals
inputs+=['MET','osimertinib EGFR','EGFR osimertinib','unknown-m1-entity','  OsImErTiNiB\n','x'*500+' osimertinib','osimertinib '+'x'*600]
inputs=list(dict.fromkeys(inputs))
extra=['[89Zr] trastuzumab and osimertinib','osimertinib and [89Zr] trastuzumab','osimertinib and ABP 215','ABP 215 and osimertinib','Which trials evaluate osimertinib and ABP 215?','Which trials evaluate osimertinib and [89Zr] trastuzumab?','Which drugs act on EGFR and what is ABP 215?','bevacizumab — awwb','bevacizumab － awwb','[89Zr] trastuzumab EGFR','89Zr - trastuzumab osimertinib','Mvasi and bevacizumab','Which companies sponsor osimertinib and generic version of doxorubicin?','Which drugs act on EGFR besides ABP 215?']
results=[]
try:
    for s in inputs:
        results.append({'input':s,'linker':E.kg.link_entities(s),'old_linker':old.kg.link_entities(s),'map':map_summary(post(0,'explore',s)),'resolver':[{'tier':c['tier'],'drug_id':c.get('drug_id')} for c in E.resolve(s)['components']]})
    regress=[]
    for s in extra:
        cur=post(0,'ask',s); prior=post(1,'ask',s)
        regress.append({'input':s,'distinct_predicate':T.is_distinct_product(s),'tracer_predicate':T.is_radiotracer(s),'current_map':map_summary(post(0,'explore',s)),'current_ask':cur,'baseline_ask':prior})
    OUT.joinpath('names_reproduction_results.json').write_text(json.dumps({'reproductions':results,'regression_probes':regress,'multi_company_aliases':{k:v for k,v in E.kg.companies.items() if len(v)>1}},ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'reproductions':len(results),'regression_probes':[{'input':r['input'],'current_entities':r['current_ask']['body'].get('entities'),'current_evidence':len(r['current_ask']['body'].get('evidence',[])),'old_entities':r['baseline_ask']['body'].get('entities'),'old_evidence':len(r['baseline_ask']['body'].get('evidence',[])),'current_center':r['current_map']['body'].get('center')} for r in regress]},ensure_ascii=False,indent=2))
finally:
    for server,worker in servers:server.shutdown();server.server_close();worker.join(3)
    E.kg.conn.close();old.kg.conn.close()

