# Planning Engine

Deterministic weekly planning engine for ПЛАНИФИКАТОР-3000.

All components are rule-based. No LLMs, no scoring, no priorities.
Given the same input the engine produces the same output on every run.

---

## Architecture

```
Google Sheets
    │
    ▼
SheetsRepository  ──► DTOs (CompletedTaskRow, MonthlyPlanRow, ...)
    │
    ▼
SheetsMapper  ──► Domain models (Task, TeamMember, ConfigRow)
    │
    ▼
PlanningOrchestrator
    │
    ├─► CapacityEngine  ──► List[Capacity]
    │
    ├─► Planner  ──► List[Task]  (ordered candidates)
    │
    ├─► Allocator  ──► List[Allocation] + List[Task] (unallocated)
    │
    ├─► BacklogBuilder  ──► Backlog
    │
    └─► WeeklyPlanResult
```

Location: `apps/api/app/services/`

---

## CapacityEngine

**File:** `services/capacity.py`

Converts `TeamMember` domain objects into `Capacity` snapshots.

### Rules

| Condition | Buffer used |
|---|---|
| `member.reserved_buffer_percent != 0` | member's own value |
| `member.reserved_buffer_percent == 0` | global config value |
| config key `buffer_percent` absent / invalid | `DEFAULT_BUFFER_PERCENT = 25.0` |

### Calculation

```
buffer_hours    = total_hours × (buffer_percent / 100)
available_hours = total_hours − buffer_hours
```

### Config integration

`CapacityEngine` accepts a `list[ConfigRow]` in its constructor.
It reads the key `"buffer_percent"` (case-insensitive).
Values outside `[0, 100]` or non-numeric values are ignored and the default is used.

### Example

```python
engine = CapacityEngine(config_rows)
capacities = engine.build(team_members)
# Ivan 40h, buffer 25% → available_hours = 30.0
```

---

## Planner

**File:** `services/planner.py`

Builds the ordered task candidate pool for the Allocator.

### Inclusion rules

| Source | Included |
|---|---|
| `recurring_tasks` | Always |
| `monthly_tasks` | Always |
| `completed_tasks` where `status != DONE` | Yes |
| `completed_tasks` where `status == DONE` | **No** — historical records only |

### Deduplication

Dedup key: `task_id`.
Priority when the same `task_id` appears in multiple sources:
1. Recurring
2. Monthly
3. Completed (non-done)

The first occurrence wins. Lower-priority duplicates are silently dropped.

### Ordering

Tasks are sorted by:
1. `week_ref` ascending (ISO week string; lexicographic sort is correct for `YYYY-Wnn`)
2. `estimate_hours` ascending (shorter tasks first within the same week)

This ordering is stable and deterministic.

### Example

```
Input:
  recurring: [standup 0.25h W25]
  monthly:   [spec 4h W25, review 1h W25]

After sort:
  [standup 0.25h W25, review 1h W25, spec 4h W25]
```

---

## Allocator

**File:** `services/allocator.py`

Assigns tasks to team members using **Greedy Balanced Allocation**.

### Algorithm

```
for each task in ordered_candidates:
    1. if task.owner matches a team member AND owner has capacity:
           assign to owner
    2. else:
           sort members by allocated_hours ascending
           assign to first member who can fit the task
    3. if no member can fit:
           task → backlog
```

### Invariants

- `allocated_hours ≤ available_hours` for every member at all times.
- A task is never split across members.
- Each task appears exactly once: either in an Allocation or in the backlog.

### Owner affinity

`task.owner` is used as a soft preference, not a hard constraint.
If the owner is over capacity the task is offered to the next available member.
If no member can fit it the task goes to backlog.

### Output

- `List[Allocation]` — one entry per member who received at least one task.
- `List[Task]` — unallocated tasks in original pool order.

---

## BacklogBuilder

**File:** `services/backlog.py`

Wraps the Allocator's unallocated task list into a `Backlog` domain object.

### Rules

- Task metadata is never mutated.
- Input order is preserved.
- No filtering or re-sorting.

---

## PlanningOrchestrator

**File:** `services/orchestrator.py`

The **single entry point** for the planning pipeline.
Routers never call `Planner`, `Allocator`, or `CapacityEngine` directly.

### Public API

```python
orchestrator = PlanningOrchestrator()
result: WeeklyPlanResult = orchestrator.generate_weekly_plan(
    week_ref="2026-W25",
    monthly_tasks=[...],
    completed_tasks=[...],
    recurring_tasks=[...],
    team_members=[...],
    config_rows=[...],   # optional; empty list uses defaults
)
```

### Pipeline steps

1. `CapacityEngine(config_rows).build(team_members)` → `capacities`
2. `Planner().build_candidates(...)` → `candidates`
3. `Allocator().allocate(candidates, capacities)` → `allocations, unallocated`
4. `BacklogBuilder().build(unallocated)` → `backlog`
5. Assemble `WeeklyPlanResult`

---

## WeeklyPlanResult

**File:** `services/schemas.py`

Pydantic v2 model with `extra="forbid"` and `frozen=True`.

| Field | Type | Description |
|---|---|---|
| `week_ref` | `str` | ISO week, e.g. `"2026-W25"` |
| `scheduled_tasks` | `list[Task]` | Tasks that were allocated |
| `backlog_tasks` | `list[Task]` | Tasks that could not be scheduled |
| `allocations` | `list[Allocation]` | Per-member allocation objects |
| `team_capacity` | `list[Capacity]` | Capacity snapshots for every member |
| `total_capacity_hours` | `float` | Sum of `available_hours` across team |
| `planned_hours` | `float` | Sum of `estimate_hours` of scheduled tasks |
| `backlog_hours` | `float` | Sum of `estimate_hours` of backlog tasks |

### Invariants enforced by validators

- `planned_hours == sum(task.estimate_hours for task in scheduled_tasks)`
- `backlog_hours == sum(task.estimate_hours for task in backlog_tasks)`

---

## Scheduling rules summary

| Rule | Enforced by |
|---|---|
| Recurring tasks always enter the pool | `Planner` |
| DONE tasks never enter the pool | `Planner` |
| Shorter tasks scheduled first (within same week) | `Planner` (sort) |
| Owner receives their tasks when capacity allows | `Allocator` |
| Team load balanced across members | `Allocator` (sort by allocated_hours) |
| Capacity never exceeded | `Allocator` (can_fit guard) |
| Unscheduled tasks preserved in backlog | `BacklogBuilder` + `WeeklyPlanResult` |
| Config buffer_percent overrides 25% default | `CapacityEngine` |

---

## API endpoint

```
GET /api/v1/plans/generate?week_ref=2026-W25
```

Response: `WeeklyPlanResult` JSON.

The endpoint is **read-only** — it does not write to Google Sheets.

The `week_ref` query parameter defaults to `"2026-W25"`.
It must match the ISO week pattern `YYYY-Wnn`.
