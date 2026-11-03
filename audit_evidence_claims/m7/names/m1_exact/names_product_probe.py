import sys,json,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
import textrules as T
E=Engine(); out=[]
for text in ['bevacizumab - awwb','bevacizumab – awwb','89Zr - trastuzumab','[89Zr] trastuzumab','[89Zr]trastuzumab','ＡＶＡＳＴＩＮ','bevacizumab－awwb','bevacizumab—awwb']:
    rq=urllib.request.Request('http://127.0.0.1:8903/api/explore',data=json.dumps({'text':text}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(rq,timeout=10) as rp: er=json.load(rp)
    out.append({'input':text,'is_distinct_product':T.is_distinct_product(text),'is_radiotracer':T.is_radiotracer(text),'is_isotope_label_first':T.is_isotope_label(text.split()[0]),'linker':E.kg.link_entities(text),'resolver':[(r['tier'],r.get('drug_id')) for r in E.resolve(text)['components']],'http_200':{k:v for k,v in er.items() if k!='groups'}})
Path('audit_evidence_claims/m7/names/m1_exact/names_product_bypass.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(out,ensure_ascii=False,indent=2))
