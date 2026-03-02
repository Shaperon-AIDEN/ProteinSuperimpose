"""
superimpose_by_chain.py 테스트.

검증 항목:
  - 기본 옵션(input_dir, output_dir, chain) 동작
  - design_id 그룹화 및 파일 출력 확인
  - pLDDT(_ma_qa_metric_local) 메타데이터 보존
  - --chain 옵션 (없는 chain 지정 시 skip)
  - --reference_model 옵션
"""

import gemmi
import pytest

from superimpose_by_chain import superimpose_models
from tests.helpers import helix_coords, rotate_z, write_cif, PLDDT_5


RESIDUES = [(i, "ALA") for i in range(1, 6)]


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def input_dir(tmp_path):
    """
    design1_model_0~2.cif (3파일) + design2_model_0~1.cif (2파일)
    """
    d = tmp_path / "input"
    for angle, idx in [(0, 0), (30, 1), (60, 2)]:
        write_cif(d / f"design1_model_{idx}.cif", RESIDUES,
                  coords=rotate_z(helix_coords(5), angle), plddt_values=PLDDT_5)
    for angle, idx in [(0, 0), (45, 1)]:
        write_cif(d / f"design2_model_{idx}.cif", RESIDUES,
                  coords=rotate_z(helix_coords(5), angle), plddt_values=PLDDT_5)
    return d


# ──────────────────────────────────────────────
# 테스트
# ──────────────────────────────────────────────

def test_output_files_created(input_dir, tmp_path):
    """기본 실행 후 모든 입력 파일에 대응하는 출력 파일이 생성된다."""
    out = tmp_path / "output"
    superimpose_models(str(input_dir), str(out), chain_id="A", reference_model_idx=0)

    assert (out / "design1_model_0.cif").exists(), "reference 파일 복사 실패"
    assert (out / "design1_model_1.cif").exists()
    assert (out / "design1_model_2.cif").exists()
    assert (out / "design2_model_0.cif").exists()
    assert (out / "design2_model_1.cif").exists()


def test_output_dir_auto_created(input_dir, tmp_path):
    """output_dir이 없어도 자동 생성된다."""
    out = tmp_path / "new_dir" / "nested"
    superimpose_models(str(input_dir), str(out), chain_id="A")
    assert out.is_dir()


def test_plddt_metadata_preserved(input_dir, tmp_path):
    """출력 CIF에 _ma_qa_metric_local 섹션이 유지된다."""
    out = tmp_path / "output"
    superimpose_models(str(input_dir), str(out), chain_id="A")

    for cif_path in out.glob("*.cif"):
        doc = gemmi.cif.read(str(cif_path))
        block = doc.sole_block()
        # _ma_qa_metric_local 테이블 존재 여부
        table = block.find("_ma_qa_metric_local.", ["metric_value"])
        assert len(table) > 0, f"{cif_path.name}: _ma_qa_metric_local 사라짐"


def test_coordinates_changed_after_superimpose(input_dir, tmp_path):
    """superimpose 후 mobile 모델의 좌표가 reference와 달라지지 않고 정렬된다 (이동 확인)."""
    out = tmp_path / "output"
    superimpose_models(str(input_dir), str(out), chain_id="A")

    # model_1은 45° 회전되어 있었으므로 superimpose 후 좌표가 변경되어야 함
    def get_ca_x(path):
        doc = gemmi.cif.read(str(path))
        block = doc.sole_block()
        table = block.find("_atom_site.", ["Cartn_x"])
        return [float(row[0]) for row in table]

    in_x = get_ca_x(input_dir / "design1_model_1.cif")
    out_x = get_ca_x(out / "design1_model_1.cif")
    assert in_x != out_x, "superimpose 후 좌표가 변경되지 않음"


def test_chain_not_found_skips(tmp_path):
    """지정한 chain이 없는 파일은 skip된다."""
    d = tmp_path / "input"
    out = tmp_path / "output"
    # chain A만 있는 파일
    write_cif(d / "design1_model_0.cif", RESIDUES, chain_id="A",
              coords=helix_coords(5), plddt_values=PLDDT_5)
    write_cif(d / "design1_model_1.cif", RESIDUES, chain_id="A",
              coords=rotate_z(helix_coords(5), 30.0), plddt_values=PLDDT_5)

    # chain B 기준으로 실행 → reference에 B 없음 → 0건 처리
    superimpose_models(str(d), str(out), chain_id="B")
    # output에 아무 파일도 생성되지 않아야 함 (reference 자체가 skip됨)
    assert not list(out.glob("*.cif"))


def test_reference_model_option(tmp_path):
    """--reference_model 1 지정 시 model_1이 reference(원본 복사)로 사용된다."""
    d = tmp_path / "input"
    out = tmp_path / "output"
    ref_content = None

    path0 = write_cif(d / "design1_model_0.cif", RESIDUES,
                      coords=helix_coords(5), plddt_values=PLDDT_5)
    path1 = write_cif(d / "design1_model_1.cif", RESIDUES,
                      coords=rotate_z(helix_coords(5), 45.0), plddt_values=PLDDT_5)
    ref_content = path1.read_text()

    superimpose_models(str(d), str(out), chain_id="A", reference_model_idx=1)

    # model_1은 변환 없이 원본 그대로 복사
    assert (out / "design1_model_1.cif").read_text() == ref_content
