"""Ingest layer: pull raw records from public sources and snapshot them to disk.

Design notes
------------
* Raw snapshots are written untouched. Every later stage reads from the snapshot,
  never from the network, so a result can be reproduced and a regression can be
  traced to either "the source changed" or "our logic changed" -- not both at once.
* Each snapshot carries a fetch timestamp and the query that produced it. The
  knowledge graph later attaches this to every edge as provenance.
* Two kinds of source are deliberately mixed:
    - reference vocabularies (Open Targets / ChEMBL): curated, stable identifiers
    - real-world free text (ClinicalTrials.gov): typos, trade names, abbreviations
  The whole point of the project is the gap between the two.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any

import requests

import config as C

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": C.USER_AGENT})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _snapshot(name: str, payload: Any, meta: dict) -> None:
    doc = {
        "_source": meta.get("source"),
        "_query": meta.get("query"),
        "_fetched_at": _now(),
        "_record_count": len(payload) if isinstance(payload, list) else 1,
        "data": payload,
    }
    path = C.RAW / f"{name}.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  -> {path.relative_to(C.ROOT)}  ({doc['_record_count']} records)")


# --------------------------------------------------------------------------- #
# Open Targets
# --------------------------------------------------------------------------- #
def _gql(query: str, variables: dict) -> dict:
    for attempt in range(4):
        r = SESSION.post(
            C.OPENTARGETS_GQL,
            json={"query": query, "variables": variables},
            timeout=C.HTTP_TIMEOUT,
        )
        if r.status_code == 200:
            body = r.json()
            if "errors" in body:
                raise RuntimeError(f"GraphQL error: {json.dumps(body['errors'])[:500]}")
            return body["data"]
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
    raise RuntimeError("Open Targets: retries exhausted")


Q_DISEASE = """
query D($id: String!) {
  disease(efoId: $id) {
    id
    name
    description
    synonyms { relation terms }
    dbXRefs
    therapeuticAreas { id name }
  }
}
"""

Q_DRUGS = """
query Drugs($id: String!) {
  disease(efoId: $id) {
    drugAndClinicalCandidates {
      count
      rows {
        maxClinicalStage
        drug {
          id
          name
          drugType
          description
          maximumClinicalStage
          synonyms { label source }
          tradeNames { label source }
          crossReferences { source ids }
          parentMolecule { id name }
          mechanismsOfAction {
            rows { actionType mechanismOfAction targetName targets { id approvedSymbol } }
          }
        }
      }
    }
  }
}
"""

Q_TARGETS = """
query Targets($id: String!, $size: Int!) {
  disease(efoId: $id) {
    associatedTargets(page: {index: 0, size: $size}) {
      count
      rows {
        score
        target {
          id
          approvedSymbol
          approvedName
          biotype
          synonyms { label source }
          symbolSynonyms { label source }
          nameSynonyms { label source }
          obsoleteSymbols { label source }
          proteinIds { id source }
        }
      }
    }
  }
}
"""


def fetch_disease() -> dict:
    print("[1/4] Open Targets - disease record")
    data = _gql(Q_DISEASE, {"id": C.DISEASE_ID})
    rec = data["disease"]
    if rec is None:
        raise RuntimeError(f"disease {C.DISEASE_ID} not found in Open Targets")
    _snapshot("disease", rec, {"source": "opentargets", "query": C.DISEASE_ID})
    return rec


def fetch_drugs() -> list[dict]:
    print("[2/4] Open Targets - drug & clinical candidates")
    data = _gql(Q_DRUGS, {"id": C.DISEASE_ID})
    rows = data["disease"]["drugAndClinicalCandidates"]["rows"]
    _snapshot("drugs", rows, {"source": "opentargets", "query": C.DISEASE_ID})
    return rows


def fetch_targets() -> list[dict]:
    print("[3/4] Open Targets - associated targets")
    data = _gql(Q_TARGETS, {"id": C.DISEASE_ID, "size": C.MAX_TARGETS})
    rows = data["disease"]["associatedTargets"]["rows"]
    _snapshot("targets", rows, {"source": "opentargets", "query": C.DISEASE_ID})
    return rows


# --------------------------------------------------------------------------- #
# ClinicalTrials.gov
# --------------------------------------------------------------------------- #
CTGOV_FIELDS = ",".join([
    "protocolSection.identificationModule.nctId",
    "protocolSection.identificationModule.briefTitle",
    "protocolSection.identificationModule.officialTitle",
    "protocolSection.statusModule.overallStatus",
    "protocolSection.statusModule.startDateStruct",
    "protocolSection.statusModule.whyStopped",
    "protocolSection.sponsorCollaboratorsModule",
    "protocolSection.conditionsModule.conditions",
    "protocolSection.designModule.phases",
    "protocolSection.designModule.studyType",
    "protocolSection.designModule.enrollmentInfo",
    "protocolSection.armsInterventionsModule.interventions",
])


def fetch_trials() -> list[dict]:
    print("[4/4] ClinicalTrials.gov - interventional studies")
    out: list[dict] = []
    token = None
    page = 0
    while len(out) < C.MAX_TRIALS:
        params = {
            "query.cond": C.CTGOV_CONDITION_QUERY,
            "filter.advanced": "AREA[StudyType]INTERVENTIONAL",
            "pageSize": C.CTGOV_PAGE_SIZE,
            "fields": CTGOV_FIELDS,
        }
        if token:
            params["pageToken"] = token
        r = SESSION.get(C.CTGOV_STUDIES, params=params, timeout=C.HTTP_TIMEOUT)
        r.raise_for_status()
        body = r.json()
        studies = body.get("studies", [])
        out.extend(studies)
        page += 1
        print(f"      page {page}: +{len(studies)} (total {len(out)})")
        token = body.get("nextPageToken")
        if not token or not studies:
            break
    out = out[: C.MAX_TRIALS]
    _snapshot("trials", out, {"source": "clinicaltrials.gov",
                              "query": C.CTGOV_CONDITION_QUERY})
    return out


def main() -> None:
    print(f"Disease scope: {C.DISEASE_LABEL} ({C.DISEASE_ID})\n")
    fetch_disease()
    fetch_drugs()
    fetch_targets()
    fetch_trials()
    print("\nIngest complete.")


if __name__ == "__main__":
    main()
