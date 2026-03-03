# backend/app/backups/service.py

import shutil
import os
from datetime import datetime
from ..config import settings

class BackupService:
    BACKUP_DIR = "backups"
    
    @classmethod
    def ensure_backup_dir(cls):
        if not os.path.exists(cls.BACKUP_DIR):
            os.makedirs(cls.BACKUP_DIR)
            
    @classmethod
    def create_backup(cls):
        cls.ensure_backup_dir()
        db_path = "test.db" # V reálnej aplikácii z settings.DATABASE_URL
        if not os.path.exists(db_path):
            return {"status": "error", "message": "Database file not found"}
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.db"
        backup_path = os.path.join(cls.BACKUP_DIR, backup_file)
        
        try:
            shutil.copy2(db_path, backup_path)
            return {
                "status": "success", 
                "filename": backup_file, 
                "size": os.path.getsize(backup_path),
                "timestamp": timestamp
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    @classmethod
    def list_backups(cls):
        cls.ensure_backup_dir()
        backups = []
        for f in os.listdir(cls.BACKUP_DIR):
            if f.endswith(".db"):
                path = os.path.join(cls.BACKUP_DIR, f)
                backups.append({
                    "filename": f,
                    "size": os.path.getsize(path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
                })
        return sorted(backups, key=lambda x: x['modified'], reverse=True)

    @classmethod
    def delete_backup(cls, filename: str):
        path = os.path.join(cls.BACKUP_DIR, filename)
        if os.path.exists(path) and filename.endswith(".db"):
            os.remove(path)
            return {"status": "success", "message": f"Backup {filename} deleted"}
        return {"status": "error", "message": "Backup not found"}
