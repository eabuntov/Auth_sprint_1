import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.v1.api_router import api_router

app = FastAPI()

with open("api/v1/openapi.json", "r", encoding="utf-8") as f:
    custom_openapi_schema = json.load(f)

def custom_openapi():
    return custom_openapi_schema

app.openapi = custom_openapi

app.include_router(api_router)


@app.get("/health", response_class=JSONResponse)
async def healthcheck():
    """
    Простой healthcheck.
    Returns 200 OK если приложение живо.
    """
    return {"status": "ok"}
