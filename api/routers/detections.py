from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from detections import (
    add_detection_manual,
    get_detection,
    list_detections,
    remove_detection,
    restore_detection,
    load_detections,
)

router = APIRouter()


@router.get("/")
def detections_list() -> list[dict[str, Any]]:
    # Ensure DB is initialized and cache is built.
    load_detections()
    return list_detections()


@router.get("/{file_hash}")
def detections_get(file_hash: str) -> dict[str, Any]:
    load_detections()
    det = get_detection(file_hash, include_deleted=True)
    if not det:
        raise HTTPException(status_code=404, detail="Detection not found")
    return det


@router.post("/")
def detections_create(payload: dict[str, Any]) -> dict[str, Any]:
    name = payload.get("name")
    file_hash = payload.get("file_hash")
    collector = payload.get("collector_name") or "manual"
    extra_info = payload.get("extra_info") or []

    if not name or not file_hash:
        raise HTTPException(status_code=400, detail="name and file_hash are required")

    if extra_info is not None and not isinstance(extra_info, list):
        raise HTTPException(status_code=400, detail="extra_info must be a list of strings")

    add_detection_manual(name, file_hash, collector_name=collector, extra_info=extra_info)
    load_detections()
    return get_detection(file_hash, include_deleted=True) or payload


@router.put("/{file_hash}")
def detections_update(file_hash: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Minimal update behavior: soft-delete + re-add as manual with the new name.
    (Keeps schema stable without inventing partial-update logic.)
    """
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    remove_detection(file_hash, soft=True)
    add_detection_manual(name, file_hash, collector_name="manual", extra_info=payload.get("extra_info") or [])
    load_detections()
    det = get_detection(file_hash, include_deleted=True)
    if not det:
        raise HTTPException(status_code=404, detail="Detection not found after update")
    return det


@router.delete("/{file_hash}")
def detections_delete(file_hash: str) -> dict[str, Any]:
    # Soft-delete to match CLI behavior.
    remove_detection(file_hash, soft=True)
    load_detections()
    return {"ok": True}


@router.post("/{file_hash}/restore")
def detections_restore(file_hash: str) -> dict[str, Any]:
    restore_detection(file_hash)
    load_detections()
    det = get_detection(file_hash, include_deleted=True)
    if not det:
        raise HTTPException(status_code=404, detail="Detection not found")
    return det

