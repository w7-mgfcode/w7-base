"""Reliquary API — boilerplate entry point.

Boilerplate phase: only /health and /version are implemented.
Real game endpoints land after STORYBOARD.md and ARCHITECTURE.md §4 are signed off.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Reliquary API",
    version="0.0.0-boilerplate",
)

cors_origins = [
    o.strip()
    for o in os.environ.get("API_CORS_ORIGINS", "http://localhost:4242").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "reliquary-api", "phase": "boilerplate"}


@app.get("/version")
async def version() -> dict[str, str]:
    return {"version": app.version}
