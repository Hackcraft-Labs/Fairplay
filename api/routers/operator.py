from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from db import init_db, reset_db

router = APIRouter()


@router.post("/reset-db")
def reset_database() -> dict[str, Any]:
    init_db()
    stats = reset_db()
    return {"ok": True, "deleted": stats}

