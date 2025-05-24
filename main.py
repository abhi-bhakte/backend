from fastapi import FastAPI
from app.routes.main import register_routes
from app.db.db import connect_to_mongodb

app = FastAPI(title="GHG Accounting API")

register_routes(app)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongodb()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
