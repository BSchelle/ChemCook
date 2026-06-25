from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.v1.routes.calculations import router as calculations_router


app = FastAPI(title="ChemCook API")


@app.exception_handler(ValueError)
async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(calculations_router, prefix="/api/v1")
