#!/usr/bin/env bash
# install_skill.sh — Install the superimpose-protein Claude Code skill
#
# 사용법:
#   bash install_skill.sh                          # 전역 설치 (~/.claude/skills/)
#   bash install_skill.sh --project                # 현재 디렉토리 프로젝트 수준 설치
#   bash install_skill.sh --project /path/to/proj  # 지정 프로젝트 수준 설치
#
# 설치 후 새 Claude Code 세션을 시작해야 스킬이 인식됩니다.

set -euo pipefail

SKILL_NAME="superimpose-protein"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_SRC="${SCRIPT_DIR}/skills/${SKILL_NAME}/SKILL.md"

# ── 소스 파일 확인 ──────────────────────────────────
if [[ ! -f "${SKILL_SRC}" ]]; then
    echo "Error: Skill source not found at:" >&2
    echo "  ${SKILL_SRC}" >&2
    exit 1
fi

# ── 설치 대상 결정 ───────────────────────────────────
if [[ "${1:-}" == "--project" ]]; then
    PROJECT_DIR="${2:-$(pwd)}"
    PROJECT_DIR="$(cd "${PROJECT_DIR}" && pwd)"
    DEST_DIR="${PROJECT_DIR}/.claude/skills/${SKILL_NAME}"
    SCOPE="project"
    SCOPE_PATH="${PROJECT_DIR}/.claude/skills/"
else
    DEST_DIR="${HOME}/.claude/skills/${SKILL_NAME}"
    SCOPE="global"
    SCOPE_PATH="${HOME}/.claude/skills/"
fi

# ── 설치 ──────────────────────────────────────────────
mkdir -p "${DEST_DIR}"
cp "${SKILL_SRC}" "${DEST_DIR}/SKILL.md"

echo ""
echo "✓ '${SKILL_NAME}' 스킬 설치 완료"
echo ""
echo "  설치 범위 : ${SCOPE}"
echo "  설치 위치 : ${DEST_DIR}/SKILL.md"
echo ""
echo "★ 주의: 새 Claude Code 세션을 시작해야 스킬이 인식됩니다."
echo "  세션 시작 후 '/superimpose-protein' 명령어를 사용하거나,"
echo "  '구조 정렬', 'superimpose', 'alignment' 키워드를 포함해 요청하세요."
echo ""
