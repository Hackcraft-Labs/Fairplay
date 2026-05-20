from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException

from ioc import add_ioc, load_iocs

router = APIRouter()


@router.get("/")
def iocs_list() -> list[dict[str, Any]]:
    return load_iocs()


@router.get("/{name}")
def iocs_get(name: str) -> dict[str, Any]:
    iocs = load_iocs()
    for ioc in iocs:
        if ioc.get("name") == name:
            return ioc
    raise HTTPException(status_code=404, detail="IOC not found")


@router.post("/")
def iocs_create(payload: dict[str, Any]) -> dict[str, Any]:
    name = payload.get("name")
    file_hash = payload.get("file_hash")
    poll_time = payload.get("poll_time", 60)

    if not name or not file_hash:
        raise HTTPException(status_code=400, detail="name and file_hash are required")
    if not isinstance(poll_time, int):
        raise HTTPException(status_code=400, detail="poll_time must be an integer (minutes)")

    if not add_ioc(name, file_hash, poll_time=poll_time):
        raise HTTPException(status_code=500, detail="Failed to create IOC")

    return iocs_get(name)


@router.put("/{name}")
def iocs_update(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Update by rewriting the IOC JSON file (keeps behavior aligned with existing design).
    """
    file_hash = payload.get("file_hash")
    poll_time = payload.get("poll_time", 60)
    new_name = payload.get("name", name)

    if not file_hash:
        raise HTTPException(status_code=400, detail="file_hash is required")
    if not isinstance(poll_time, int):
        raise HTTPException(status_code=400, detail="poll_time must be an integer (minutes)")

    # Rename file if needed.
    old_path = os.path.join("ioc", f"{name}.json")
    new_path = os.path.join("ioc", f"{new_name}.json")
    if name != new_name and os.path.exists(old_path):
        try:
            os.replace(old_path, new_path)
        except OSError:
            raise HTTPException(status_code=500, detail="Failed to rename IOC file")

    if not add_ioc(new_name, file_hash, poll_time=poll_time):
        raise HTTPException(status_code=500, detail="Failed to update IOC")

    return iocs_get(new_name)


@router.delete("/{name}")
def iocs_delete(name: str) -> dict[str, Any]:
    path = os.path.join("ioc", f"{name}.json")
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            raise HTTPException(status_code=500, detail="Failed to delete IOC file")

    # Reload for side effects (DB mirror + in-memory list).
    load_iocs()
    return {"ok": True}

