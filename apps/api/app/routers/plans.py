from fastapi import APIRouter

from app.schemas import Plan

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[Plan])
def list_plans() -> list[Plan]:
    return [
        Plan(title="Синхронизировать стратегию продукта", status="active"),
        Plan(title="Запустить первый production-инкремент", status="draft"),
    ]
