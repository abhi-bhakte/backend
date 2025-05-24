from fastapi import APIRouter
from .transportation import router as transportation_router
from .composting import router as composting_router
from .anaerobic_digestion import router as anaerobic_digestion_router
from .recycling import router as recycling_router
from .incineration import router as incineration_router
from .landfill import router as landfill_router

# Create a main router to include all sub-routers
router = APIRouter()
router.include_router(transportation_router, prefix="/transportation", tags=["Transportation"])
router.include_router(composting_router, prefix="/composting", tags=["Composting"])
router.include_router(anaerobic_digestion_router, prefix="/anaerobic-digestion", tags=["Anaerobic Digestion"])
router.include_router(recycling_router, prefix="/recycling", tags=["Recycling"])
router.include_router(incineration_router, prefix="/incineration", tags=["Incineration"])
router.include_router(landfill_router, prefix="/landfill", tags=["Landfill"])

__all__ = ["router"]


