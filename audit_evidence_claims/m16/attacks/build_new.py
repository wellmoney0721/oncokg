from pathlib import Path
import ast,json,hashlib
out=Path(__file__).resolve().parent;root=out.parents[2]
cases=['trastuzumab I-124','I-124 trastuzumab','trastuzumab I124','I124 trastuzumab','trastuzumab i-124','i-124 trastuzumab','I-124-labelled trastuzumab','trastuzumab labelled with I-124','trastuzumab labeled with I-124','I-124-labeled trastuzumab','[I-124] trastuzumab','trastuzumab [I-124]','124I trastuzumab','trastuzumab 124I','124I-labelled trastuzumab','trastuzumab labelled with 124I','trastuzumab','trastuzumab I-124, osimertinib','osimertinib, trastuzumab I-124','vinblastine H3','vinblastine H-3','[H-3] vinblastine','vinblastine 3h','3hvinblastine','vinblastine','18 FDFO trastuzumab','18-FDFO trastuzumab','18 F DFO trastuzumab','18FDFO trastuzumab','osimertinib 80 mg','paclitaxel 2 cycles','cisplatin 75 mg/m2 day 1','13-cis retinoic acid','BKM-120NX','trastuzumab Ga-68','trastuzumab 68Ga','trastuzumab Ga68','trastuzumab Zr-89','trastuzumab 89Zr','trastuzumab I-131','trastuzumab 131I','I-124-labelled trastuzumab, osimertinib']
s=(root/'audit_evidence_claims/m15/attacks/targeted_probe.py').read_text(encoding='utf8')
s=s.replace("'m15_previous'","'m16_previous'")
start=s.index('cases = ');end=s.index('\nrows=[]',start);s=s[:start]+'cases = '+repr(cases)+s[end:]
s=s.replace('targeted_results.json','new_results.json').replace('targeted_summary.json','new_summary.json')
(out/'new_probe.py').write_text(s,encoding='utf8')
s=(root/'audit_evidence_claims/m15/attacks/targeted_http.py').read_text(encoding='utf8')
start=s.index('CASES = ');end=s.index('\n\n',start);s=s[:start]+'CASES = '+repr(cases)+s[end:]
s=s.replace('PORT = 8945','PORT = 8970').replace('targeted_','new_')
(out/'new_http.py').write_text(s,encoding='utf8')
(out/'new_cases.json').write_text(json.dumps(cases,indent=2),encoding='utf8')
