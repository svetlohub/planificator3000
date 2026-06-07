"""
Planner

Collects tasks from all three sources and produces an ordered candidate
pool for the Allocator.

Inclusion rules
---------------
- Recurring tasks  → always included
- Monthly tasks    → always included
- Completed tasks  → included only when status != DONE
  (completed sheet tasks that are DONE are historical records, not work)

Ordering
--------
Tasks are sorted by:
  1. deadline ascending   (week_ref acts as the ISO week deadline proxy)
  2. estimate_hours ascending  (smaller tasks surface first within the same deadline)

This ordering is fully deterministic given the same input set.
"""

from app.domain import Task, TaskStatus


def _task_sort_key(task: Task) -> tuple[str, float]:
    """Return a stable sort key: (week_ref, estimate_hours)."""
    return (task.week_ref, task.estimate_hours)


class Planner:
    """
    Builds the ordered weekly task candidate pool.

    Usage::

        planner = Planner()
        candidates = planner.build_candidates(
            monthly_tasks=...,
            completed_tasks=...,
            recurring_tasks=...,
        )
    """

    def build_candidates(
        self,
        monthly_tasks: list[Task],
        completed_tasks: list[Task],
        recurring_tasks: list[Task],
    ) -> list[Task]:
        """
        Return a deduplicated, ordered list of tasks ready for allocation.

        Deduplication key: task_id.  If the same task_id appears in multiple
        sources the first occurrence (recurring > monthly > completed) wins.
        """
        seen: set[str] = set()
        pool: list[Task] = []

        # Source priority for dedup: recurring first so they are never dropped
        for task in [*recurring_tasks, *monthly_tasks]:
            if task.task_id not in seen:
                seen.add(task.task_id)
                pool.append(task)

        # Completed-source rows: skip truly finished work
        for task in completed_tasks:
            if task.task_id not in seen and task.status is not TaskStatus.DONE:
                seen.add(task.task_id)
                pool.append(task)

        return sorted(pool, key=_task_sort_key)
