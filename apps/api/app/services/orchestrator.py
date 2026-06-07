"""
PlanningOrchestrator

The single service called by the API layer.  Routers never touch
CapacityEngine, Planner, Allocator, or BacklogBuilder directly.

Pipeline
--------
CapacityEngine → Planner → Allocator → BacklogBuilder → WeeklyPlanResult

Config integration
------------------
ConfigRow list is forwarded to CapacityEngine to extract buffer_percent.
If the list is empty or the key is absent the engine uses its default (25%).
"""

from app.connectors.sheets.schemas import ConfigRow
from app.domain import Task, TeamMember
from app.services.allocator import Allocator
from app.services.backlog import BacklogBuilder
from app.services.capacity import CapacityEngine
from app.services.planner import Planner
from app.services.schemas import WeeklyPlanResult


class PlanningOrchestrator:
    """
    Coordinates the full weekly planning cycle.

    Usage::

        orchestrator = PlanningOrchestrator()
        result = orchestrator.generate_weekly_plan(
            week_ref="2026-W25",
            monthly_tasks=...,
            completed_tasks=...,
            recurring_tasks=...,
            team_members=...,
            config_rows=...,
        )
    """

    def __init__(self) -> None:
        self._planner = Planner()
        self._allocator = Allocator()
        self._backlog_builder = BacklogBuilder()

    def generate_weekly_plan(
        self,
        week_ref: str,
        monthly_tasks: list[Task],
        completed_tasks: list[Task],
        recurring_tasks: list[Task],
        team_members: list[TeamMember],
        config_rows: list[ConfigRow] | None = None,
    ) -> WeeklyPlanResult:
        """
        Execute the full planning pipeline and return a WeeklyPlanResult.

        Parameters
        ----------
        week_ref        : ISO week string, e.g. "2026-W25"
        monthly_tasks   : tasks sourced from the Monthly Plan worksheet
        completed_tasks : tasks sourced from the Completed Tasks worksheet
        recurring_tasks : tasks sourced from the Recurring Tasks worksheet
        team_members    : team members with capacity data
        config_rows     : optional config rows read from the Config worksheet
        """
        # ── Step 1: build capacity snapshots ──────────────────────────────
        capacity_engine = CapacityEngine(config_rows or [])
        capacities = capacity_engine.build(team_members)

        # ── Step 2: build ordered task candidate pool ──────────────────────
        candidates = self._planner.build_candidates(
            monthly_tasks=monthly_tasks,
            completed_tasks=completed_tasks,
            recurring_tasks=recurring_tasks,
        )

        # ── Step 3: allocate tasks to team members ─────────────────────────
        allocations, unallocated = self._allocator.allocate(candidates, capacities)

        # ── Step 4: build backlog ──────────────────────────────────────────
        backlog = self._backlog_builder.build(unallocated)

        # ── Step 5: assemble result ────────────────────────────────────────
        scheduled_tasks: list[Task] = [
            task for allocation in allocations for task in allocation.tasks
        ]
        total_capacity = round(sum(c.available_hours for c in capacities), 10)
        planned_hours = round(sum(t.estimate_hours for t in scheduled_tasks), 10)
        backlog_hours = round(sum(t.estimate_hours for t in backlog.tasks), 10)

        return WeeklyPlanResult(
            week_ref=week_ref,
            scheduled_tasks=scheduled_tasks,
            backlog_tasks=backlog.tasks,
            allocations=allocations,
            team_capacity=capacities,
            total_capacity_hours=total_capacity,
            planned_hours=planned_hours,
            backlog_hours=backlog_hours,
        )
