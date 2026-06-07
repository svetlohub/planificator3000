"""
BacklogBuilder

Wraps unallocated tasks into the Backlog domain model.

Rules
-----
- Task metadata is preserved exactly as received (no mutation).
- Order is preserved (Allocator produces backlog in task-pool order).
- Tasks are not re-sorted or filtered.
"""

from app.domain import Backlog, Task


class BacklogBuilder:
    """
    Builds a Backlog from the list of tasks that the Allocator could not schedule.

    Usage::

        builder = BacklogBuilder()
        backlog = builder.build(unallocated_tasks)
    """

    def build(self, unallocated_tasks: list[Task]) -> Backlog:
        """Return a Backlog containing all unallocated tasks in original order."""
        return Backlog(tasks=list(unallocated_tasks))
