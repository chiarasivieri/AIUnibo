% ============================================================
%  Operating Room Scheduling Problem (ORSP)
%  CP model in MiniZinc
%  Decision + Optimization version
%  Authors: Chiara Sivieri, Liam Busnelli Urso
% ============================================================

% ------------------------------------------------------------
%  INSTANCE PARAMETERS
% ------------------------------------------------------------

int: n_surgeries;                             % number of surgeries to schedule
int: n_rooms;                                 % number of operating rooms
int: n_days;                                  % planning horizon in days
int: horizon;                                 % minutes available per room per day
int: n_surgeons;                              % number of surgeons
int: n_room_types;                            % number of distinct room types
int: soft_cap;                                % soft daily limit per room (minutes)

array[1..n_surgeries] of int: duration;       % surgery duration (minutes)
array[1..n_surgeries] of int: cleaning;       % mandatory cleaning after surgery (minutes)
array[1..n_surgeries] of 1..n_surgeons: surgeon;     % surgeon assigned to each surgery
array[1..n_surgeries] of 1..n_days:   release_day;   % earliest schedulable day
array[1..n_surgeries] of 1..n_days:   deadline;      % latest schedulable day
array[1..n_surgeries] of 0..n_room_types: surgery_room_type; % required room type (0 = any)
array[1..n_rooms]     of 1..n_room_types: room_type;         % type of each room

% ------------------------------------------------------------
%  DERIVED PARAMETERS
% ------------------------------------------------------------

% Effective duration including mandatory post-surgery cleaning
array[1..n_surgeries] of int: eff_dur =
    [ duration[s] + cleaning[s] | s in 1..n_surgeries ];

% Compatibility matrix: can surgery s be performed in room r?
array[1..n_surgeries, 1..n_rooms] of bool: compatible =
    array2d(1..n_surgeries, 1..n_rooms,
        [ surgery_room_type[s] = 0 \/ surgery_room_type[s] = room_type[r]
          | s in 1..n_surgeries, r in 1..n_rooms ]);

% ------------------------------------------------------------
%  DECISION VARIABLES
% ------------------------------------------------------------

array[1..n_surgeries] of var 1..n_days:    day;    % assigned day
array[1..n_surgeries] of var 1..n_rooms:   room;   % assigned room
array[1..n_surgeries] of var 0..horizon-1: start;  % start time within assigned day (minutes)

% Derived: end time of each surgery (including cleaning)
array[1..n_surgeries] of var 1..horizon: end_time =
    [ start[s] + eff_dur[s] | s in 1..n_surgeries ];

% ------------------------------------------------------------
%  HARD CONSTRAINTS
% ------------------------------------------------------------

% C1: Respect release dates and deadlines
constraint forall(s in 1..n_surgeries)(
    day[s] >= release_day[s] /\ day[s] <= deadline[s]
);

% C2: Surgery (+ cleaning) must finish within the daily horizon
constraint forall(s in 1..n_surgeries)(
    end_time[s] <= horizon
);

% C3: Assigned room must be compatible with the surgery type
constraint forall(s in 1..n_surgeries)(
    compatible[s, room[s]]
);

% C4: No two surgeries overlap in the same room on the same day
constraint forall(s1 in 1..n_surgeries, s2 in s1+1..n_surgeries)(
    (room[s1] = room[s2] /\ day[s1] = day[s2]) ->
    (end_time[s1] <= start[s2] \/ end_time[s2] <= start[s1])
);

% C5: The same surgeon cannot perform two surgeries simultaneously
constraint forall(s1 in 1..n_surgeries, s2 in s1+1..n_surgeries)(
    (surgeon[s1] = surgeon[s2] /\ day[s1] = day[s2]) ->
    (end_time[s1] <= start[s2] \/ end_time[s2] <= start[s1])
);

% ------------------------------------------------------------
%  IMPLIED CONSTRAINTS
% ------------------------------------------------------------

% IC1: Total effective duration in a room on a day cannot exceed horizon.
%      This is implied by C2+C4 but speeds up propagation significantly.
constraint forall(r in 1..n_rooms, d in 1..n_days)(
    sum(s in 1..n_surgeries)(
        eff_dur[s] * bool2int(room[s] = r /\ day[s] = d)
    ) <= horizon
);

% IC2: Total effective duration per surgeon per day cannot exceed horizon.
%      Implied by C2+C5, helps prune surgeon overload early.
constraint forall(sg in 1..n_surgeons, d in 1..n_days)(
    sum(s in 1..n_surgeries where surgeon[s] = sg)(
        eff_dur[s] * bool2int(day[s] = d)
    ) <= horizon
);

% IC3: Each surgery must start early enough to finish before horizon.
%      Redundant with C2 but makes the domain tighter immediately.
constraint forall(s in 1..n_surgeries)(
    start[s] <= horizon - eff_dur[s]
);

% ------------------------------------------------------------
%  SYMMETRY BREAKING
% ------------------------------------------------------------

% SB1: Among surgeries performed by the same surgeon on the same day,
%      order by surgery index to fix one canonical ordering.
%      This does not conflict with any hard constraint.
constraint forall(s1 in 1..n_surgeries, s2 in s1+1..n_surgeries)(
    (surgeon[s1] = surgeon[s2] /\ day[s1] = day[s2]) ->
    start[s1] <= start[s2]
);

% ------------------------------------------------------------
%  OBJECTIVE
% ------------------------------------------------------------

% Overtime of surgery s: how many minutes it pushes beyond the soft cap.
% A surgery ending at minute 450 with soft_cap=420 contributes 30 min overtime.
array[1..n_surgeries] of var 0..horizon: overtime =
    [ max(0, end_time[s] - soft_cap) | s in 1..n_surgeries ];

% Total overtime across all surgeries (objective to minimize)
var 0..n_surgeries * horizon: total_overtime = sum(s in 1..n_surgeries)(overtime[s]);

% Tight bounds to help the solver prune faster
constraint total_overtime >= 0;
constraint total_overtime <= sum(s in 1..n_surgeries)(
    max(0, eff_dur[s] - soft_cap)
);

% ------------------------------------------------------------
%  SEARCH STRATEGY
% ------------------------------------------------------------

% Strategy: assign days first (most constrained by deadlines),
% then rooms (compatibility pruning), then start times.
% Does not conflict with SB1 (which only constrains relative ordering
% of start times, not their absolute assignment order).

solve
    :: seq_search([
        int_search(day,   smallest_domain, indomain_min),
        int_search(room,  smallest_domain, indomain_min),
        int_search(start, smallest_domain, indomain_min)
    ])
    minimize total_overtime;

% To run decision version only, replace with:
% solve satisfy;


%  OUTPUT

output [
    "=== ORSP Solution ===\n",
    "Surgery | Day | Room | Start | End  | Overtime\n",
    "--------|-----|------|-------|-----|----------\n"
] ++
[
    "   " ++ show(s) ++
    "    |  " ++ show(day[s]) ++
    "  |  "  ++ show(room[s]) ++
    "  | "   ++ show(start[s]) ++
    "   | "  ++ show(end_time[s]) ++
    "  |  "  ++ show(overtime[s]) ++ "\n"
    | s in 1..n_surgeries
] ++
["\nTotal overtime: ", show(total_overtime), " min\n"];
