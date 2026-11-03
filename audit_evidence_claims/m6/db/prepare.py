"""Copy prior audit reproducers into m6/db, changing only repository-root depth."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
names = ['db_recheck.py', 'db_missing_sponsor_count.py', 'db_role_fallback.py',
         'db_score_fixture.py', 'db_numeric_fixture.py', 'db_snapshot.py',
         'db_assertions.py']
manifest = []
for name in names:
    source = ROOT / 'audit_evidence_claims/m5' / name
    original = source.read_text(encoding='utf-8')
    adapted = original.replace('.parents[2]', '.parents[3]')
    (OUT / name).write_text(adapted, encoding='utf-8')
    manifest.append({'source': str(source.relative_to(ROOT)), 'destination': name,
                     'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'adaptation': 'Path(__file__).resolve().parents[2] -> parents[3] only' if adapted != original else 'none'})
(OUT / 'replay_sources.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest, indent=2))
