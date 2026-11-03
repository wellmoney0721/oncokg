"""Project-wide configuration.

Scope is deliberately narrow: one disease area (NSCLC). A narrow slice lets the
entity-resolution and quality-control logic be evaluated honestly against a
hand-scored sample, which a broad-but-shallow crawl would not allow.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
WEB = ROOT / "web"

for _p in (RAW, PROCESSED, REPORTS, WEB):
    _p.mkdir(parents=True, exist_ok=True)

# --- disease scope -----------------------------------------------------------
# MONDO_0005233 = non-small cell lung carcinoma (Open Targets / MONDO)
DISEASE_ID = "MONDO_0005233"
DISEASE_LABEL = "non-small cell lung carcinoma"
CTGOV_CONDITION_QUERY = "non-small cell lung cancer"

# --- endpoints ---------------------------------------------------------------
OPENTARGETS_GQL = "https://api.platform.opentargets.org/api/v4/graphql"
CTGOV_STUDIES = "https://clinicaltrials.gov/api/v2/studies"

# --- ingest limits -----------------------------------------------------------
MAX_TARGETS = 300          # top associated targets by OT association score
MAX_TRIALS = 3000          # cap so a full rebuild stays under a few minutes
CTGOV_PAGE_SIZE = 1000

HTTP_TIMEOUT = 180
USER_AGENT = "oncokg-demo/0.1 (public-data portfolio project)"
