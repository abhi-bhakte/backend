from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.transportation import router as transportation_router
from app.api.v1.composting import router as composting_router
from app.api.v1.anaerobic_digestion import router as anaerobic_digestion_router
from app.api.v1.recycling import router as recycling_router
from app.api.v1.incineration import router as incineration_router
from app.api.v1.landfill import router as landfill_router
from app.api.v1.save_data import router as save_data_router
from app.api.v1.auth import router as auth_router
from app.api.v1.permissions import router as permissions_router
from app.middleware.auth import AuthMiddleware



def register_routes(app: FastAPI):
    


    app.add_middleware(
        AuthMiddleware,
        exempt_paths=[
            "/api/v1/login",
            "/api/v1/register",
            "/docs",         
            
        ]
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (you can restrict this to specific domains)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

    # Include API routes
    app.include_router(transportation_router, prefix="/api/v1/transportation", tags=["Transportation"])
    app.include_router(composting_router, prefix="/api/v1/composting", tags=["Composting"])
    app.include_router(anaerobic_digestion_router, prefix="/api/v1/anaerobic_digestion", tags=["Anaerobic Digestion"])
    app.include_router(recycling_router, prefix="/api/v1/recycling", tags=["Recycling"])
    app.include_router(incineration_router, prefix="/api/v1/incineration", tags=["Incineration"])
    app.include_router(landfill_router, prefix="/api/v1/landfill", tags=["Landfill"])
    app.include_router(save_data_router, prefix="/api/v1", tags=["Save Data"])
    app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
    app.include_router(permissions_router, prefix="/api/v1", tags=["Permissions"])




app = FastAPI(title="GHG Accounting API")
register_routes(app)