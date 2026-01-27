import os
import subprocess
from pathlib import Path
from typing import Optional, List

from .base import DatabaseBackup, BackupFailedException, ConnectionFailedException


class PostgreSQLBackup(DatabaseBackup):
    """Performs PostgreSQL testing, backup, restoration, etc."""

    def __init__(self, config):
        super().__init__(config)
        self.port = self.port or 5432

    def test_connection(self) -> bool:
        """Test PostgreSQL connection using psql command."""
        try:
            cmd = [
                'psql',
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.username,
                '-d', 'postgres',
                '-c', 'SELECT 1'
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = str(self.password or "")

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                timeout=10,
                check=True
            )

            self.logger.info(f"Connection to PostgreSQL {self.host}:{self.port} is successful")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"PostgreSQL connection failed: {e.stderr.decode()}")
            raise ConnectionFailedException(f"Cannot connect to PostgreSQL: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            raise ConnectionFailedException("PostgreSQL connection timeout")
        except FileNotFoundError:
            raise ConnectionFailedException("psql not found. Please install PostgreSQL client tools.")

    def full_backup(self, out_path: Path, compress: bool = True) -> Path:
        """Performs full backup for the entire PostgreSQL database using pg_dump"""
        try:
            output_file = out_path / f"{self.database_name}_full_{self._timestamp()}.sql"

            cmd = [
                'pg_dump',
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.username,
                '-v',
                self.database_name
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = self.password

            with open(output_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    env=env,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    timeout=3600,
                    check=True
                )

            self.logger.info(f"Full backup created: {output_file}")
            return output_file

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Backup failed: {e.stderr.decode()}")
            raise BackupFailedException(f"PostgreSQL backup failed: {e.stderr.decode()}")
        except FileNotFoundError:
            raise BackupFailedException("pg_dump not found. Please install PostgreSQL client tools.")
        except Exception as e:
            raise BackupFailedException(f"Unexpected error: {str(e)}")

    def incremental_backup(self, out_path: Path, last_backup_path: Optional[Path] = None) -> Path:
        """Incremental backup"""
        pass

    def differential_backup(self, out_path: Path, base_backup_path: Optional[Path] = None) -> Path:
        """Differential backup"""
        pass

    def restore(self, backup_path: Path, target: Optional[str] = None) -> bool:
        """Restore PostgreSQL database from backup"""
        try:
            target = target or self.database_name

            # Create database if it doesn't exist
            create_cmd = [
                'createdb',
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.username,
                target
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = self.password

            subprocess.run(create_cmd, env=env, capture_output=True)

            restore_cmd = [
                'psql',
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.username,
                '-d', target,
                '-f', str(backup_path)
            ]

            result = subprocess.run(
                restore_cmd,
                env=env,
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
            raise BackupFailedException("psql/createdb not found. Please install PostgreSQL client tools.")

    def selective_restore(self, backup_path: Path, tables: List[str]) -> bool:
        """Restore specific tables from backup"""
        pass
