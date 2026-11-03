# Codex 감사 2라운드 — 지적별 재현 결과 (2026-11-03 KST)

원문: `codex_report.txt`, 증거: `audit_evidence_20261103/`.
Codex 보고를 그대로 믿지 않고, 아래 각 줄을 이 레포에서 직접 다시 돌려 확인했다.
"맞음" = 내가 재현함. "부분" = 결론은 맞지만 세부가 틀림. "틀림" = 재현 안 됨.

## 막는 결함(BLOCKERS)

| # | 지적 | 판정 | 내가 본 것 |
| --- | --- | --- | --- |
| B1 | 관계 이름을 바꾼 뒤 조회·대시보드가 아직 `DEVELOPS` 를 찾음 | 맞음 | `src/query.py:206,213,286,294`, `src/make_dashboard_data.py:57,82,86`. `query.py "Which companies are developing osimertinib?"` → refusal(근거 없음) |
| B2 | `Merck & Co., Inc.` 의 모회사가 Merck KGaA 로 붙음 | 맞음 | 표준 키가 `merck` 로 줄어 `merckkgaa`.startswith("merck") 에 걸림(`src/normalize.py:926`). BeiGene→BeOne 은 이름 변경인데 `PARENT_OF` 로 표현됨 |
| B3 | 파생 관계를 은퇴 처리보다 먼저 만들어, 빠진 시험의 파생 엣지가 한 번 더 살아남음 | 맞음 | `src/graph.py` 파생 쿼리(308행대) 뒤에 `retire_unseen()`(333행) |
| B4 | 근거 검사가 지어낸 내용을 통과시킴 | 맞음 | 직접 실행: `xyzabumab cures cancer.` 통과, 근거 `47.5%` 에 대해 `47%` 통과·`47.5%` 거부, `forty-seven percent` 통과. 원인 = `[a-z0-9]+` 토큰화가 `47.5` 를 `47`·`5` 로 쪼갬, 소문자 고유명사는 검사 안 함 |
| B5 | 라벨 정정 `--check` 가 PENDING 이 있어도 "all corrections are already in the labels" 를 찍고 0 종료 | 맞음 | `src/apply_label_corrections.py:83~85,99~101` — check 모드에선 `applied` 가 늘지 않음. 행 대조도 id·verdict 만 봄 |

## 라벨 재채점

| 행 | 판정 | 근거 |
| --- | --- | --- |
| test `CC-486 → AZACITIDINE` | 맞음 | 이 레포 기준(Abraxane 정정 = "별도 승인·대체 불가 제품은 다른 제품")을 그대로 적용하면 경구 아자시티딘(Onureg)도 별도 제품 |
| test `NanoPac → PACLITAXEL` | 맞음 | 같은 기준 |
| postfix `Nab-paclitaxel → PACLITAXEL` | 맞음 | test 정정 3번(Abraxane)과 같은 오류인데 postfix 에선 correct 로 남아 있음 = 기준 불일치 |
| 정정 ID22 사유 | 맞음 | NCT07318883 은 HLX07 대 위약 시험이고 "Paclitaxel or Nab-Paclitaxel" 은 선택 가능한 병용 약 — "두 제형 비교가 핵심"이라는 사유는 틀림. 판정(incorrect)은 그대로 맞음 |

결과: 원시 정밀도 test 105/115 = 91.3% → **103/115 = 89.6%**, postfix 37/38 → **36/38 = 94.7%**(Codex 계산, 수리 뒤 다시 확인 예정).

## 도메인 오류 — 직접 돌린 결과

| 입력 | 결과 | 판정 |
| --- | --- | --- |
| `tobramycin` | ALIAS → DEXAMETHASONE | 맞음 |
| `corticosteroid` | FUZZY_AUTO → **PREDNISONE**(CHEMBL635) | **부분** — 클래스 용어가 자동 해석되는 결함은 맞지만 Codex 가 적은 HYDROCORTISONE 은 틀림 |
| `Mvasi` · `Alymsys` · `Zirabev` | ALIAS → 베바시주맙 | 맞음(바이오시밀러가 오리지널로 접힘) |
| `cemiplimab-rwlc` | BLOCKED_DISTINCT_PRODUCT | 맞음(오리지널을 막음) |
| `liposomal doxorubicin` / `… and cisplatin` | 혼자면 막힘, `and cisplatin` 을 붙이면 EXACT doxorubicin | 맞음 |
| `prednisolone phosphate` | SALT_STRIPPED → PREDNISOLONE | 맞음(에스테르 전구약물을 염처럼 벗김) |
| `pembrolizumab antibody` | BLOCKED_CLASS_TERM | 맞음(실제 약을 막음) |
| `mab inhibitor` | UNRESOLVED(사유 코드 없음) | **부분** — 잘못된 엣지는 안 생김. 결함은 사유 코드가 없다는 것뿐 |
| `No pembrolizumab` | CONTAINED_ALIAS → 펨브롤리주맙 | 맞음(부정을 노출로 받아들임) |

## 통계 지적

| 지적 | 판정 |
| --- | --- |
| 원시 105/115 · Wilson 84.7~95.2% 재현 | 맞음(감사도 같은 값) |
| 현재 모집단 가중치 × 예전 라벨을 섞음 | 받아들임 — 수리 때 같은 시점 기준으로 맞춤 |
| 계층별 Wilson 끝값 가중합은 보정된 95% 구간이 아님 · 부트스트랩 94.2~99.0% | 받아들임 — 둘 다 싣고, 부트스트랩이 100% 계층의 오류를 못 본다는 한계도 적음 |
| 이월 계층 기여 1.0%p | 받아들임 — README 에 수치로 |

## 과장 문장

| 문장 | 판정 |
| --- | --- |
| "모든 엣지가 출처 레코드·해석 계층을 가진다" | 맞음 — 살아 있는 엣지 중 `source_record` 빈칸 3,187(SPONSORS_TRIAL_OF 전부), `tier` 빈칸 10,368 |
| "사실은 어느 쪽이든 같다" | 맞음 — 검사기가 강제하지 않음 |
| "변하지 않은 원천에서 다시 만들면 변경 0" | 맞음 — B3 때문에 원천이 빠지면 성립 안 함 |
| "four other molecules" 인데 셋 | 확인 필요(수리 때 README 행 대조) |
| "other 62 re-scored rows agreed" vs 62건 중 5건 불일치 | 확인 필요 |
| "most recent 3,000" — 정렬 지정 없음 | 확인 필요 |

## Codex 가 놓친 것(내가 찾은 것)

- `src/graph.py` 주석은 비산업 스폰서 비율을 **60.6%** 라 적고 README·산출물은 **58.8%** 다.
- 같은 주석이 "no confidence is manufactured"라 하는데 파생 엣지는 `confidence=1.0` 으로 박혀 있다.

## Codex 가 틀린 것

- `corticosteroid` 의 해석 대상(HYDROCORTISONE 이라 함 → 실제는 PREDNISONE).
- `mab inhibitor` 를 "가드를 빠져나간다"고 했지만 결과는 UNRESOLVED 라 잘못된 주장은 생기지 않는다(사유 코드 누락만 결함).

## 수리 결과 (2026-11-03 KST)

위 "맞음"·"부분" 항목은 전부 고쳤다. 커밋 8d8be5b · ca27e4b, 회귀 시험 `tests/test_audit_round2.py` 20개(전체 44개 통과).
연달아 두 번 재빌드했을 때 added/changed/retired = 0/0/0.

- 홀드아웃 헤드라인: 라벨 당시 원시 **103/115 = 89.6%**(Wilson 82.6~93.9). Codex 의 가중 96.0% 는 오늘의 모집단 가중치에
  예전 라벨을 섞은 값이라 싣지 않는다(라벨 당시 계층 모집단은 저장돼 있지 않다).
- 현재 파이프라인 test 99/99 는 수리가 겨냥한 행을 다시 채점한 것이라 홀드아웃 추정치가 아니다. 해석이 바뀐 25행은
  stale 로 빼서 `evaluation_frozen_test.json.stale_labels` 에 재라벨링 목록으로 남겼다.
- 수리하면서 새로 찾은 것: AACT 유래 동의어 2,595개(전체 28%)가 오염원이다(tobramycin 은 그 한 예). 318개를 규칙으로 뺐다.
  첫 시도는 너무 넓어 apatinib(=rivoceranib) 같은 맞는 이름까지 지웠다 → 큐레이션된 동의어·철자 유사도로 좁혔다.
  남은 거절 쪽 오류(terelizumab 등)는 README 남은 결함 11번.
- 수리 첫판이 망가뜨렸다가 되돌린 것: "Non-platinum chemotherapy: paclitaxel" 이 부정으로 막힘("non" 제외),
  PTX·DOC 3글자 약어 삭제(사전 전체에서 한 분자에만 걸리면 유지).
- 수리 전후 gold 문자열 411개 해석 비교: 28개 바뀜. 괄호 공유 버그(AZD8205→saruparib, IM→imatinib)·요법 약어(AC→doxorubicin,
  EP→etoposide)가 없어졌고, ABI-007·Genexol-PM·CC-486·NanoPac 은 별도 제품으로 막힌다.
