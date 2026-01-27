import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List


class DatabaseBackupException(Exception):
    """Custom exception for database backup operations"""
    pass


class ConnectionFailedException(DatabaseBackupException):
    """Raised when database connection fails"""
    pass


class BackupFailedException(DatabaseBackupException):
    """Raised when backup operation fails"""
    pass


class RestoreFailedException(DatabaseBackupException):
    """Raised when restore operation fails"""
    pass


class DatabaseBackup(ABC):
    """Abstract base class for database backup operations"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port')
        self.username = config.get('username')
        self.password = config.get('password')
        self.database_name = config.get('database')

    @abstractmethod
    def test_connection(self) -> bool:
        """Test database connectivity"""
        pass

    @abstractmethod
    def full_backup(self, out_path: Path, compress: bool = True) -> Path:
        """Perform full database backup"""
        pass

    @abstractmethod
    def incremental_backup(self, out_path: Path,
                           last_backup_path: Optional[Path] = None) -> Path:
        """Perform incremental backup"""
        pass

    @abstractmethod
    def differential_backup(self, out_path: Path,
                            base_backup_path: Optional[Path] = None) -> Path:
        """Perform differential backup"""
        pass

    @abstractmethod
    def restore(self, backup_path: Path, target: Optional[str] = None) -> bool:
        """Restore database from backup"""
        pass

    @abstractmethod
    def selective_restore(self, backup_path: Path,
                          objects: List[str]) -> bool:
        """Restore specific tables/collections"""
        pass

    @staticmethod
    def _timestamp() -> str:
        """Generate timestamp for backup filename"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
