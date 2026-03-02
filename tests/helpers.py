"""
테스트용 최소 유효 mmCIF 파일 생성 헬퍼.

BioPython MMCIFParser와 gemmi 모두 파싱 가능한 CIF를 생성한다.
CA 원자만 포함하며, pLDDT 데이터(_ma_qa_metric_local)도 기록한다.
"""

import math
from pathlib import Path


PLDDT_5 = [75.0, 80.0, 85.0, 90.0, 70.0]


def helix_coords(n: int, radius: float = 2.0, rise: float = 1.5, angle_step: float = 100.0):
    """n개의 CA 원자에 대한 나선형 3D 좌표 생성 (Å)."""
    coords = []
    for i in range(n):
        angle = math.radians(i * angle_step)
        coords.append((radius * math.cos(angle), radius * math.sin(angle), i * rise))
    return coords


def rotate_z(coords, angle_deg: float):
    """좌표 목록을 Z축 기준으로 angle_deg만큼 회전."""
    a = math.radians(angle_deg)
    cos_a, sin_a = math.cos(a), math.sin(a)
    return [(cos_a * x - sin_a * y, sin_a * x + cos_a * y, z) for x, y, z in coords]


def make_minimal_cif(
    residues: list,
    chain_id: str = "A",
    plddt_values: list = None,
    coords: list = None,
    data_name: str = "test",
) -> str:
    """
    최소 유효 mmCIF 문자열 생성.

    Parameters
    ----------
    residues     : [(seq_num, res_name), ...] - 잔기 목록
    chain_id     : chain ID (BioPython auth_asym_id 기준)
    plddt_values : 잔기별 pLDDT 값 리스트 (None이면 80.0으로 채움)
    coords       : [(x, y, z), ...] - 좌표 목록 (None이면 나선형 자동 생성)
    data_name    : CIF data block 이름
    """
    n = len(residues)
    if plddt_values is None:
        plddt_values = [80.0] * n
    if coords is None:
        coords = helix_coords(n)

    lines = [f"data_{data_name}", "#"]

    # ── _atom_site ──────────────────────────────────────────
    lines += [
        "loop_",
        "_atom_site.group_PDB",
        "_atom_site.id",
        "_atom_site.type_symbol",
        "_atom_site.label_atom_id",
        "_atom_site.label_alt_id",
        "_atom_site.label_comp_id",
        "_atom_site.label_asym_id",
        "_atom_site.label_entity_id",
        "_atom_site.label_seq_id",
        "_atom_site.pdbx_PDB_ins_code",
        "_atom_site.Cartn_x",
        "_atom_site.Cartn_y",
        "_atom_site.Cartn_z",
        "_atom_site.occupancy",
        "_atom_site.B_iso_or_equiv",
        "_atom_site.auth_seq_id",
        "_atom_site.auth_asym_id",
        "_atom_site.auth_atom_id",
        "_atom_site.pdbx_PDB_model_num",
    ]
    for i, ((seq_num, res_name), (x, y, z), plddt) in enumerate(
        zip(residues, coords, plddt_values), start=1
    ):
        lines.append(
            f"ATOM {i} C CA . {res_name} {chain_id} 1 {seq_num} ? "
            f"{x:.3f} {y:.3f} {z:.3f} 1.00 {plddt:.2f} {seq_num} {chain_id} CA 1"
        )
    lines.append("#")

    # ── _ma_qa_metric (pLDDT 메타데이터) ─────────────────────
    lines += [
        "loop_",
        "_ma_qa_metric.id",
        "_ma_qa_metric.name",
        "_ma_qa_metric.type",
        "_ma_qa_metric.mode",
        "_ma_qa_metric.software_group_id",
        "1 pLDDT pLDDT local 1",
        "#",
    ]

    # ── _ma_qa_metric_local (잔기별 pLDDT) ───────────────────
    lines += [
        "loop_",
        "_ma_qa_metric_local.ordinal_id",
        "_ma_qa_metric_local.model_id",
        "_ma_qa_metric_local.label_asym_id",
        "_ma_qa_metric_local.label_seq_id",
        "_ma_qa_metric_local.label_comp_id",
        "_ma_qa_metric_local.metric_id",
        "_ma_qa_metric_local.metric_value",
    ]
    for i, ((seq_num, res_name), plddt) in enumerate(zip(residues, plddt_values), start=1):
        lines.append(f"{i} 1 {chain_id} {seq_num} {res_name} 1 {plddt:.2f}")
    lines.append("#")

    return "\n".join(lines) + "\n"


def write_cif(path: Path, residues: list, **kwargs) -> Path:
    """CIF 파일을 생성하고 경로를 반환."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(make_minimal_cif(residues, **kwargs))
    return path
