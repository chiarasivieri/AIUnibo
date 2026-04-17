"""
parse_cp_output.py
Parses raw MiniZinc stdout and saves a .json result file
in the format required by the CDMO course checker.

Usage:
    python3 parse_cp_output.py \
        --approach gecode \
        --instance 1 \
        --elapsed 42 \
        --output /res/CP/1.json \
        --raw "$(minizinc ...)"
"""

import argparse
import json
import math
import os
import re
import sys


def parse_minizinc_output(raw: str, elapsed: int) -> dict:
    """
    Parse MiniZinc stdout to extract the last (best) solution found.
    MiniZinc outputs solutions separated by '----------'
    and ends with '==========' if optimal.
    """
    lines  = raw.strip().splitlines()
    blocks = "\n".join(lines).split("----------")

    # Find last non-empty block (= best solution found)
    solution_block = ""
    for block in reversed(blocks):
        if block.strip():
            solution_block = block.strip()
            break

    is_optimal = "==========" in raw
    timed_out  = "% Time limit exceeded" in raw or elapsed >= 300

    if not solution_block or "UNSATISFIABLE" in raw:
        return {
            "time":    300,
            "optimal": False,
            "obj":     None,
            "sol":     [],
        }

    # Extract objective value
    obj = None
    obj_match = re.search(r"Total overtime:\s*(\d+)", solution_block)
    if obj_match:
        obj = int(obj_match.group(1))

    # Extract solution rows: lines like "   1    |  1  |  2  | 0   | 105  |  0"
    sol = []
    for line in solution_block.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 6:
            try:
                surgery  = int(parts[0])
                day      = int(parts[1])
                room     = int(parts[2])
                start    = int(parts[3])
                end      = int(parts[4])
                sol.append({
                    "surgery": surgery,
                    "day":     day,
                    "room":    room,
                    "start":   start,
                    "end":     end,
                })
            except ValueError:
                continue

    runtime = math.floor(elapsed)
    if timed_out and not is_optimal:
        runtime = min(runtime, 300)

    return {
        "time":    runtime,
        "optimal": is_optimal,
        "obj":     obj,
        "sol":     sol,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approach",  required=True)
    parser.add_argument("--instance",  required=True)
    parser.add_argument("--elapsed",   type=int, required=True)
    parser.add_argument("--output",    required=True)
    parser.add_argument("--raw",       required=True)
    args = parser.parse_args()

    result = {args.approach: parse_minizinc_output(args.raw, args.elapsed)}

    try:
        with open(args.output, "r") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}

    existing.update(result)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
