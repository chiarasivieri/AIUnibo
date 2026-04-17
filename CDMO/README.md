# CDMO Project – Operating Room Scheduling Problem (ORSP)

**Course:** Combinatorial Decision Making & Optimization 
**Authors:** Chiara Sivieri, Liam Busnelli Urso  
**University:** Università di Bologna

---

## Problem Description

The **Operating Room Scheduling Problem (ORSP)** consists of assigning a set of elective surgical cases to operating rooms and time slots over a planning horizon, while satisfying a set of hard constraints and optimizing a set of soft objectives.

**Hard constraints:**
- Each surgery must be assigned to a compatible operating room
- No two surgeries can overlap in the same room on the same day
- No surgeon can perform two surgeries simultaneously
- Each surgery must be scheduled within its release date and deadline
- Each surgery (including cleaning time) must fit within the daily time horizon

**Optimization objective:**
- Minimize total overtime — the excess of surgery end times beyond a soft daily capacity cap per room

---

## Repository Structure

```
CDMO_Proj_SivieriChiara_BusnelliUrsoLiam/
│
├── README.md                      # this file
│
├── source/
│   ├── Dockerfile                 # reproducible environment
│   ├── run_all.sh                 # runs all models on all instances
│   │
│   ├── CP/
│   │   ├── orsp.mzn               # MiniZinc model
│   │   ├── instances/             # .dzn instance files
│   │   └── run.sh                 # run CP on a single instance
│   │
│   ├── SAT/                       # SAT/SMT model (Z3)
│   │   ├── orsp_sat.py
│   │   └── run.sh
│   │
│   └── MIP/
│       ├── orsp_mip.py            # MIP model (Python)
│       └── run.sh
│
├── res/
│   ├── CP/                        # results as .json per instance
│   ├── SAT/
│   └── MIP/
│
└── report/
    ├── report.tex
    └── references.bib
```

---

## Requirements

All solvers run inside Docker. Build the image once and use it for all models.

```bash
cd source/
docker build -t cdmo_orsp .
```

---

## How to Run

### Run a single model on a single instance

Each approach has a `run.sh` script that takes two arguments:
- `APPROACH`: the solver/configuration name (used as key in the output `.json`)
- `INSTANCE`: the instance number (e.g. `1`, `2`, ...)

**CP (MiniZinc + Gecode):**
```bash
docker run --rm -v $(pwd)/res:/res cdmo_orsp \
  bash source/CP/run.sh gecode 1
```

**SAT/SMT (Z3):**
```bash
docker run --rm -v $(pwd)/res:/res cdmo_orsp \
  bash source/SAT/run.sh z3 1
```

**MIP (Python):**
```bash
docker run --rm -v $(pwd)/res:/res cdmo_orsp \
  bash source/MIP/run.sh mip 1
```

Results are saved to `res/<APPROACH>/<INSTANCE>.json`.

---

### Run all models on all instances

```bash
docker run --rm -v $(pwd)/res:/res cdmo_orsp bash source/run_all.sh
```

This generates all feasible `.json` result files under `res/`.

---

## Output Format

Each `.json` result file follows the format required by the course checker:

```json
{
  "gecode": {
    "time": 42,
    "optimal": true,
    "obj": 15,
    "sol": [
      { "surgery": 1, "day": 1, "room": 2, "start": 0 },
      ...
    ]
  }
}
```

| Field | Description |
|---|---|
| `time` | Floor of runtime in seconds (300 if timeout) |
| `optimal` | `true` if solved to optimality, `false` otherwise |
| `obj` | Objective value (total overtime in minutes), `null` for decision version |
| `sol` | List of assignments: surgery → day, room, start time |

---

## Solution Checker

Before submission, verify all results with the official checker:

```bash
python check_solution.py res/CP/1.json
```

The checker is provided by the course instructors and must not be modified.

---

## Time Limit

All solvers are run with a **300-second (5-minute) time limit** in sequential mode (single core).

---

## References

- Cardoen, B., Demeulemeester, E., Beliën, J. (2010). *Operating room planning and scheduling: A literature review.* European Journal of Operational Research, 201(3), 921–932.
- Zhu, S., Fan, W., Yang, S., Pei, J., & Pardalos, P. M. (2019). *Operating room planning and surgical case scheduling: a review of literature.* Journal of Combinatorial Optimization, 37(3), 757–805.
- Roshanaei, V., Booth, K. E. C., Aleman, D. M., Urbach, D. R., & Beck, J. C. (2020). *Branch-and-check methods for multi-level operating room planning and scheduling.* International Journal of Production Economics, 220.