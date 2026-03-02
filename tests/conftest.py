"""공통 pytest fixtures."""

import sys
from pathlib import Path

import pytest

# 프로젝트 루트를 sys.path에 추가 (스크립트 직접 import 가능하도록)
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.helpers import helix_coords, rotate_z, write_cif


RESIDUES_5 = [(i, "ALA") for i in range(1, 6)]   # 5잔기 (seq 1~5)
RESIDUES_4 = [(i, "ALA") for i in range(1, 5)]   # 4잔기 (seq 1~4), CDR 짧은 경우
PLDDT_5 = [75.0, 80.0, 85.0, 90.0, 70.0]


@pytest.fixture
def ref_cif(tmp_path) -> Path:
    """Reference CIF: chain A, 5잔기, 나선형 좌표."""
    return write_cif(
        tmp_path / "ref_model_0.cif",
        RESIDUES_5,
        chain_id="A",
        plddt_values=PLDDT_5,
        coords=helix_coords(5),
    )


@pytest.fixture
def mob_cif(tmp_path) -> Path:
    """Mobile CIF: chain A, 5잔기, 45° 회전된 좌표."""
    return write_cif(
        tmp_path / "mob_model_1.cif",
        RESIDUES_5,
        chain_id="A",
        plddt_values=PLDDT_5,
        coords=rotate_z(helix_coords(5), 45.0),
    )


@pytest.fixture
def mob_short_cif(tmp_path) -> Path:
    """Mobile CIF: chain A, 4잔기 (seq 1~4) — CDR 길이 상이."""
    return write_cif(
        tmp_path / "mob_short_model_2.cif",
        RESIDUES_4,
        chain_id="A",
        plddt_values=[80.0] * 4,
        coords=rotate_z(helix_coords(4), 90.0),
    )


@pytest.fixture
def flat_input_dir(tmp_path) -> Path:
    """
    단일 디렉토리 내 3개 파일 (superimpose_by_chain.py 용).

    input_dir/
      design1_model_0.cif   ← reference
      design1_model_1.cif   ← 45° 회전
      design1_model_2.cif   ← 90° 회전
    """
    d = tmp_path / "input_dir"
    residues = RESIDUES_5
    write_cif(d / "design1_model_0.cif", residues, coords=helix_coords(5), plddt_values=PLDDT_5)
    write_cif(d / "design1_model_1.cif", residues, coords=rotate_z(helix_coords(5), 45.0), plddt_values=PLDDT_5)
    write_cif(d / "design1_model_2.cif", residues, coords=rotate_z(helix_coords(5), 90.0), plddt_values=PLDDT_5)
    return d


@pytest.fixture
def nested_input_root(tmp_path) -> Path:
    """
    최상위 폴더 하위에 2단계 디렉토리 구조 (superimpose_all_by_chain.py 용).

    input_root/
      sub1/
        h_design1_model_0.cif   (5잔기)
        h_design1_model_1.cif   (5잔기, 45° 회전)
      sub2/
        m_design1_model_0.cif   (5잔기, 20° 회전)
        m_design1_model_1.cif   (4잔기, CDR 상이)
    """
    r = tmp_path / "input_root"
    residues5 = RESIDUES_5
    residues4 = RESIDUES_4

    write_cif(r / "sub1" / "h_design1_model_0.cif", residues5, coords=helix_coords(5), plddt_values=PLDDT_5)
    write_cif(r / "sub1" / "h_design1_model_1.cif", residues5, coords=rotate_z(helix_coords(5), 45.0), plddt_values=PLDDT_5)
    write_cif(r / "sub2" / "m_design1_model_0.cif", residues5, coords=rotate_z(helix_coords(5), 20.0), plddt_values=PLDDT_5)
    write_cif(r / "sub2" / "m_design1_model_1.cif", residues4, coords=rotate_z(helix_coords(4), 90.0), plddt_values=[80.0] * 4)
    return r
