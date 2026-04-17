"""
Operating Room Scheduling Problem (ORSP)
SAT/SMT model using Z3

Authors: Chiara Sivieri, Liam Busnelli Urso

Encoding strategy:
  - Boolean variables: assigned[s][d][r] — surgery s on day d in room r
  - Integer variables: start[s] — start time in minutes
  - No-overlap encoded via disjunctive constraints (big-M / order encoding)
  - Objective: minimize total overtime via Z3 Optimize

Usage:
    python3 orsp_sat.py --instance 1 --approach z3 --output /res/SAT/1.json
"""

import argparse
import json
import math
import time

import z3


# ── Instance loader ────────────────────────────────────────────────────────────

def load_instance(instance_number: int) -> dict:
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
            "surgeon":      [ 1,   2,  1,   3,  2,  3],
            "release_day":  [ 1,   1,  1,   1,  2,  2],
            "deadline":     [ 2,   2,  1,   2,  2,  2],
            "room_type":           [1, 1],
            "surgery_room_type":   [0, 0, 0, 0, 0, 0],
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


def is_compatible(s_idx, r_idx, inst):
    st = inst["surgery_room_type"][s_idx]
    rt = inst["room_type"][r_idx]
    return st == 0 or st == rt


# ── SAT/SMT model ──────────────────────────────────────────────────────────────

def solve(inst: dict, approach: str, time_limit: int = 300) -> dict:
    S        = inst["n_surgeries"]
    R        = inst["n_rooms"]
    D        = inst["n_days"]
    H        = inst["horizon"]
    soft_cap = inst["soft_cap"]
    eff_dur  = [inst["duration"][s] + inst["cleaning"][s] for s in range(S)]

    opt = z3.Optimize()
    opt.set("timeout", time_limit * 1000)   # Z3 timeout in milliseconds

    # ── Boolean assignment variables ──────────────────────────────────────────
    # assigned[s][d][r] = True iff surgery s is on day d in room r
    assigned = [[[z3.Bool(f"a_{s}_{d}_{r}")
                  for r in range(R)]
                 for d in range(D)]
                for s in range(S)]

    # ── Integer start-time variables ──────────────────────────────────────────
    start = [z3.Int(f"start_{s}") for s in range(S)]

    # ── C1: Each surgery assigned exactly once ────────────────────────────────
    for s in range(S):
        opt.add(
            z3.Sum([z3.If(assigned[s][d][r], 1, 0)
                    for d in range(D) for r in range(R)]) == 1
        )

    # ── C2: Domain of start times ─────────────────────────────────────────────
    for s in range(S):
        opt.add(start[s] >= 0)
        opt.add(start[s] + eff_dur[s] <= H)

    # ── C3: Release dates and deadlines ───────────────────────────────────────
    for s in range(S):
        rel = inst["release_day"][s] - 1
        dl  = inst["deadline"][s]  - 1
        for d in range(D):
            if d < rel or d > dl:
                for r in range(R):
                    opt.add(z3.Not(assigned[s][d][r]))

    # ── C4: Room compatibility ────────────────────────────────────────────────
    for s in range(S):
        for d in range(D):
            for r in range(R):
                if not is_compatible(s, r, inst):
                    opt.add(z3.Not(assigned[s][d][r]))

    # ── C5: No overlap in the same room on the same day ───────────────────────
    # If s1 and s2 are both in room r on day d, they must not overlap.
    # Encoded as: assigned[s1][d][r] ∧ assigned[s2][d][r] →
    #             start[s1]+eff[s1] ≤ start[s2] ∨ start[s2]+eff[s2] ≤ start[s1]
    for d in range(D):
        for r in range(R):
            for s1 in range(S):
                for s2 in range(s1 + 1, S):
                    both_here = z3.And(assigned[s1][d][r], assigned[s2][d][r])
                    no_overlap = z3.Or(
                        start[s1] + eff_dur[s1] <= start[s2],
                        start[s2] + eff_dur[s2] <= start[s1]
                    )
                    opt.add(z3.Implies(both_here, no_overlap))

    # ── C6: Same surgeon cannot overlap on the same day ───────────────────────
    surgeon_ids = list(set(inst["surgeon"]))
    for sg in surgeon_ids:
        surg_list = [s for s in range(S) if inst["surgeon"][s] == sg]
        for d in range(D):
            for i, s1 in enumerate(surg_list):
                for s2 in surg_list[i + 1:]:
                    s1_on_d = z3.Or([assigned[s1][d][r] for r in range(R)])
                    s2_on_d = z3.Or([assigned[s2][d][r] for r in range(R)])
                    both_on_d = z3.And(s1_on_d, s2_on_d)
                    no_overlap = z3.Or(
                        start[s1] + eff_dur[s1] <= start[s2],
                        start[s2] + eff_dur[s2] <= start[s1]
                    )
                    opt.add(z3.Implies(both_on_d, no_overlap))

    # ── Overtime and objective ────────────────────────────────────────────────
    overtime = []
    for s in range(S):
        ot = z3.Int(f"ot_{s}")
        opt.add(ot >= 0)
        opt.add(ot >= start[s] + eff_dur[s] - soft_cap)
        overtime.append(ot)

    total_overtime = z3.Int("total_overtime")
    opt.add(total_overtime == z3.Sum(overtime))
    opt.minimize(total_overtime)

    # ── Solve ─────────────────────────────────────────────────────────────────
    t0     = time.time()
    status = opt.check()
    elapsed = time.time() - t0

    is_feasible = (status == z3.sat)
    # Z3 Optimize does not distinguish OPTIMAL from FEASIBLE within timeout;
    # we mark optimal only if it finished before the time limit.
    is_optimal  = is_feasible and elapsed < time_limit - 1

    if is_feasible:
        model  = opt.model()
        obj_val = model[total_overtime].as_long()
        sol = []
        for s in range(S):
            for d in range(D):
                for r in range(R):
                    if z3.is_true(model[assigned[s][d][r]]):
                        sol.append({
                            "surgery": s + 1,
                            "day":     d + 1,
                            "room":    r + 1,
                            "start":   model[start[s]].as_long(),
                            "end":     model[start[s]].as_long() + eff_dur[s],
                        })
    else:
        obj_val = None
        sol     = []

    runtime = math.floor(elapsed)
    if not is_feasible:
        runtime = 300

    return {
        approach: {
            "time":    runtime,
            "optimal": is_optimal,
            "obj":     obj_val,
            "sol":     sol,
        }
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ORSP SAT/SMT solver (Z3)")
    parser.add_argument("--instance",   type=int, required=True)
    parser.add_argument("--approach",   type=str, default="z3")
    parser.add_argument("--output",     type=str, required=True)
    parser.add_argument("--time-limit", type=int, default=300)
    args = parser.parse_args()

    inst   = load_instance(args.instance)
    result = solve(inst, args.approach, args.time_limit)

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

    print(f"Saved to {args.output}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()