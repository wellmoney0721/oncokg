from pathlib import Path

old = Path('audit_evidence_claims/m3')
new = Path('audit_evidence_claims/m4')
names = ['ui_collect.py', 'ui_harness.js', 'ui_regressions.js',
         'ui_missing_sponsor_count.js', 'ui_demos.js', 'ui_demos_collect.py',
         'ui_m3_checks.js']
for name in names:
    text = old.joinpath(name).read_text(encoding='utf-8')
    text = text.replace('audit_evidence_claims/m3', 'audit_evidence_claims/m4')
    text = text.replace("browser:{browserInventory:'The browser access host is unavailable',nativeChromeSelection:'Computer Use was not approved to use Google Chrome',inputPerformed:false}",
                        "browser:{performed:false,scope:'Node VM only; no current browser claim'}")
    new.joinpath(name).write_text(text, encoding='utf-8')
    print(name)
