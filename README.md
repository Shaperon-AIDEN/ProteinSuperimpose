# ProteinSuperimpose

CIF 형식의 단백질 구조 파일들을 지정한 Chain의 Cα 원자를 기준으로 superimpose하는 스크립트 모음입니다.
정렬 시 모든 Chain이 rigid body로 함께 이동하며, pLDDT 등 원본 CIF의 모든 메타데이터가 보존됩니다.

| 스크립트 | 용도 |
|----------|------|
| [`superimpose_by_chain.py`](#superimpose_by_chainpy) | 단일 디렉토리 내 파일을 디자인 그룹별로 superimpose |
| [`superimpose_all_by_chain.py`](#superimpose_all_by_chainpy) | 최상위 폴더 하위의 **모든** CIF 파일을 단일 reference 기준으로 superimpose |

---

## Claude Code Skill

Claude Code에서 `/superimpose-protein` 슬래시 명령어 또는 "구조 정렬", "superimpose", "alignment" 키워드로 이 스크립트들을 자동 실행할 수 있습니다.

### 스킬 설치

**자동 설치 (권장):**

```bash
# 전역 설치 (~/.claude/skills/) — 모든 프로젝트에서 사용 가능
bash install_skill.sh

# 프로젝트 수준 설치 (.claude/skills/) — 현재 프로젝트에서만 사용
bash install_skill.sh --project

# 특정 프로젝트에 설치
bash install_skill.sh --project /path/to/your/project
```

**수동 설치:**

```bash
# 전역 설치
mkdir -p ~/.claude/skills/superimpose-protein
cp skills/superimpose-protein/SKILL.md ~/.claude/skills/superimpose-protein/

# 프로젝트 수준 설치
mkdir -p .claude/skills/superimpose-protein
cp skills/superimpose-protein/SKILL.md .claude/skills/superimpose-protein/
```

### 설치 후 주의사항

> **중요:** 스킬 설치 후 반드시 새 Claude Code 세션을 시작해야 스킬이 인식됩니다.
> `~/.claude/skills/`는 세션 시작 시 로드되며, 실행 중인 세션에서는 새로 생성된 파일을 자동 감지하지 않습니다.

설치 확인 방법:
```
# Claude Code 새 세션에서 슬래시 명령어 사용
/superimpose-protein chain=A input=./my_structures
```

---

## 요구 사항

- [Conda](https://docs.conda.io/en/latest/miniconda.html) 설치
- Python 3.11 (Conda 환경 `superimpose` 권장)

### 환경 생성 및 라이브러리 설치

```bash
# Conda 환경 생성
conda create -n superimpose python=3.11 -y

# 라이브러리 설치
conda run -n superimpose pip install -r requirements.txt
```

---

## superimpose_by_chain.py

단일 디렉토리 내 CIF 파일을 `<design_id>_model_N.cif` 패턴으로 그룹화하고,
각 그룹 내에서 reference 모델을 기준으로 나머지 모델을 superimpose합니다.

### 사용법

```bash
conda run -n superimpose python superimpose_by_chain.py \
  --input_dir  <입력 디렉토리> \
  --output_dir <출력 디렉토리> \
  [--chain A] \
  [--reference_model 0]
```

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--input_dir` | *(필수)* | CIF 파일이 있는 입력 디렉토리 |
| `--output_dir` | *(필수)* | 정렬된 CIF 파일을 저장할 출력 디렉토리 (없으면 자동 생성) |
| `--chain` | `A` | Superimpose 기준으로 사용할 Chain ID |
| `--reference_model` | `0` | 기준(reference)으로 사용할 모델 번호 |

### 입력 파일 명명 규칙

스크립트는 아래 패턴의 파일을 인식합니다:

```
<design_id>_model_<N>.cif
```

예시:
```
designCDRsFR_hALBD2hmsame1_0025_model_0.cif   ← reference (N=0)
designCDRsFR_hALBD2hmsame1_0025_model_1.cif
...
designCDRsFR_hALBD2hmsame1_0025_model_9.cif
ALB_vNMb#02_model_0.cif
ALB_vNMb#02_model_1.cif
```

같은 `<design_id>`를 가진 파일들이 하나의 그룹으로 처리됩니다.

### 사용 예시

```bash
# Chain A 기준 (기본값)
conda run -n superimpose python superimpose_by_chain.py \
  --input_dir  vNMb#02 \
  --output_dir vNMb#02_aligned

# Chain B 기준
conda run -n superimpose python superimpose_by_chain.py \
  --input_dir  predicted_structure_seed1235 \
  --output_dir predicted_structure_seed1235_aligned \
  --chain B

# model_1을 reference로 사용
conda run -n superimpose python superimpose_by_chain.py \
  --input_dir  vNMb#02 \
  --output_dir vNMb#02_aligned_ref1 \
  --chain A \
  --reference_model 1
```

### 동작 방식

1. `--input_dir` 내 `*.cif` 파일을 `<design_id>_model_<N>.cif` 패턴으로 그룹화
2. 각 그룹에서 `--reference_model` 번호의 구조를 reference로 로드
3. `--chain`으로 지정한 Chain의 Cα 원자만을 사용해 최적 superimposition 계산
4. 계산된 rotation/translation을 구조 전체(모든 Chain)에 적용
5. 원본 CIF 파일에서 좌표 컬럼(`_atom_site.Cartn_x/y/z`)만 갱신하여 저장
   - pLDDT(`_ma_qa_metric_local`) 등 모든 메타데이터 보존
   - reference 모델은 원본 파일 그대로 복사

> Google Drive 등 네트워크 스토리지의 파일은 다운로드 지연으로 타임아웃이 발생할 수 있습니다.
> 이 경우 자동으로 최대 5회 재시도합니다.

### 출력

```
총 디자인 그룹 수: 380
Superimpose 기준 Chain: A
Reference 모델 인덱스: 0
  진행: 500개 처리 완료
  ...
완료: 성공 3,420개, 오류 0개
결과 저장 위치: predicted_structure_seed1235_aligned
```

---

## superimpose_all_by_chain.py

최상위 폴더 하위의 **모든** CIF 파일을 단일 reference 구조를 기준으로 superimpose합니다.
하위 디렉토리를 재귀적으로 탐색하며, 입력 디렉토리 구조를 그대로 유지해 결과를 저장합니다.
잔기 번호(residue sequence number) 기준으로 공통 Cα만 사용하므로, CDR 길이가 다른 설계들 간에도 alignment 가능합니다.

### 사용법

```bash
conda run -n superimpose python superimpose_all_by_chain.py \
  --input_root  <최상위 입력 디렉토리> \
  --output_root <최상위 출력 디렉토리> \
  [--chain A] \
  [--reference FILE]
```

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--input_root` | *(필수)* | CIF 파일이 있는 최상위 디렉토리 (하위 폴더 포함 재귀 탐색) |
| `--output_root` | *(필수)* | 결과를 저장할 최상위 디렉토리 (입력 디렉토리 구조 미러링) |
| `--chain` | `A` | Superimpose 기준으로 사용할 Chain ID |
| `--reference` | *(없음)* | 기준 CIF 파일 경로. 미지정 시 `input_root` 내 알파벳 순 첫 번째 파일 자동 선택 |

### 사용 예시

```bash
# consistency_HSA/MSA 전체를 Chain A 기준으로 단일 reference에 정렬
conda run -n superimpose python superimpose_all_by_chain.py \
  --input_root  structure_prediction_designedNMb \
  --output_root structure_prediction_designedNMb_aligned \
  --chain A

# 특정 파일을 reference로 명시
conda run -n superimpose python superimpose_all_by_chain.py \
  --input_root  structure_prediction_designedNMb \
  --output_root structure_prediction_designedNMb_aligned \
  --chain B \
  --reference   structure_prediction_designedNMb/consistency_HSA/predicted_structure_seed1235/h_designCDRsFR_hALBD2hmsame1_0025_model_0.cif
```

### 동작 방식

1. `--input_root` 하위의 모든 `*.cif` 파일을 재귀적으로 수집 (알파벳 순 정렬)
2. `--reference`로 지정된 파일 또는 첫 번째 파일을 단일 global reference로 사용
3. `--chain`으로 지정한 Chain의 Cα 원자를 잔기 번호 기준으로 매칭
   - CDR 길이 등이 달라도 공통 잔기만 사용해 alignment 수행
4. 계산된 rotation/translation을 구조 전체(모든 Chain)에 적용
5. 원본 CIF 파일에서 좌표 컬럼만 갱신하여 저장 (pLDDT 등 모든 메타데이터 보존)
6. 출력 경로는 `output_root / <input_root 기준 상대경로>`로 결정 (디렉토리 구조 미러링)

### 출력

```
총 CIF 파일 수  : 38,000
Superimpose Chain: A
Reference 구조  : consistency_HSA/predicted_structure_seed1235/h_designCDRsFR_hALBD2hmsame1_0025_model_0.cif
Reference Cα 수 : 127

  진행: 1,000/38,000  (성공 999 / 스킵 0 / 오류 0)
  진행: 2,000/38,000  (성공 1,999 / 스킵 0 / 오류 0)
  ...
완료: 성공 37,999개, 스킵 0개, 오류 0개
결과 저장 위치: structure_prediction_designedNMb_aligned
```
