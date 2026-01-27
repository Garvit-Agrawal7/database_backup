import subprocess
from pathlib import Path
from typing import Optional, List

from .base import DatabaseBackup, BackupFailedException, ConnectionFailedException


class MongoDBBackup(DatabaseBackup):
    """Performs MongoDB testing, backup, restoration, etc."""

    def __init__(self, config):
        super().__init__(config)
        self.port = f':{self.port}' if self.port else ''

    def test_connection(self) -> bool:
        """Tests MongoDB connection to the server (Uses mongosh)."""
        try:
            cmd = [
                'mongosh',
                f'mongodb+srv://{self.username}:{self.password}@{self.host}{self.port}',
                '--eval', 'db.adminCommand("ping")'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=10,
                check=True
            )

            self.logger.info(f"Connection to MongoDB {self.database_name} successful")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"MongoDB connection failed: {e.stderr.decode()}")
            raise ConnectionFailedException(f"Cannot connect to MongoDB: {e.stderr.decode()}")

        except subprocess.TimeoutExpired:
            raise ConnectionFailedException("MongoDB connection timeout")

        except FileNotFoundError:
            raise ConnectionFailedException("mongosh not found. Please install MongoDB client tools.")

    def full_backup(self, out_path: Path, compress: bool = True) -> Path:
        """Full MongoDB backup using mongodump (Works for both local and online MongoDB (Atlas))."""
        try:
            out_file = out_path / f"{self.host}_full_{self._timestamp()}"
            out_file.mkdir(parents=True, exist_ok=True)

            cmd = [
                'mongodump',
                f'--uri=mongodb+srv://{self.username}:{self.password}@{self.host}{self.port}',
                f'--out={out_file}',
                '--gzip' if compress else '',
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=3600,
                check=True
            )

            self.logger.info(f"Full backup created: {out_file}")
            return out_file

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Backup failed: {e.stderr.decode()}")
            raise BackupFailedException(f"MongoDB backup failed: {e.stderr.decode()}")

        except FileNotFoundError:
            raise BackupFailedException("mongodump not found. Please install MongoDB client tools.")

        except Exception as e:
            raise BackupFailedException(f"Unexpected error: {str(e)}")

    def incremental_backup(self, out_path: Path, last_backup: Optional[Path] = None) -> Path:
        """Incremental backup"""
        pass

    def differential_backup(self, out_path: Path, base_backup: Optional[Path] = None) -> Path:
        """Differential backup"""
        pass

    def restore(self, backup_path: Path, target: Optional[str] = None) -> bool:
        """Restore MongoDB database from backup (Can restore from both local and online Database)."""
        try:
            target = target or self.host

            cmd = [
                'mongorestore',
                f'--uri=mongodb+srv://{self.username}:{self.password}@{self.host}{self.port}',
                f'--db={target}',
                str(backup_path),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=3600,
                check=True
            )

            self.logger.info(f"Restore completed for {target}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Restore failed: {e.stderr.decode()}")
            raise
        except FileNotFoundError:
            raise BackupFailedException("mongorestore not found. Please install MongoDB client tools.")

    def selective_restore(self, backup_path: Path, collections: List[str]) -> bool:
        """Restore specific collections from backup"""
        pass
