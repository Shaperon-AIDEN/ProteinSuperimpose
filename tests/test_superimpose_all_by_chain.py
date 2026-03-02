"""
superimpose_all_by_chain.py 테스트.

PR Test Plan 검증 항목:
  1. --input_root / --output_root / --chain 옵션 동작 확인
  2. 하위 디렉토리 구조가 output_root에 그대로 미러링되는지 확인
  3. 출력 CIF 파일의 pLDDT(_ma_qa_metric_local) 메타데이터 보존 확인
  4. --reference 명시 옵션 동작 확인
  5. CDR 길이가 다른 파일 처리 시 공통 Cα 매칭으로 skip 없이 처리되는지 확인
"""

import gemmi
import pytest

from superimpose_all_by_chain import superimpose_all
from tests.helpers import helix_coords, rotate_z, write_cif

RESIDUES_5 = [(i, "ALA") for i in range(1, 6)]   # seq 1~5
RESIDUES_4 = [(i, "ALA") for i in range(1, 5)]   # seq 1~4 (CDR 짧은 경우)
PLDDT_5 = [75.0, 80.0, 85.0, 90.0, 70.0]


# ──────────────────────────────────────────────
# Test 1: 기본 옵션 동작
# ──────────────────────────────────────────────

def test_basic_options(nested_input_root, tmp_path):
    """--input_root, --output_root, --chain 옵션으로 정상 실행된다."""
    out = tmp_path / "output"
    # 오류 없이 실행 완료되어야 함
    superimpose_all(str(nested_input_root), str(out), chain_id="A")
    assert out.is_dir()


def test_all_cif_files_are_output(nested_input_root, tmp_path):
    """input_root 내 모든 CIF 파일에 대응하는 출력 파일이 생성된다."""
    out = tmp_path / "output"
    superimpose_all(str(nested_input_root), str(out), chain_id="A")

    input_files = sorted(nested_input_root.rglob("*.cif"))
    for f in input_files:
        expected = out / f.relative_to(nested_input_root)
        assert expected.exists(), f"출력 파일 없음: {expected.relative_to(out)}"


# ──────────────────────────────────────────────
# Test 2: 디렉토리 구조 미러링
# ──────────────────────────────────────────────

def test_directory_structure_mirrored(nested_input_root, tmp_path):
    """하위 디렉토리 구조가 output_root에 그대로 복제된다."""
    out = tmp_path / "output"
    superimpose_all(str(nested_input_root), str(out), chain_id="A")

    assert (out / "sub1").is_dir(), "sub1 디렉토리 미생성"
    assert (out / "sub2").is_dir(), "sub2 디렉토리 미생성"
    assert (out / "sub1" / "h_design1_model_0.cif").exists()
    assert (out / "sub1" / "h_design1_model_1.cif").exists()
    assert (out / "sub2" / "m_design1_model_0.cif").exists()
    assert (out / "sub2" / "m_design1_model_1.cif").exists()


# ──────────────────────────────────────────────
# Test 3: pLDDT 메타데이터 보존
# ──────────────────────────────────────────────

def test_plddt_metadata_preserved(nested_input_root, tmp_path):
    """출력 CIF 파일에 _ma_qa_metric_local 섹션이 유지된다."""
    out = tmp_path / "output"
    superimpose_all(str(nested_input_root), str(out), chain_id="A")

    for cif_path in out.rglob("*.cif"):
        doc = gemmi.cif.read(str(cif_path))
        block = doc.sole_block()
        table = block.find("_ma_qa_metric_local.", ["metric_value"])
        assert len(table) > 0, f"{cif_path.name}: _ma_qa_metric_local 사라짐"


def test_plddt_values_unchanged(nested_input_root, tmp_path):
    """superimpose 후 pLDDT 수치가 원본과 동일하게 유지된다."""
    out = tmp_path / "output"
    superimpose_all(str(nested_input_root), str(out), chain_id="A")

    def get_plddt(path):
        block = gemmi.cif.read(str(path)).sole_block()
        return [float(r[0]) for r in block.find("_ma_qa_metric_local.", ["metric_value"])]

    for cif_path in (nested_input_root / "sub1").glob("*.cif"):
        in_vals = get_plddt(cif_path)
        out_vals = get_plddt(out / "sub1" / cif_path.name)
        assert in_vals == out_vals, f"{cif_path.name}: pLDDT 값 변경됨"


# ──────────────────────────────────────────────
# Test 4: --reference 명시 옵션
# ──────────────────────────────────────────────

def test_explicit_reference_is_copied_as_is(nested_input_root, tmp_path):
    """--reference로 지정한 파일은 좌표 변환 없이 원본 그대로 복사된다."""
    out = tmp_path / "output"
    explicit_ref = nested_input_root / "sub2" / "m_design1_model_0.cif"
    original_content = explicit_ref.read_text()

    superimpose_all(
        str(nested_input_root), str(out),
        chain_id="A",
        reference_path=str(explicit_ref),
    )

    output_ref = out / "sub2" / "m_design1_model_0.cif"
    assert output_ref.exists(), "reference 출력 파일 없음"
    assert output_ref.read_text() == original_content, "reference 파일 내용이 변경됨"


def test_explicit_reference_not_found_raises(nested_input_root, tmp_path):
    """존재하지 않는 --reference 지정 시 FileNotFoundError가 발생한다."""
    with pytest.raises(FileNotFoundError):
        superimpose_all(
            str(nested_input_root), str(tmp_path / "out"),
            chain_id="A",
            reference_path=str(tmp_path / "nonexistent.cif"),
        )


def test_default_reference_is_first_sorted_file(nested_input_root, tmp_path):
    """--reference 미지정 시 알파벳 순 첫 번째 파일이 reference로 선택된다."""
    out = tmp_path / "output"
    all_files = sorted(nested_input_root.rglob("*.cif"))
    expected_ref = all_files[0]
    original_content = expected_ref.read_text()

    superimpose_all(str(nested_input_root), str(out), chain_id="A")

    output_ref = out / expected_ref.relative_to(nested_input_root)
    assert output_ref.read_text() == original_content, "기본 reference 파일 내용이 변경됨"


# ──────────────────────────────────────────────
# Test 5: CDR 길이 상이 — 공통 Cα 매칭
# ──────────────────────────────────────────────

def test_short_residue_file_not_skipped(tmp_path):
    """
    잔기 수가 다른 mobile 파일도 공통 Cα(3개 이상)가 있으면 skip되지 않는다.
    ref: seq 1~5 (5잔기), mob: seq 1~4 (4잔기) → 공통 4개 → 처리되어야 함
    """
    root = tmp_path / "input"
    out = tmp_path / "output"

    write_cif(root / "ref_model_0.cif", RESIDUES_5,
              coords=helix_coords(5), plddt_values=PLDDT_5)
    write_cif(root / "mob_model_1.cif", RESIDUES_4,
              coords=rotate_z(helix_coords(4), 30.0), plddt_values=[80.0] * 4)

    superimpose_all(str(root), str(out), chain_id="A")

    assert (out / "mob_model_1.cif").exists(), "공통 Cα 4개인데 skip됨"


def test_too_few_common_ca_is_skipped(tmp_path):
    """
    공통 Cα가 3개 미만인 파일은 skip되어 출력 파일이 생성되지 않는다.
    ref: seq 1~5, mob: seq 10~14 → 공통 0개 → skip
    """
    root = tmp_path / "input"
    out = tmp_path / "output"

    ref_path = write_cif(root / "a_ref.cif", RESIDUES_5,
                         coords=helix_coords(5), plddt_values=PLDDT_5)
    # 잔기 번호가 전혀 겹치지 않는 파일
    disjoint = [(i, "ALA") for i in range(10, 15)]
    write_cif(root / "z_mob.cif", disjoint,
              coords=rotate_z(helix_coords(5), 30.0), plddt_values=[80.0] * 5)

    # reference를 명시하여 정렬 순서에 무관하게 의도를 명확히 함
    superimpose_all(str(root), str(out), chain_id="A", reference_path=str(ref_path))

    assert not (out / "z_mob.cif").exists(), "공통 Cα 0개인데 출력 파일 생성됨"


def test_coordinates_actually_transformed(tmp_path):
    """superimpose 후 mobile 파일의 좌표가 입력 좌표와 다르다 (변환이 적용됨)."""
    root = tmp_path / "input"
    out = tmp_path / "output"

    ref_path = write_cif(root / "a_ref.cif", RESIDUES_5,
                         coords=helix_coords(5), plddt_values=PLDDT_5)
    mob_path = write_cif(root / "z_mob.cif", RESIDUES_5,
                         coords=rotate_z(helix_coords(5), 45.0), plddt_values=PLDDT_5)

    # reference를 명시하여 정렬 순서에 무관하게 의도를 명확히 함
    superimpose_all(str(root), str(out), chain_id="A", reference_path=str(ref_path))

    def get_coords(path):
        block = gemmi.cif.read(str(path)).sole_block()
        return [(float(r[0]), float(r[1]), float(r[2]))
                for r in block.find("_atom_site.", ["Cartn_x", "Cartn_y", "Cartn_z"])]

    assert get_coords(mob_path) != get_coords(out / "z_mob.cif"), \
        "좌표 변환이 적용되지 않음"
