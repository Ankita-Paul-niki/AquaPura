"""
History router — GET /api/history, DELETE /api/history/{id}

Stub implementation. Will be completed in Phase 4 (database integration).
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/history")
def get_history():
    """Return paginated assessment history. (Stub — Phase 4)"""
    # TODO (Phase 4): query SQLite via SQLAlchemy and return records
    return {"items": [], "total": 0}


@router.delete("/history/{record_id}")
def delete_history(record_id: int):
    """Delete a single assessment record. (Stub — Phase 4)"""
    # TODO (Phase 4): find record and delete; raise 404 if not found
    raise HTTPException(status_code=501, detail="Not yet implemented.")
