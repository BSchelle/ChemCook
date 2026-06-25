from fastapi import APIRouter

from backend.app.models.calculation import CalculationCreate, CalculationRead
from backend.app.services import calculation_service


router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.post("/preview", response_model=CalculationRead)
async def preview_calculation(payload: CalculationCreate) -> CalculationRead:
    return calculation_service.compute_reaction_calculation(payload)
