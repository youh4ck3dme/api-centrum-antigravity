# backend/app/backups/routes.py

from fastapi import APIRouter, HTTPException
from .service import BackupService

router = APIRouter(tags=["Backups"])

@router.post("/backups/create")
async def create_backup():
    result = BackupService.create_backup()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/backups")
async def list_backups():
    return BackupService.list_backups()

@router.delete("/backups/{filename}")
async def delete_backup(filename: str):
    result = BackupService.delete_backup(filename)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result
