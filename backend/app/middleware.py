from fastapi import Request
from fastapi.responses import JSONResponse


async def outage_middleware(request: Request, call_next):
    return JSONResponse(
        status_code=503,
        content={"detail": {"code": "service_unavailable"}},
    )
