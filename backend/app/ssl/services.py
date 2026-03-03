# backend/app/ssl/services.py

import subprocess
from pathlib import Path
from ..config import settings


class SSLService:
    @staticmethod
    def generate_ssl_certificate(domain: str, email: str):
        certbot_cmd = [
            "certbot", "certonly", "--standalone",
            "--non-interactive", "--agree-tos",
            "--email", email,
            "--domains", domain
        ]
        try:
            subprocess.run(certbot_cmd, check=True)
            return {"status": "success", "domain": domain}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": str(e)}

