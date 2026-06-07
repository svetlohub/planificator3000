"""Plans router.

Endpoints
---------
GET /plans          — stub list (retained from Sprint 1)
GET /plans/current  — raw Sheets data as domain objects (Sprint 1)
GET /plans/generate — full planning cycle via PlanningOrchestrator (Sprint 2)
"""

from fastapi import APIRouter

from app.connectors.sheets import SheetsMapper
from app.dependencies import SettingsDep, SheetsRepositoryDep
from app.domain import Task, TeamMember
from app.schemas import CurrentPlanResponse, Plan
from app.services import PlanningOrchestrator, WeeklyPlanResult
from app.services.capacity import DEFAULT_BUFFER_PERCENT

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[Plan])
def list_plans() -> list[Plan]:
    return [
        Plan(title="Синхронизировать стратегию продукта", status="active"),
        Plan(title="Запустить первый production-инкремент", status="draft"),
    ]


@router.get("/current", response_model=CurrentPlanResponse)
def get_current_plan(
    repository: SheetsRepositoryDep,
    settings: SettingsDep,
) -> CurrentPlanResponse:
    """Load raw tasks and team roster from Sheets; return domain objects."""
    mapper = SheetsMapper()

    monthly_rows = repository.load_monthly_plan()
    completed_rows = repository.load_completed_tasks()
    recurring_rows = repository.load_recurring_tasks()
    team_rows = repository.load_team_roster()

    tasks: list[Task] = [
        *mapper.monthly_plan_to_domain_tasks(monthly_rows),
        *mapper.completed_tasks_to_domain(completed_rows),
        *mapper.recurring_tasks_to_domain(recurring_rows),
    ]
    team: list[TeamMember] = mapper.team_roster_to_domain(team_rows)

    return CurrentPlanResponse(
        tasks=tasks,
        team=team,
        sheets_configured=settings.sheets_configured,
    )


@router.get("/generate", response_model=WeeklyPlanResult)
def generate_plan(
    repository: SheetsRepositoryDep,
    settings: SettingsDep,
    week_ref: str = "2026-W25",
) -> WeeklyPlanResult:
    """
    Execute the full planning pipeline and return a WeeklyPlanResult.

    Steps
    -----
    1. Load all worksheets from Sheets.
    2. Map DTOs to domain models via SheetsMapper.
    3. Read Config sheet for buffer_percent (default 25 % if absent).
    4. Run PlanningOrchestrator.
    5. Return WeeklyPlanResult.

    This endpoint is read-only — no writes to Sheets occur.
    """
    mapper = SheetsMapper()

    monthly_tasks = mapper.monthly_plan_to_domain_tasks(repository.load_monthly_plan())
    completed_tasks = mapper.completed_tasks_to_domain(repository.load_completed_tasks())
    recurring_tasks = mapper.recurring_tasks_to_domain(repository.load_recurring_tasks())
    team_members = mapper.team_roster_to_domain(repository.load_team_roster())
    config_rows = repository.load_config()

    orchestrator = PlanningOrchestrator()
    return orchestrator.generate_weekly_plan(
        week_ref=week_ref,
        monthly_tasks=monthly_tasks,
        completed_tasks=completed_tasks,
        recurring_tasks=recurring_tasks,
        team_members=team_members,
        config_rows=config_rows,
    )
