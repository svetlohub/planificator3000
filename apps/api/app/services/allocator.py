"""
Allocator

Assigns tasks to team members using a greedy balanced algorithm.

Algorithm: Greedy Balanced Allocation
--------------------------------------
For each task (in the order supplied by the Planner):
  1. Sort team members by currently allocated hours (ascending).
  2. Find the first member whose remaining capacity >= task.estimate_hours.
  3. If found  → assign task to that member.
  4. If not found → task goes to backlog.

Invariant: allocated_hours never exceeds available_hours for any member.

Owner affinity
--------------
If task.owner matches a team member name the task is offered to that
member first before the balanced-load fallback.  This preserves
the sheet's owner intent without making it mandatory (the owner may
be over capacity, in which case the next available member takes it).

The algorithm is deterministic given:
  - a fixed task order
  - a fixed team list
  - stable sort (Python's sort is stable)
"""

from dataclasses import dataclass, field

from app.domain import Allocation, Capacity, Task


@dataclass
class _MemberSlot:
    """Mutable allocation accumulator for one team member."""

    capacity: Capacity
    tasks: list[Task] = field(default_factory=list)
    allocated_hours: float = 0.0

    @property
    def remaining_hours(self) -> float:
        return round(self.capacity.available_hours - self.allocated_hours, 10)

    def can_fit(self, task: Task) -> bool:
        return self.remaining_hours >= task.estimate_hours - 1e-9

    def assign(self, task: Task) -> None:
        self.tasks.append(task)
        self.allocated_hours = round(self.allocated_hours + task.estimate_hours, 10)


def _build_assigned_task(task: Task, assignee: str) -> Task:
    """Return a copy of the task with the assignee field set."""
    return task.model_copy(update={"assignee": assignee})


class Allocator:
    """
    Greedy balanced task allocator.

    Usage::

        allocator = Allocator()
        allocations, backlog_tasks = allocator.allocate(tasks, capacities)
    """

    def allocate(
        self,
        tasks: list[Task],
        capacities: list[Capacity],
    ) -> tuple[list[Allocation], list[Task]]:
        """
        Assign tasks to team members.

        Returns
        -------
        allocations  : one Allocation per member who received at least one task
        backlog_tasks: tasks that could not be scheduled
        """
        if not capacities:
            return [], list(tasks)

        slots: dict[str, _MemberSlot] = {
            cap.member_name: _MemberSlot(capacity=cap) for cap in capacities
        }
        backlog: list[Task] = []

        for task in tasks:
            assigned = self._try_assign(task, slots)
            if not assigned:
                backlog.append(task)

        allocations = [
            Allocation(
                assignee=slot.capacity.member_name,
                tasks=slot.tasks,
                allocated_hours=slot.allocated_hours,
            )
            for slot in slots.values()
            if slot.tasks
        ]
        return allocations, backlog

    # ------------------------------------------------------------------ private

    def _try_assign(self, task: Task, slots: dict[str, _MemberSlot]) -> bool:
        """
        Attempt to assign task to a member.

        Returns True when a slot was found and the task was assigned.
        """
        # 1. Try owner affinity first
        if task.owner and task.owner in slots:
            owner_slot = slots[task.owner]
            if owner_slot.can_fit(task):
                owner_slot.assign(_build_assigned_task(task, task.owner))
                return True

        # 2. Greedy balanced: pick least-loaded member who can fit the task
        ordered = sorted(slots.values(), key=lambda s: s.allocated_hours)
        for slot in ordered:
            if slot.can_fit(task):
                slot.assign(_build_assigned_task(task, slot.capacity.member_name))
                return True

        return False
