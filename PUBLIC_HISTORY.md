# Commit hashes in the public copy

The working history of this project also held two files that are not part of
it: a private hand-over note with contact details (`HANDOFF.md`, and two copies
of it inside `audit_evidence_20261103/`) and a fact check of an unrelated
project (`KIWOOM_FACTCHECK.md`). They were removed from every commit before
publishing. Nothing else was changed except the first commit's message, which
named the note; every commit hash changed with them.

The audit reports and verdict files cite the original hashes. This table maps
each original hash to the commit that carries the same change here. The one
commit that only added the fact check is gone.

| original | public | subject |
| --- | --- | --- |
| `e79049b` | `5e564e4` | OncoKG: 인수인계 시점 그대로 (HANDOFF.md 포함) |
| `1b7e7f7` | (removed) | added the fact check of the unrelated project |
| `172063a` | `d304438` | Codex 독립 감사 2라운드 보고서(원문) |
| `73855d0` | `5000437` | Codex 2라운드 지적 직접 재현 결과 |
| `8d8be5b` | `62a817c` | Codex 2라운드 수리 1: 조회 관계 이름, 회사 지도, 그래프 은퇴 순서, 근거 검사, 라벨 정정 3건 |
| `ca27e4b` | `60f528d` | Codex 2라운드 수리 2: 약 이름 해석 도메인 오류, 평가 기준 시점 맞춤, 회귀 시험 20개 |
| `eb37439` | `d666169` | README 두 개를 2라운드 수리 뒤 산출물에 맞춤, 수리 결과 기록 |
| `da5e3ba` | `4b0190c` | 대시보드 헤드라인을 라벨 당시 홀드아웃 89.6% 로, 템플릿의 낡은 문장 정정 |
| `fa7983a` | `9006062` | 3차 감사 지시서: 현재 수치와 2차 수리 점검 항목으로 갱신 |
| `ebc0dc2` | `fa25f1c` | Codex 3라운드 감사 보고서와 증거(대용량 사본 제외) |
| `d3e1b48` | `588177b` | Codex 3라운드 수리: 백신 문구, 질의 우회, 사명 변경, 접미사·에스테르·위약·근거 검사, 라벨 4건 |
| `b5c64ff` | `a55ba16` | 3라운드: 벡터 단어 차단, 판정문, README 두 개·대시보드를 새 수치로 |
| `f6a91a8` | `ed11865` | 대시보드를 쉬운 한국어로 다시 씀 (숫자는 그대로 파이프라인 산출물에서 읽음) |
| `7b238a2` | `a420eed` | 직접 써 보기 화면(src/app.py): 약 이름 해석·질문·AI 답 근거 검사를 실제 파이프라인 함수로 |
| `0c441e0` | `f307eb7` | 근거 검사에 문장 단위 주장 검사 추가: 관계·부정·비교·추측·개발 주장·단계·시험 수·평범한 말 |
| `a12762b` | `d6c28ff` | 주장 검사를 절 단위 주어-관계-목적어 읽기로 다시 씀 (Codex 1차 지적 전부 수리) |
| `9a80fcb` | `c2ac824` | 주장 검사 Codex 2차 지적 수리: 명사형·수동태 방향, 이음 대상, 절 단위 대명사, 숫자 주인, 작용 종류 경계, 목록 제목, 거절 제품, 인용, 동사 없는 조각, 질환 주장 |
| `8d4a606` | `6dc060d` | 2차 판정문: 탐침 결과 파일이 덮인 사실 기록 |
| `2de10d9` | `410e58a` | 주장 검사 Codex 3차 지적 수리: 복수 대명사, 두 약이 나눈 시험 수, 제목 검사, 종류 단어·질환·동일시, 근거에 있는 인용만 지움, 충실한 문장 오탐 |
| `9fda6f8` | `0e3a98a` | 주장 검사 Codex 4차 지적 수리: 제목 형용사 보존, 복수 대명사·생략 주어 그룹, 'trials: N' 공유 수, 시험 묶음 단계·상태, 종류 단어 주인, 철자 띄워 쓴 부정, 충실한 문장 오탐 |
| `80da81b` | `65ec22b` | 주장 검사 Codex 5차 지적 수리: 제목 명사 보존, 주어 묶음 전원 검사, 수동태 뒤 it, 괄호 속 단계·상태, 'such trials' 수, 종류 단어 주인, 충실한 문장 12건 |
| `aa5655a` | `b261396` | 구조화된 답: 언어 모델은 근거 엣지를 인용한 주장만 내고, 주장마다 그래프와 정확히 대조해 맞는 것만으로 답 문장을 씀 |
| `60b9c61` | `54e912e` | 구조화된 답 Codex 1차 수리: 이름은 id·그래프 이름·ASCII만, 증거 이름 그대로 허용, 잘못된 형식은 거절, NaN·깊은 중첩·빈 답 처리, 문서 |
| `6bcde72` | `3924d63` | 구조화된 답 Codex 2차 수리: 이름 하나에 노드 하나, 무한·NaN 숫자, 모델 없음·장애 보고, 문구 |
| `8adf2dd` | `ff80c1d` | 구조화된 답 Codex 3차 수리: 여러 노드를 가리킬 수 있는 별칭은 거절 |
| `5a112d9` | `76aed60` | 구조화된 답 Codex 4차 승인 기록, 대시보드 재생성 |
| `bfcb83d` | `aac4584` | 직접 써 보기: 관계 지도(약·표적·회사·임상을 넣고 이어진 것을 눌러 따라가기) |
| `9db058c` | `69a97b2` | 관계 지도 Codex 1차 수리: 여러 토큰 제품·추적자 거절, 주관/협력 역할, 은퇴 노드, 정렬·잘림 표시, 링크 제한 |
| `c64f433` | `7511f3c` | 관계 지도: 역할 없는 후원은 추측하지 않음, 이름 순 정렬 바로잡음, Codex 2차 중단 기록 |
| `574097f` | `34dcd97` | 관계 지도 Codex 2차 수리: 거절 범위가 쉼표·접속어를 넘지 않음, 기록 없는 수는 0이 아님 |
| `bf436c6` | `1b24989` | 관계 지도 Codex 3차 수리: 거절을 그 약이 든 최소 구간에 묶음, 쉼표 경계, 긴 이름 재매칭 금지 |
| `514929c` | `f8cc07e` | 관계 지도 Codex 4차 수리: 수식어가 있는 목록 항목의 약은 모두 거절(추측하지 않음) |
| `595f5f9` | `a9947f4` | 관계 지도 Codex 5차 수리: 붙은 슬래시, 접속어로 떨어진 수식어, 목록 항목 경계, 선형 검사 |
| `c43f911` | `94c9126` | 관계 지도: 상품명 자체(Mvasi 등)는 접속어 너머로 거절을 옮기지 않음, 단독 수식어만 옮김 |
| `b7a00f9` | `bb5d6bf` | Codex 6차 지시서 |
| `9bd7cb4` | `3e7c834` | 관계 지도 Codex 6차 수리: 해석기 거절과 일치, 붙은 구분자·가장자리 구두점·괄호 안 접속어, 전체 이름 우선 |
| `ec4eede` | `d0b26d5` | 관계 지도 Codex 7차 수리: 한 가지 정규화로 모든 검사, 공백 동위원소, 정확한 저장 이름만 통째로, 해석 캐시 |
| `3a362eb` | `ad5a8b9` | 관계 지도 Codex 8차 수리: 해석기 추적자 규칙 존중, 구두점 접은 형태도 검사, 모든 대시, 캐시·쉼표·단독 이름 |
| `c364c84` | `59ef376` | 관계 지도 Codex 9차 수리: 조회 키와 같은 형태로 거절(접미사·동위원소 인접·밑줄·악센트) |
| `2b9fc92` | `c707a25` | 관계 지도 Codex 10차 수리: 이름 안·옆 동위원소, 동위원소 단독 이름만, 구분자 무관 수식어 |
| `d9260a1` | `953d34d` | 관계 지도 Codex 11차 수리: 조각난 동위원소·접미사를 키처럼 붙여 검사 |
| `481100c` | `7f318fd` | 관계 지도 Codex 12차 수리: 이름 안에서 쪼개진 동위원소도 붙여 검사 |
| `73ee310` | `02d30fa` | 관계 지도 Codex 13차 수리: 킬레이터에 붙은 동위원소 거절, 소문자 화학명·용량은 그대로 |
| `1b38966` | `2a56016` | 관계 지도 Codex 14차 수리: 대문자 한 글자 원소, 뒤 표시어, 의료용 질량의 끝 표지 |
| `8ebd662` | `ffda738` | 관계 지도 Codex 15차 수리: 의료용 동위원소 질량표로 항목 전체 검사, 표지된 약 자체는 허용 |
| `4df54ae` | `db929cc` | 관계 지도 Codex 16차 수리: 원소 먼저 쓴 한 글자 동위원소, 항목당 한 번 계산 |
| `4bed79c` | `6a401d8` | 관계 지도 Codex 17차 수리: 구두점 경계를 지킨 한 글자 동위원소 검사 |
| `c476d9d` | `ba411af` | 관계 지도 Codex 18차 수리: 원소 이름으로 쓴 동위원소와 방사표지 단어 |
| `0932ac3` | `89fefd4` | 관계 지도 Codex 19차 수리: 나뉜 방사표지 단어, 99m 앞에 쓴 원소 이름 |
| `e648017` | `f8d5382` | Refuse therapy-nuclide labels (Tb-161, Th-227, Bi-213) and glued label spellings (Codex m20) |
| `7f85cc0` | `5b8a770` | Refuse bounded symbol isotopes (Ce-134, Mn-52) and radioisotope wording (Codex m21) |
| `a7d5f7f` | `a26292a` | Refuse fused mass symbols (52Mn, 134CeDOTA) and radio-/astatinated/labelled wording (Codex m22) |
| `6505eec` | `c3a2c38` | Refuse interior symbol isotopes (DOTACe134) and conjugate wording; narrow negation (Codex m23) |
| `16b600d` | `7c71acd` | Payload exemption by name word, coupling wording, joined-phrase negation (Codex m24) |
| `c42e895` | `29730bc` | Negation stops at its own word; reagent nouns after linked to (Codex m25) |
| `9d8b796` | `0d22d33` | not-only affirms; linked reads named reagents anywhere in the item (Codex m26) |
| `23b07f5` | `f775add` | Hyphenated payload codes, named dyes, focus words after not (Codex m27 partial) |
| `e5c11e1` | `4e4eb5e` | Focus words in label guard, dye codes, extra modification of a named ADC (Codex m28) |
| `8eb2555` | `46ab0f3` | Suffixed dye codes; any further partner of a named ADC refuses (Codex m29 partial) |
| `9f7f808` | `c4c7e2e` | linked fails closed with relation allowlist; modification verbs; ADC partner windows (Codex m30) |
| `4493fe0` | `87f779c` | Read past setting phrases to the partner; gene relations; question words end windows (Codex m31) |
| `b21da2b` | `e9a8449` | Relation map takes one whole name; shared drug keys are not decided by spelling |
| `db1580d` | `2ef9782` | Relation map reads stored names under one rule (Codex m32) |
| `1f6017e` | `2948f86` | Map reads a drug only by its preferred name; refused stored names stay refused (Codex m33) |
| `56eb3d6` | `6df1e02` | Check every stored spelling for refusal; keep rotation signs; brackets around a name (Codex m34) |
| `c3040c1` | `5b9c10f` | Rotation signs read after invisible characters go; sign groups beside bracketed names (Codex m35) |
| `2b1aca1` | `bf942fa` | Compare names with a sign descriptor as written; any sign beside a shared-key name (Codex m36) |
| `e821094` | `9b94f08` | Descriptor scan covers every non-letter; page states the descriptor exception (Codex m37 should-fix) |
| `dff2810` | `720c2c6` | Map audit rounds 20-38: keep brief, report and log; note data licences |

Later commits differ between the two copies in the same way; on GitHub, read
them from `git log`.
