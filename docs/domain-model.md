# Domain Model

The ПЛАНИФИКАТОР-3000 domain layer is intentionally small. It defines stable data contracts and invariants only; it does not contain planner algorithms, Google Sheets integration, prioritization rules, or scheduling business logic.

## Entities

### Task

`Task` is the normalized unit of work. It contains identifiers, ownership metadata, source, status, estimate, type, and the week reference that places the task into a planning window.

Important fields:

- `task_id` — external or internal stable task identifier.
- `title` — human-readable task name.
- `source` — one of `completed`, `monthly`, `recurring`, `carry_over`.
- `status` — one of `done`, `pending`, `planned`, `in_progress`.
- `owner` — accountable person for the task.
- `assignee` — execution assignee; it can be empty while a task is still unassigned.
- `estimate_hours` — effort estimate using quarter-hour precision.
- `task_type` — domain tag such as planning, reporting, engineering, or operations.
- `week_ref` — planning week in `YYYY-Www` format.

Computed properties:

- `is_completed`
- `is_assigned`

### TeamMember

`TeamMember` describes a person that can receive work. It stores weekly capacity, a reserved buffer, and normalized skills. Skills are metadata for downstream use cases and are not used by this layer to make planning decisions.

Computed properties:

- `buffer_hours`
- `available_capacity_hours`

### Capacity

`Capacity` is a weekly capacity snapshot for one member. It stores total hours, reserved buffer hours, and available hours. The model validates that available hours equal total hours minus buffer hours.

Computed property:

- `buffer_percent`

### WeeklyPlan

`WeeklyPlan` groups tasks for a single `week_ref`. It validates that every nested task belongs to the same week as the plan.

Computed properties:

- `total_estimate_hours`
- `planned_tasks_count`
- `completed_tasks_count`

### Allocation

`Allocation` groups tasks assigned to one person. It validates that nested tasks have the same assignee and that `allocated_hours` equals the sum of task estimates.

Computed property:

- `tasks_count`

### Backlog

`Backlog` is the holding area for known tasks that are not necessarily part of an active weekly plan. It keeps the domain aware of work that exists without forcing the planning engine to schedule it immediately.

Computed properties:

- `tasks_count`
- `total_estimate_hours`

### WeeklyReport

`WeeklyReport` is a read-model contract for weekly reporting. It captures the week reference, completed task count, active task count, and summary lines.

Computed properties:

- `total_referenced_tasks_count`
- `has_activity`

## Relationships

- `WeeklyPlan` contains many `Task` objects for exactly one `week_ref`.
- `Allocation` contains many `Task` objects for exactly one `assignee`.
- `Backlog` contains many `Task` objects without implying that they are planned or allocated.
- `Capacity` references a team member by `member_name`; it is a snapshot, not the source of truth for the person.
- `WeeklyReport` references task activity by aggregate counts and summary lines instead of embedding task objects.

## Why there is no `priority`

Priority is intentionally excluded from the core domain contract because it is a policy decision, not a stable entity attribute at this stage. Different inputs can express urgency differently: source order, stakeholder signal, deadlines, carry-over age, or manual ranking. Adding `priority` too early would make the domain model look deterministic while the actual prioritization policy is still undefined.

When prioritization rules become explicit, they should be introduced as a separate policy or scoring contract rather than a casual field on `Task`.

## Why there are no `dependencies`

Dependencies are also excluded by design. A dependency graph implies ordering semantics, cycle handling, blocked states, and planner behavior. Those concerns belong to planner logic, not to the base domain contracts requested here.

The current layer can serialize and validate tasks safely without deciding whether one task blocks another. A future planning module can add dependency-specific contracts once dependency behavior is defined.

## Role of the backlog

The backlog is the buffer between task discovery and weekly execution. It lets the system preserve known work from monthly inputs, recurring inputs, carry-over items, or other sources without forcing every item into a plan.

In this domain layer, backlog is only a typed collection with simple aggregate computed properties. It does not sort, prioritize, allocate, or schedule tasks.
