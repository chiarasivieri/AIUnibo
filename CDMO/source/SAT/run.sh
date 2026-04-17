#!/bin/bash
# ============================================================
#  Run SAT/SMT model on a single instance
#  Usage: bash run.sh <approach_name> <instance_number>
#  Example: bash run.sh z3 1
# ============================================================

set -e

APPROACH=${1:-z3}
INSTANCE=${2:-1}
OUTPUT_DIR="/res/SAT"
OUTPUT_FILE="${OUTPUT_DIR}/${INSTANCE}.json"

mkdir -p "${OUTPUT_DIR}"

echo "Running SAT/SMT (${APPROACH}) on instance ${INSTANCE}..."

python3 "$(dirname "$0")/orsp_sat.py" \
    --instance  "${INSTANCE}" \
    --approach  "${APPROACH}" \
    --output    "${OUTPUT_FILE}" \
    --time-limit 300

echo "Done. Result saved to ${OUTPUT_FILE}"