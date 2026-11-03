# Codex 감사 3라운드 — 지적별 재현 결과와 수리 (2026-11-03 KST)

원문: `codex_report_round3.txt`, 증거: `audit_evidence_round3/`(대용량 사본은 .gitignore).
각 줄은 이 레포에서 직접 다시 돌려 확인했다. 재현 스크립트는 지적마다 `tests/test_audit_round2.py` 의
round 3 시험으로 남겼다(전체 56개 통과).

## 막는 결함

| # | 지적 | 판정 | 내가 본 것 → 수리 |
| --- | --- | --- | --- |
| B1 | 백신 결함이 그래프에 남아 있음 | **맞음 — 내 잘못** | 2차 README 에 "더 재현되지 않는다"고 적었는데 짧은 문자열만 확인했다. 실제 50자 문자열은 TASADENOTUREV, 살아 있는 엣지 2개(두 번째는 다른 시험의 `Recombinant adenovirus- Ad/L523S` — 감사가 찾은 것 외에 내가 추가로 찾음). → 계열어 수식어 상한 40→90, 벡터 단어를 계열어로. 엣지 0 |
| B2 | 질의가 해석기 거절 규칙을 우회 | 맞음 | "What trials evaluate Mvasi?" → BEVACIZUMAB 연결. → 별도 제품 이름은 출처와 무관하게 색인에서 제거, 질문 속 별도 제품은 Refused |
| B3 | 사명 변경이 소유 관계로 남음(GSK, Schering-Plough) | 맞음 | GSK 의 키가 glaxosmithkline 인데 자기 자신 검사가 모회사 표시 이름("GSK"→gsk)과 비교. Schering-Plough 는 2009 합병의 법적 존속 회사. → 같은 회사 키 비교, Schering-Plough·Merck & Co 를 한 키(merckco)로 |
| B4 | 공표 수치 불일치(정리 후 별칭 9,750 · 회사 키 59 · 2차 불일치 3건이 홀드아웃) | 맞음 | 9,750 은 정리 전 목록 개수(정리 후 색인 키 7,610). 회사 키는 57(이번 수리 뒤 모회사 56 + 같은 회사 8). 2차 정정은 홀드아웃 2 + 수정 후 1. → 대시보드 타일·README 문구 정정 |

## 라벨

| 행 | 판정 | 비고 |
| --- | --- | --- |
| test 139 DN-101 (calcitriol) | 맞음 | 감사 스스로 "별도 승인은 아님"이라 했지만, 자기 코드로 개발된 별도 제형이라 NanoPac 과 같은 기준을 적용 |
| dev 180 Genexol-PM | 맞음 | 해석기는 2차부터 막고 있었는데 라벨만 남아 있었음 |
| dev 181 Pegylated liposomal doxorubicin | 맞음 | Doxil — 라벨이 대체 금지 |
| postfix 1 ABI-007 | 맞음 | Abraxane 코드. 단독 `ABI-007` 은 해석기도 PACLITAXEL 로 보내고 있었음 → 차단 |
| 정정 대조에 성분 열 누락 · 22번 메모에 옛 사유 | 맞음 | 성분까지 대조, 사유가 바뀌면 메모를 다시 맞춤(--check 도 이를 미반영으로 셈) |

결과: 라벨 당시 원시 test **102/115 = 88.7%**(81.6–93.3), dev **124/137 = 90.5%**, postfix **35/38 = 92.1%** — 감사 계산과 같음.

## 도메인

| 입력 | 수리 전 | 수리 후 |
| --- | --- | --- |
| `pembrolizumab-free regimen` | CLEANED → PEMBROLIZUMAB | BLOCKED_NEGATED (`free` 는 접미사가 아님, "X-free" 는 부재. "free base" 는 예외) |
| `[89Zr]pembrolizumab` | EXACT → PEMBROLIZUMAB | BLOCKED_CLASS_TERM(추적자) |
| `filgrastim-sndz`, `pegfilgrastim-jmdb`, `Pazenir` | 원래 분자 | BLOCKED_DISTINCT_PRODUCT |
| `Cemiplimab-RWLC` | 차단 | CEMIPLIMAB (대문자 FDA 접미사 인정, 제목형 단어는 스폰서 이름으로 계속 차단) |
| `dexamethasone sodium phosphate`, `etoposide phosphate` | 부모 분자 | UNRESOLVED (에스테르는 자기 기록의 정식명에만 맞음) |
| `ICE` | IFOSFAMIDE | UNRESOLVED (요법 약어는 출처 무관 제거) |
| `cisplatin + placebo to match pembrolizumab` | 전부 차단 | CISPLATIN 살림, 위약이 가리키는 약만 차단 |
| 근거 검사 `aspirin`, `1e6`, `⅔` | 통과 | 거부(사전에 있는 약 이름, 지수 표기, 유니코드 분수) |

수리 첫판이 기존 시험 하나를 깨뜨렸다: `Placebo to Match AZD9291, Osimertinib` 은 쉼표로 같은 약의 코드와 이름을 나열한 것인데,
위약 부분만 막자 Osimertinib 이 새어 나왔다. → 위약이 가리키는 약과 **같은 약**인 성분은 함께 막는 쪽으로 좁혔다.

## 통계 지적

| 지적 | 판정 |
| --- | --- |
| 낡은 행 제외가 오류 행을 전부 빼므로 살아남은 행 비율은 추정치가 아님 | 맞음 — README 표에서 현재 파이프라인 층화·구간 열을 지웠다. JSON 에는 남기되 "survivor-selected" 로 적었다 |
| 부트스트랩이 이미 알려진 오류가 만드는 상한(99.72%)보다 높게 나옴 | 맞음 — 같은 이유. 공표하지 않는다 |
| 이월 계층 0.88% | 맞음, README 그대로 |
| 수정 후 구간은 수리를 확인하지 못함 | 맞음 — 남은 결함 7번 문구를 "수리를 확인해 주지 않는다, 근거는 회귀 시험"으로 |

## 과장 문장

README 의 해당 문장을 고쳤다: 근거 검사가 잡는 범위(어휘 밖 비-INN 이름은 통과), 분절 잔여물(5글자 미만은 사라짐),
"조용히 캐시" 문단(산출물이 코드 버전을 기록하지 않음 → 남은 결함 14번), 질의 연결 문장, 백신 항목 경위.

## 감사가 틀린 것

재현하지 못한 지적은 없었다. 감사가 놓친 것은 하나다: `Recombinant adenovirus- Ad/L523S` 의 두 번째 백신 엣지(위 B1).

## 숫자 (수리 후 재빌드 두 번, 두 번째 변경 0)

노드 6,469 · 엣지 17,564 · SPONSORS_TRIAL_OF 3,176(산업 41.2%) · 커버리지 78.0%(4,936/6,329) · 큐레이션 모호 2,187→65, 정확 1,997→4,053 ·
품질 발견 1,800 · 낡은 행 test 26 / dev 33 / postfix 5.
