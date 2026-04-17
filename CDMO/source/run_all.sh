#!/bin/bash
# ============================================================
#  Run ALL models on ALL instances
#  Usage: bash run_all.sh
#  Generates all .json files under /res/
# ============================================================

set -e

SCRIPT_DIR="$(dirname "$0")"
INSTANCES=(1 2)   # add more instance numbers as you create them

echo "=============================="
echo " CDMO ORSP – Full Experiment"
echo "=============================="

# ── CP ────────────────────────────────────────────────────────────────────────
echo ""
echo "--- CP (MiniZinc) ---"
for INST in "${INSTANCES[@]}"; do
    echo "  [CP] gecode         instance ${INST}"
    bash "${SCRIPT_DIR}/CP/run.sh" gecode "${INST}" || echo "  FAILED"

    echo "  [CP] chuffed        instance ${INST}"
    bash "${SCRIPT_DIR}/CP/run.sh" chuffed "${INST}" || echo "  FAILED"
done

# ── MIP ───────────────────────────────────────────────────────────────────────
echo ""
echo "--- MIP (OR-Tools CP-SAT) ---"
for INST in "${INSTANCES[@]}"; do
    echo "  [MIP] ortools       instance ${INST}"
    bash "${SCRIPT_DIR}/MIP/run.sh" ortools "${INST}" || echo "  FAILED"
done

# ── SAT/SMT ───────────────────────────────────────────────────────────────────
echo ""
echo "--- SAT/SMT (Z3) ---"
for INST in "${INSTANCES[@]}"; do
    echo "  [SAT] z3            instance ${INST}"
    bash "${SCRIPT_DIR}/SAT/run.sh" z3 "${INST}" || echo "  FAILED"
done

echo ""
echo "=============================="
echo " All done. Results in /res/"
echo "=============================="