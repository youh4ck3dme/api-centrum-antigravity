# backend/app/backups/service.py

import re
import shutil
import subprocess
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from ..config import settings

class BackupService:
    BACKUP_DIR = Path("backups")
    BACKUP_FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+\.(db|sql)$")

    @classmethod
    def ensure_backup_dir(cls) -> Path:
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        return cls.BACKUP_DIR.resolve()

    @classmethod
    def _validate_backup_filename(cls, filename: str) -> bool:
        if not filename:
            return False
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        return bool(cls.BACKUP_FILENAME_PATTERN.fullmatch(filename))

    @classmethod
    def _resolve_backup_path(cls, filename: str) -> Path | None:
        backup_dir = cls.ensure_backup_dir()
        candidate = (backup_dir / filename).resolve()
        try:
            candidate.relative_to(backup_dir)
        except ValueError:
            return None
        return candidate

    @classmethod
    def create_backup(cls):
        backup_dir = cls.ensure_backup_dir()
        db_url = settings.DATABASE_URL
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # --- PostgreSQL backup via pg_dump ---
        if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
            parsed = urlparse(db_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 5432
            user = parsed.username or "postgres"
            password = parsed.password or ""
            dbname = parsed.path.lstrip("/")

            backup_file = f"backup_{timestamp}.sql"
            backup_path = backup_dir / backup_file

            env = os.environ.copy()
            env["PGPASSWORD"] = password

            try:
                result = subprocess.run(
                    ["pg_dump", "-h", host, "-p", str(port), "-U", user, "-d", dbname, "-f", str(backup_path)],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode != 0:
                    return {"status": "error", "message": f"pg_dump failed: {result.stderr.strip()}"}

                return {
                    "status": "success",
                    "filename": backup_file,
                    "size": backup_path.stat().st_size,
                    "timestamp": timestamp,
                }
            except FileNotFoundError:
                return {"status": "error", "message": "pg_dump not found — postgresql-client not installed"}
            except subprocess.TimeoutExpired:
                return {"status": "error", "message": "pg_dump timed out after 60 seconds"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # --- SQLite backup via file copy ---
        if db_url.startswith("sqlite:///"):
            db_path = Path(db_url.replace("sqlite:///", "")).resolve()
        else:
            return {"status": "error", "message": f"Unsupported database URL scheme: {db_url}"}

        if not db_path.exists():
            return {"status": "error", "message": f"Database file not found at {db_path}"}

        backup_file = f"backup_{timestamp}.db"
        backup_path = backup_dir / backup_file

        try:
            shutil.copy2(db_path, backup_path)
            return {
                "status": "success",
                "filename": backup_file,
                "size": backup_path.stat().st_size,
                "timestamp": timestamp,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @classmethod
    def list_backups(cls):
        backup_dir = cls.ensure_backup_dir()
        backups = []
        for path in backup_dir.iterdir():
            if path.is_file() and cls._validate_backup_filename(path.name):
                backups.append({
                    "filename": path.name,
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                })
        return sorted(backups, key=lambda x: x['modified'], reverse=True)

    @classmethod
    def delete_backup(cls, filename: str):
        if not cls._validate_backup_filename(filename):
            return {
                "status": "error",
                "message": "Invalid backup filename",
                "status_code": 400,
            }

        path = cls._resolve_backup_path(filename)
        if path is None:
            return {
                "status": "error",
                "message": "Invalid backup filename",
                "status_code": 400,
            }

        if path.exists() and path.is_file():
            path.unlink()
            return {"status": "success", "message": f"Backup {filename} deleted"}
        return {"status": "error", "message": "Backup not found", "status_code": 404}

    @classmethod
    def get_backup_path(cls, filename: str) -> Path | None:
        if not cls._validate_backup_filename(filename):
            return None
        return cls._resolve_backup_path(filename)
