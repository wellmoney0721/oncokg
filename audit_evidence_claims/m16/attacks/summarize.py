from pathlib import Path
import json,sys
p=Path('audit_evidence_claims/m16/attacks')
for stem in ['focused','fresh','edge','targeted']:
 x=json.loads((p/(stem+'_results.json')).read_text(encoding='utf8'))
 rs=x['cases'] if isinstance(x,dict) else x
 print(stem,len(rs))
 if stem=='targeted':
  print(json.dumps([{'text':r['text'],'center':r['current']['map'].get('center',{}).get('label'),'refused':r['current']['map'].get('refused')} for r in rs],ensure_ascii=False,indent=2))
x=json.loads((p/'alias_variants.json').read_text(encoding='utf8'));print('aliases',len(x),len(set(r['key'] for r in x)),len([r for r in x if r['original_refused'] and r['center']]))
rs=json.loads((p/'new_results.json').read_text(encoding='utf8'))['cases']
for text in ['I-124-labelled trastuzumab','trastuzumab labelled with I-124','124I-labelled trastuzumab','trastuzumab labelled with 124I','vinblastine H3','18 F DFO trastuzumab']:
 r=next(r for r in rs if r['text']==text);c=r['current']
 print(json.dumps({'text':text,'center':c['map'].get('center'),'marked_calls':c['marked_calls'],'links':c['public_linker'],'whole_name':c['whole_name'],'resolver':c['resolver']},ensure_ascii=False,indent=2))
