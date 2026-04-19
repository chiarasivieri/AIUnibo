#!/bin/bash
# ============================================================
#  Run CP model on a single instance
#  Usage: bash run.sh <approach_name> <instance_number>
#  Example: bash run.sh gecode 1
# ============================================================

set -e

APPROACH=${1:-gecode}
INSTANCE=${2:-1}

MODEL_DIR="$(dirname "$0")"
INSTANCE_FILE="${MODEL_DIR}/instances/inst${INSTANCE}.dzn"
MODEL_FILE="${MODEL_DIR}/orsp.mzn"
OUTPUT_DIR="/res/CP"
OUTPUT_FILE="${OUTPUT_DIR}/${INSTANCE}.json"

mkdir -p "${OUTPUT_DIR}"

if [ ! -f "${INSTANCE_FILE}" ]; then
    echo "ERROR: Instance file not found: ${INSTANCE_FILE}"
    exit 1
fi

echo "Running CP (${APPROACH}) on instance ${INSTANCE}..."

# Map approach name to MiniZinc solver flag
case "${APPROACH}" in
    gecode)         SOLVER="gecode" ;;
    chuffed)        SOLVER="chuffed" ;;
    gecode_symbreak) SOLVER="gecode" ;;   # same solver, symmetry breaking is in the model
    *)              SOLVER="${APPROACH}" ;;
esac

# Run MiniZinc with 5-minute time limit (300000 ms)
# -a: output all intermediate solutions (for optimization tracking)
# --output-time: print timing info
START_TIME=$(date +%s%N)

RESULT=$(minizinc \
    --solver "${SOLVER}" \
    --time-limit 300000 \
    -a \
    --output-objective \
    "${MODEL_FILE}" "${INSTANCE_FILE}" 2>&1) || true

END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000000 ))

echo "Elapsed: ${ELAPSED}s"
echo "Raw output:"
echo "${RESULT}"

# Parse and save result via Python helper
python3 "$(dirname "$0")/../utilis/parse_cp_output.py" \
    --approach "${APPROACH}" \
    --instance "${INSTANCE}" \
    --elapsed "${ELAPSED}" \
    --output "${OUTPUT_FILE}" \
    --raw "${RESULT}"

echo "Result saved to ${OUTPUT_FILE}"