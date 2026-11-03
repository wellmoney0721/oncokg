# 주장 검사 Codex 1차 — 지적별 판정과 수리 (2026-11-03 KST)

원문 `audit_evidence_claims/r1_report.md` · 재현 스크립트 `audit_evidence_claims/independent_*.py`. 판정: CHANGES REQUIRED.
지적은 모두 이 레포에서 다시 돌려 확인했고 전부 맞았다. 단어 모음 방식으로는 고칠 수 없어 절 단위
주어–관계–목적어 읽기로 다시 썼다(`src/claims.py`).

| # | 지적 | 판정 | 수리 |
| --- | --- | --- | --- |
| 1 | 관계 방향·양쪽 대상 미확인 (`EGFR acts on osimertinib` 등 5건) | 맞음 | 관계어 위치 기준 왼쪽·오른쪽 대상 묶음, 수동태 뒤집기, 종류 불일치 = relation_direction, 한쪽 없음 = relation_incomplete |
| 2 | 대명사가 다음 문장에서 주어를 잃음 | 맞음 | 대명사·생략 주어는 앞 절의 주어로, 앞이 없으면 no_antecedent |
| 3 | 같은 문장의 다른 대상 값(단계·상태·수)을 빌려 씀 | 맞음 | 단계는 바로 앞 대상, 숫자는 바로 뒤 대상의 근거로만, 상태·말은 절의 모든 대상을 함께 말하는 근거로만 |
| 4 | quoted() 두 단어 규칙이 부정·개발 주장을 세탁 | 맞음 | 규칙 삭제. 근거 문장 전체를 그대로 옮긴 줄만 통과 |
| 5 | `non-` 부정 사라짐 | 맞음 | 폐암 이름(non-small cell)만 먼저 지우고 `non`은 부정 |
| 6 | 대괄호·한국어로 검사 우회 | 맞음 | 출처 id 대괄호만 지움, 마크다운 링크는 글자만 남김, 영어가 아닌 글은 unreadable |
| 7 | 문법 단어로만 된 임상 주장, 작용 종류 무시 | 맞음 | treatment·all·cancer 등을 문법 목록에서 뺌, inhibit/activate는 근거의 작용 종류와 대조(대상-표적 근거에 작용 종류를 넣음) |
| 8 | phase 13·3b·긴 단위·"trials: 13" | 맞음 | 단계 숫자 전체 비교, 접미사 포함, 숫자는 위치와 무관하게 주인 대상의 근거로 |
| SF | 충실한 바꿔 말하기 10/30 걸림 | 맞음 | 별칭(Tagrisso) 허용, 상태 구문, 목록 제목 합치기, 명사형(target of, inhibitor, sponsor), 수동 `sponsored by` → 1/30 (`supports trials`, 엄격 의도) |
| SF | 짝 절의 데카르트 곱 | 맞음 | 두 쪽 모두 술어가 있으면 and/but에서 절을 나눔 |
| SF | 중복 제거가 다른 문장의 지적을 숨김 | 맞음 | (값, 문장)으로 중복 제거 |
| SF | 문서가 코드보다 많이 약속 | 맞음 | README 13번, docstring, 대시보드 06, 써 보기 3번 문구를 실제 범위로 |

추가로 찾은 것: 질의 연결이 "is a"를 isa(isatuximab)로 읽던 결함(1차 전에 수리), 대명사 "the target of"를 대명사로 잘못 읽음, "EGFR;"처럼 문장부호가 붙은 이름이 연결 안 됨.
시험 128개(1차 공격 33건 전부 grounded=False, 충실한 바꿔 말하기 16건 전부 통과).
