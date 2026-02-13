from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.transportation import router as transportation_router
from app.api.v1.composting import router as composting_router
from app.api.v1.anaerobic_digestion import router as anaerobic_digestion_router
from app.api.v1.recycling import router as recycling_router
from app.api.v1.incineration import router as incineration_router
from app.api.v1.landfill import router as landfill_router
from app.api.v1.waste_input_api.waste_input import router as waste_input_router
from app.api.v1.auth import router as auth_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.scenario import router as scenario_router
from app.api.v1.db_database import router as db_router
from app.api.v1.reference_data import router as reference_data_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.profile import router as profile_router
from app.middleware.auth import AuthMiddleware



def register_routes(app: FastAPI):


    # Add CORS middleware (first to ensure it applies to all routes)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://calc.greenaadhaar.in",
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ],  # Allow all relevant origins for local dev and prod
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
        expose_headers=["Retry-After"],
    )
    

    # Add Auth middleware AFTER CORS
    app.add_middleware(
        AuthMiddleware,
        exempt_paths=[
            "/",  # Exempt root path
            "/api/v1/login",
            "/api/v1/register",
            "/docs",
            "/openapi.json", 
            
        ]
    )

    

    # Include API routes
    app.include_router(transportation_router, prefix="/api/v1/transportation", tags=["Calculation"])
    app.include_router(composting_router, prefix="/api/v1/composting", tags=["Calculation"])
    app.include_router(anaerobic_digestion_router, prefix="/api/v1/anaerobic_digestion", tags=["Calculation"])
    app.include_router(recycling_router, prefix="/api/v1/recycling", tags=["Calculation"])
    app.include_router(incineration_router, prefix="/api/v1/incineration", tags=["Calculation"])
    app.include_router(landfill_router, prefix="/api/v1/landfill", tags=["Calculation"])
    app.include_router(waste_input_router, prefix="/api/v1/waste_data", tags=["Waste Data"])
    app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
    app.include_router(permissions_router, prefix="/api/v1", tags=["Permissions"])
    app.include_router(scenario_router, prefix="/api/v1/scenario", tags=["Scenario"])
    app.include_router(db_router, prefix="/api/v1/db_database", tags=["DB Database"])
    app.include_router(reference_data_router, prefix="/api/v1/db_database", tags=["Reference Data"])
    app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
    app.include_router(profile_router, prefix="/api/v1", tags=["Profile"])




app = FastAPI(title="GHG Accounting API")
register_routes(app)
