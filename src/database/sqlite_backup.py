import shutil
import sqlite3
from pathlib import Path
from typing import Optional, List

from .base import DatabaseBackup, BackupFailedException, ConnectionFailedException


class SQLiteBackup(DatabaseBackup):
    """SQLite testing, backup, restoration handler (no auth for sqlite)"""

    def __init__(self, config):
        super().__init__(config)
        self.db_path = Path(config.get('database', 'database.db'))

    def test_connection(self) -> bool:
        """Test if SQLite file exists"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()

            self.logger.info(f"Connection to SQLite {self.db_path} successful")
            return True

        except sqlite3.Error as e:
            self.logger.error(f"SQLite connection failed: {e}")
            raise ConnectionFailedException(f"Cannot connect to SQLite: {e}")
        except FileNotFoundError:
            raise ConnectionFailedException(f"SQLite database file not found: {self.db_path}")

    def full_backup(self, out_path: Path, compress: bool = True) -> Path:
        """Creates full SQLite backup by copying database file"""
        try:
            output_file = out_path / f"{self.db_path.stem}_full_{self._timestamp()}.db"

            # Using SQLite backup API for consistency
            source = sqlite3.connect(str(self.db_path))
            dest = sqlite3.connect(str(output_file))

            with dest:
                source.backup(dest)

            source.close()
            dest.close()

            self.logger.info(f"Full backup created: {output_file}")
            return output_file

        except sqlite3.Error as e:
            self.logger.error(f"Backup failed: {e}")
            raise BackupFailedException(f"SQLite backup failed: {e}")
        except Exception as e:
            raise BackupFailedException(f"Unexpected error: {str(e)}")

    def incremental_backup(self, out_path: Path, last_backup: Optional[Path] = None) -> Path:
        """SQLite incremental backup"""
        pass

    def differential_backup(self, out_path: Path, base_backup: Optional[Path] = None) -> Path:
        """SQLite differential backup"""
        pass

    def restore(self, backup_path: Path, target: Optional[str] = None) -> bool:
        """Restore SQLite database from backup"""
        try:
            target = target or self.db_path
            shutil.copy(backup_path, target)

            self.logger.info(f"Restore completed for {target}")
            return True

        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            raise

    def selective_restore(self, backup_path: Path, tables: List[str]) -> bool:
        """Restore specific tables from SQLite backup"""
        pass
