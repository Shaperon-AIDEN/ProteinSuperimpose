# superimpose_by_chainA.py

CIF 형식의 단백질 구조 파일들을 지정한 Chain의 Cα 원자를 기준으로 superimpose합니다.
파일명 패턴(`*_model_N.cif`)으로 디자인 그룹을 자동 분류하고, reference 모델에 나머지 모델을 정렬합니다.
정렬 시 모든 Chain이 rigid body로 함께 이동합니다.

---

## 요구 사항

- Python 3.8 이상

### 라이브러리 설치

```bash
pip install -r requirements.txt
```

---

## 사용법

```bash
python superimpose_by_chainA.py \
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

---

## 입력 파일 명명 규칙

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

---

## 사용 예시

### Chain A 기준 (기본값)

```bash
python superimpose_by_chainA.py \
  --input_dir  vNMb#02 \
  --output_dir vNMb#02_aligned
```

### Chain B 기준

```bash
python superimpose_by_chainA.py \
  --input_dir  consistency_analysis_HSA/predicted_structure_seed1235 \
  --output_dir consistency_analysis_HSA/predicted_structure_seed1235_aligned \
  --chain B
```

### model_1을 reference로 사용

```bash
python superimpose_by_chainA.py \
  --input_dir  vNMb#02 \
  --output_dir vNMb#02_aligned_ref1 \
  --chain A \
  --reference_model 1
```

---

## 동작 방식

1. `--input_dir` 내 `*.cif` 파일을 `<design_id>_model_<N>.cif` 패턴으로 그룹화
2. 각 그룹에서 `--reference_model` 번호의 구조를 reference로 로드
3. `--chain`으로 지정한 Chain의 Cα 원자만을 사용해 최적 superimposition 계산
4. 계산된 rotation/translation을 구조 전체(모든 Chain)에 적용
5. reference 포함 모든 모델을 `--output_dir`에 저장

> Google Drive 등 네트워크 스토리지의 파일은 다운로드 지연으로 타임아웃이 발생할 수 있습니다.
> 이 경우 자동으로 최대 5회 재시도합니다.

---

## 출력

- 정렬된 CIF 파일: `<output_dir>/<원본 파일명>.cif`
- 처리 완료 후 성공/오류 건수 및 저장 경로 출력

```
총 디자인 그룹 수: 380
Superimpose 기준 Chain: A
Reference 모델 인덱스: 0
  진행: 500개 처리 완료
  ...
완료: 성공 3420개, 오류 0개
결과 저장 위치: consistency_analysis_HSA/predicted_structure_seed1235_aligned
```
