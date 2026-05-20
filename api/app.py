from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import detections, iocs, operator

app = FastAPI(title="Fairplay API", version="1.0")

# local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detections.router, prefix="/detections", tags=["detections"])
app.include_router(iocs.router, prefix="/iocs", tags=["iocs"])
app.include_router(operator.router, prefix="/ops", tags=["ops"])

