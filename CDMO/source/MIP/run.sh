#!/bin/bash
# ============================================================
#  Run MIP model on a single instance
#  Usage: bash run.sh <approach_name> <instance_number>
#  Example: bash run.sh ortools 1
# ============================================================

set -e

APPROACH=${1:-ortools}
INSTANCE=${2:-1}
OUTPUT_DIR="/res/MIP"
OUTPUT_FILE="${OUTPUT_DIR}/${INSTANCE}.json"

mkdir -p "${OUTPUT_DIR}"

echo "Running MIP (${APPROACH}) on instance ${INSTANCE}..."

python3 "$(dirname "$0")/orsp_mip.py" \
    --instance  "${INSTANCE}" \
    --approach  "${APPROACH}" \
    --output    "${OUTPUT_FILE}" \
    --time-limit 300

echo "Done. Result saved to ${OUTPUT_FILE}"