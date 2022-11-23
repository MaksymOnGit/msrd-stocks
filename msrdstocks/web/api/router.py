from fastapi.routing import APIRouter

from msrdstocks.web.api import docs, monitoring, stocks

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
