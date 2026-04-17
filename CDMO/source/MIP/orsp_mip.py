"""
Operating Room Scheduling Problem (ORSP)
MIP model using Google OR-Tools CP-SAT solver

Authors: Chiara Sivieri, Liam Busnelli Urso

Usage:
    python3 orsp_mip.py --instance 1 --approach ortools --output /res/MIP/1.json
"""

import argparse
import json
import math
import time

from ortools.sat.python import cp_model


# ── Instance loader ────────────────────────────────────────────────────────────

def load_instance(instance_number: int) -> dict:
    """
    Load instance parameters.
    In production these would be read from a file;
    here we define small instances inline for reproducibility.
    """
    instances = {
        1: {
            "n_surgeries":  6,
            "n_rooms":      2,
            "n_days":       2,
            "horizon":      480,
            "n_surgeons":   3,
            "soft_cap":     420,
            "duration":     [90, 120, 60, 150, 90, 75],
            "cleaning":     [15,  20, 10,  25, 15, 10],
            "surgeon":      [ 1,   2,  1,   3,  2,  3],   # 1-indexed
            "release_day":  [ 1,   1,  1,   1,  2,  2],   # 1-indexed
            "deadline":     [ 2,   2,  1,   2,  2,  2],   # 1-indexed
            # room_type[r] and surgery_room_type[s]: 0 = any room
            "room_type":            [1, 1],
            "surgery_room_type":    [0, 0, 0, 0, 0, 0],
        },
        2: {
            "n_surgeries":  12,
            "n_rooms":       3,
            "n_days":        3,
            "horizon":     480,
            "n_surgeons":    4,
            "soft_cap":    420,
            "duration":    [90, 120, 60, 150, 90, 75, 100, 130, 80, 110, 95, 70],
            "cleaning":    [15,  20, 10,  25, 15, 10,  20,  25, 15,  20, 15, 10],
            "surgeon":     [ 1,   2,  1,   3,  2,  3,   4,   1,  2,   3,  4,  1],
            "release_day": [ 1,   1,  1,   1,  1,  1,   2,   2,  2,   2,  3,  3],
            "deadline":    [ 2,   3,  1,   3,  2,  3,   3,   3,  3,   3,  3,  3],
            "room_type":           [1, 2, 1],
            "surgery_room_type":   [1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1],
        },
    }
    if instance_number not in instances:
        raise ValueError(f"Instance {instance_number} not found.")
    return instances[instance_number]


# ── Compatibility helper ───────────────────────────────────────────────────────

def is_compatible(s_idx: int, r_idx: int, inst: dict) -> bool:
    """Return True if surgery s can be performed in room r."""
    st = inst["surgery_room_type"][s_idx]
    rt = inst["room_type"][r_idx]
    return st == 0 or st == rt


# ── MIP model ─────────────────────────────────────────────────────────────────

def solve(inst: dict, approach: str, time_limit: int = 300) -> dict:
    """
    Build and solve the ORSP using OR-Tools CP-SAT.

    Variables
    ---------
    x[s, d, r]  : bool – surgery s is scheduled on day d in room r
    start[s]    : int  – start time (minutes) of surgery s within its assigned day
    overtime[s] : int  – max(0, end_time[s] - soft_cap)

    Returns a result dict compatible with the course .json format.
    """
    S = inst["n_surgeries"]
    R = inst["n_rooms"]
    D = inst["n_days"]
    H = inst["horizon"]
    soft_cap = inst["soft_cap"]

    eff_dur = [inst["duration"][s] + inst["cleaning"][s] for s in range(S)]

    model = cp_model.CpModel()

    # ── Decision variables ────────────────────────────────────────────────────

    # x[s][d][r] = 1 iff surgery s is on day d in room r
    x = [[[model.NewBoolVar(f"x_{s}_{d}_{r}")
           for r in range(R)]
          for d in range(D)]
         for s in range(S)]

    # start[s] = start time in minutes (within the assigned day)
    start = [model.NewIntVar(0, H - eff_dur[s], f"start_{s}") for s in range(S)]

    # overtime[s] = max(0, start[s] + eff_dur[s] - soft_cap)
    overtime = [model.NewIntVar(0, H, f"overtime_{s}") for s in range(S)]

    # ── Hard constraints ──────────────────────────────────────────────────────

    # C1: Each surgery is assigned exactly once (one day, one room)
    for s in range(S):
        model.Add(
            sum(x[s][d][r] for d in range(D) for r in range(R)) == 1
        )

    # C2: Respect release dates and deadlines (0-indexed internally)
    for s in range(S):
        rel = inst["release_day"][s] - 1
        dl  = inst["deadline"][s]  - 1
        for d in range(D):
            if d < rel or d > dl:
                for r in range(R):
                    model.Add(x[s][d][r] == 0)

    # C3: Room compatibility
    for s in range(S):
        for d in range(D):
            for r in range(R):
                if not is_compatible(s, r, inst):
                    model.Add(x[s][d][r] == 0)

    # C4: No overlap in the same room on the same day
    #     Using interval variables and NoOverlap constraint (cleaner in CP-SAT)
    for d in range(D):
        for r in range(R):
            intervals = []
            for s in range(S):
                # Optional interval: active only when x[s][d][r] == 1
                interval = model.NewOptionalIntervalVar(
                    start[s],
                    eff_dur[s],
                    start[s] + eff_dur[s],
                    x[s][d][r],
                    f"interval_{s}_{d}_{r}"
                )
                intervals.append(interval)
            model.AddNoOverlap(intervals)

    # C5: Same surgeon cannot operate in two rooms simultaneously on the same day
    surgeon_ids = list(set(inst["surgeon"]))
    for sg in surgeon_ids:
        surgeries_by_surgeon = [s for s in range(S) if inst["surgeon"][s] == sg]
        for d in range(D):
            intervals = []
            for s in surgeries_by_surgeon:
                # is_active: surgery s is on day d (in any room)
                is_active = model.NewBoolVar(f"active_{s}_{d}_sg{sg}")
                model.Add(
                    sum(x[s][d][r] for r in range(R)) == 1
                ).OnlyEnforceIf(is_active)
                model.Add(
                    sum(x[s][d][r] for r in range(R)) == 0
                ).OnlyEnforceIf(is_active.Not())
                interval = model.NewOptionalIntervalVar(
                    start[s],
                    eff_dur[s],
                    start[s] + eff_dur[s],
                    is_active,
                    f"surgeon_interval_{s}_{d}"
                )
                intervals.append(interval)
            if intervals:
                model.AddNoOverlap(intervals)

    # C6: Surgery must finish within the daily horizon
    for s in range(S):
        model.Add(start[s] + eff_dur[s] <= H)

    # ── Overtime constraints ──────────────────────────────────────────────────

    for s in range(S):
        end_s = start[s] + eff_dur[s]
        model.AddMaxEquality(overtime[s], [0, end_s - soft_cap])

    # ── Objective ─────────────────────────────────────────────────────────────

    total_overtime = model.NewIntVar(0, S * H, "total_overtime")
    model.Add(total_overtime == sum(overtime))
    model.Minimize(total_overtime)

    # ── Solve ─────────────────────────────────────────────────────────────────

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers  = 1   # sequential only

    t0     = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - t0

    # ── Extract solution ──────────────────────────────────────────────────────

    status_name = solver.StatusName(status)
    is_optimal  = status == cp_model.OPTIMAL
    is_feasible = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    if is_feasible:
        obj_value = int(solver.ObjectiveValue())
        sol = []
        for s in range(S):
            for d in range(D):
                for r in range(R):
                    if solver.Value(x[s][d][r]) == 1:
                        sol.append({
                            "surgery":  s + 1,
                            "day":      d + 1,
                            "room":     r + 1,
                            "start":    solver.Value(start[s]),
                            "end":      solver.Value(start[s]) + eff_dur[s],
                        })
    else:
        obj_value = None
        sol = []

    runtime = math.floor(elapsed)
    if not is_feasible:
        runtime = 300  # timed out without solution

    return {
        approach: {
            "time":    runtime,
            "optimal": is_optimal,
            "obj":     obj_value,
            "sol":     sol,
        }
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ORSP MIP solver (OR-Tools CP-SAT)")
    parser.add_argument("--instance",  type=int, required=True, help="Instance number")
    parser.add_argument("--approach",  type=str, default="ortools", help="Approach name (key in JSON)")
    parser.add_argument("--output",    type=str, required=True, help="Output .json file path")
    parser.add_argument("--time-limit",type=int, default=300, help="Time limit in seconds")
    args = parser.parse_args()

    inst   = load_instance(args.instance)
    result = solve(inst, args.approach, args.time_limit)

    # Merge with existing file if present (multiple approaches in same json)
    try:
        with open(args.output, "r") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}

    existing.update(result)

    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Saved result to {args.output}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()