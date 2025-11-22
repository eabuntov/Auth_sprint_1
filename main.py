from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.v1.api_router import api_router

app = FastAPI()

app.include_router(api_router)


@app.get("/health", response_class=JSONResponse)
async def healthcheck():
    """
    Простой healthcheck.
    Returns 200 OK если приложение живо.
    """
    return {"status": "ok"}
