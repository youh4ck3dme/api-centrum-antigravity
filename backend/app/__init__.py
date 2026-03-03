"""
API Centrum Backend Package
Domain & SSL Management System with Neon Auth Integration
"""

# Version information
__version__ = "1.0.0"
__author__ = "API Centrum Team"

# Ponecháme len základné informácie. Ťažké importy (.main, .db.engine) 
# spôsobujú problémy pri migráciách a cirkulárne závislosti.

# Initialize database
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

# Health check
def health_check():
    """Basic health check"""
    return {
        "status": "ok",
        "version": __version__,
        "database": "connected" if engine else "disconnected"
    }

__all__ = [
    "app",
    "settings", 
    "engine",
    "Base",
    "get_db",
    "User",
    "Role", 
    "AuditLog",
    "CRUDUser",
    "CRUDRole",
    "LocalAuthService",
    "CompositeAuthService",
    "AuthMigrationService",
    "NeonAuthService",
    "WebsupportService",
    "DashboardStats",
    "init_db",
    "health_check"
]