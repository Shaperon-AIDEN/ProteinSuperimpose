---
name: superimpose-protein
description: >
  단백질 CIF 구조 파일들을 지정한 chain의 Cα 원자를 기준으로 superimpose.
  "구조 정렬", "superimpose", "alignment", "CIF 정렬" 키워드가 포함될 때 사용.
  두 가지 모드를 지원:
  (1) 단일 디렉토리 내 design_id 그룹별 정렬 (superimpose_by_chain.py)
  (2) 최상위 폴더 하위 모든 CIF 파일을 단일 reference에 정렬 (superimpose_all_by_chain.py)
---

# Protein Structure Superimposition Skill

사용자가 단백질 CIF 구조 파일들의 superimposition을 요청했습니다.

## Step 1 — 파라미터 파악

아래 정보를 컨텍스트에서 추론하거나, 불명확하면 사용자에게 확인합니다:

| 파라미터 | 설명 | 기본값 |
|---------|------|--------|
| **mode** | `group` = 디렉토리 내 design_id 그룹별 정렬 / `all` = 전체 파일을 단일 reference에 정렬 | 컨텍스트 판단 |
| **input** | 입력 CIF 파일 경로 (단일 디렉토리 또는 최상위 폴더) | — |
| **output** | 출력 디렉토리 경로 | input + `_aligned` 자동 생성 |
| **chain** | Superimpose 기준 chain ID | `A` |
| **reference** | (mode=all 전용) 기준 CIF 파일 경로 | 자동 선택 (알파벳 첫 번째) |

**모드 판단 기준:**
- 파일명에 `_model_N.cif` 패턴이 있고 같은 디자인의 여러 예측 모델을 정렬 → `group` 모드
- 여러 서브폴더에 걸친 모든 구조를 한 기준에 정렬 (h_/m_ 접두사 등) → `all` 모드

## Step 2 — ProteinSuperimpose 스크립트 위치 확인

다음 우선순위로 `superimpose_by_chain.py` 파일을 탐색하여 `script_dir`을 결정합니다:

1. 스킬 전역 설치 디렉토리: `~/.claude/skills/superimpose-protein/`
2. 스킬 프로젝트 설치 디렉토리: `.claude/skills/superimpose-protein/` (현재 작업 디렉토리 기준)
3. 현재 프로젝트 내 `ProteinSuperimpose/` 폴더
4. `~/workspace/Projects/nanobody_ALB/ProteinSuperimpose/`

스크립트를 찾지 못하면 위치를 사용자에게 확인합니다.

## Step 3 — conda 환경 확인

스크립트 실행 전 필요 라이브러리 확인:
```bash
conda run -n acemd python -c "import Bio, gemmi, numpy; print('OK')"
```
오류 시:
```bash
conda run -n acemd pip install -r <script_dir>/requirements.txt
```

## Step 4 — 스크립트 실행

### mode = group (superimpose_by_chain.py)

```bash
conda run -n acemd python <script_dir>/superimpose_by_chain.py \
  --input_dir  "<input>" \
  --output_dir "<output>" \
  --chain <chain> \
  [--reference_model <N>]
```

### mode = all (superimpose_all_by_chain.py)

```bash
conda run -n acemd python <script_dir>/superimpose_all_by_chain.py \
  --input_root  "<input>" \
  --output_root "<output>" \
  --chain <chain> \
  [--reference "<reference_file>"]
```

## Step 5 — 결과 검증

실행 완료 후:
1. 출력 요약(성공/스킵/오류 건수) 사용자에게 보고
2. 출력 디렉토리 파일 수 확인 (`find <output> -name "*.cif" | wc -l`)
3. 오류가 있으면 원인 파악 후 사용자에게 안내

## 주의사항

- 출력 디렉토리가 없으면 자동 생성됨 (별도 확인 불필요)
- pLDDT 등 원본 CIF 메타데이터는 gemmi를 통해 자동 보존됨
- CDR 길이가 다른 설계들 간에도 잔기 번호 기준 공통 Cα로 정렬됨 (mode=all)
- 파일이 많을 경우(>10,000) 실행 시간이 길 수 있음 — 사용자에게 미리 안내
