from .base import DatabaseBackup
from .mongodb_backup import MongoDBBackup
from .mysql_backup import MySQLBackup
from .postgresql_backup import PostgreSQLBackup
from .sqlite_backup import SQLiteBackup


class DatabaseFactory:
    """Factory for creating database backup handlers"""

    _handlers = {
        'mysql': MySQLBackup,
        'postgresql': PostgreSQLBackup,
        'mongodb': MongoDBBackup,
        'sqlite': SQLiteBackup
    }

    @classmethod
    def create(cls, db_type: str, config: dict) -> DatabaseBackup:
        """Create appropriate database handler based on type"""
        db_type = db_type.lower()

        if db_type not in cls._handlers:
            raise ValueError(f"Unsupported database type: {db_type}")

        return cls._handlers[db_type](config)

    @classmethod
    def supported_types(cls):
        """Return list of supported database types"""
        return list(cls._handlers.keys())
