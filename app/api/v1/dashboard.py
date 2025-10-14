

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from app.db.db import get_db
from app.services.dashboard_service import get_city_summary_service
from app.models.dashboard_models import CitySummaryResponse
from app.utils.auth import verify_token

router = APIRouter(tags=["Dashboard"])


@router.get("/city-summary", summary="Get city waste summary for a time range (IST)", response_model=CitySummaryResponse)
async def get_city_summary(
    city_name: str = Query(...),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD"),
    db=Depends(get_db),
    authorization: str = Header(None)
):
    """
    Returns city waste summary for the full days between start_date and end_date (inclusive), in IST.
    The backend always interprets each date as 00:00 to 23:59:59 IST.
    Restricts regular users to only their allowed cities.
    """
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ", 1)[1]
    user_payload = verify_token(token)
    role = user_payload.get("role")
    accessible_cities = user_payload.get("accessibleCities", [])
    # Restrict regular users
    if role == "regular" and city_name not in accessible_cities:
        raise HTTPException(status_code=403, detail="You do not have access to this city.")
    try:
        result = await get_city_summary_service(city_name, start_date, end_date, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
