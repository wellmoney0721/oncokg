import json
from pathlib import Path
root=Path.cwd();old=json.loads((root/'audit_evidence_claims/m15/attacks/alias_variants.json').read_text(encoding='utf8'));new=json.loads((root/'audit_evidence_claims/m16/attacks/alias_variants.json').read_text(encoding='utf8'))
a={r['text']:r for r in old};changes=[]
for r in new:
 p=a.get(r['text'],{})
 if (p.get('center'),bool(p.get('refused'))) !=(r.get('center'),bool(r.get('refused'))):changes.append({'text':r['text'],'old':p,'new':r})
out={'old_count':len(old),'new_count':len(new),'changes':changes}
(root/'audit_evidence_claims/m16/attacks/alias_variants_comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False,indent=2))
