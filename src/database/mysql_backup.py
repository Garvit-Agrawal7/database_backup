import os
import subprocess
from pathlib import Path
from typing import Optional, List

from .base import DatabaseBackup, BackupFailedException, ConnectionFailedException


class MySQLBackup(DatabaseBackup):
    """Performs MySQL testing, backup, restoration, etc."""

    def __init__(self, config):
        super().__init__(config)
        self.port = self.port or 3306

    def test_connection(self) -> bool:
        """Tests MySQL connection using mysqladmin ping."""
        try:
            cmd = [
                'mysqladmin',
                '-h', self.host,
                '-P', str(self.port),
                '-u', self.username,
                'ping'
            ]

            env = os.environ.copy()
            env['MYSQL_PWD'] = str(self.password or "")

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                timeout=10,
                check=True

            )

            self.logger.info(f"Connection to MySQL {self.host}:{self.port} successful")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"MySQL connection failed: {e.stderr.decode()}")
            raise ConnectionFailedException(f"Cannot connect to MySQL: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            raise ConnectionFailedException("MySQL connection timeout")
        except FileNotFoundError:
            raise ConnectionFailedException("mysqladmin not found. Please install MySQL client tools.")

    def full_backup(self, out_path: Path, compress: bool = True) -> Path:
        """Perform full MySQL backup using mysqldump"""
        try:
            output_file = out_path / f"{self.database_name}_full_{self._timestamp()}.sql"

            cmd = [
                'mysqldump',
                '-h', self.host,
                '-P', str(self.port),
                '-u', self.username,
                '--set-gtid-purged=OFF',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                self.database_name
            ]

            env = os.environ.copy()
            env['MYSQL_PWD'] = str(self.password or "")

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
            raise BackupFailedException(f"MySQL backup failed: {e.stderr.decode()}")
        except FileNotFoundError:
            raise BackupFailedException("mysqldump not found. Please install MySQL client tools.")
        except Exception as e:
            raise BackupFailedException(f"Unexpected error: {str(e)}")

    def incremental_backup(self, out_path: Path, last_path: Optional[Path] = None) -> Path:
        """Incremental backup"""
        pass

    def differential_backup(self, out_path: Path, base_path: Optional[Path] = None) -> Path:
        """Differential backup"""
        pass

    def restore(self, backup_path: Path, target: Optional[str] = None) -> bool:
        """Restore MySQL database from SQL dump, from backup"""
        try:
            target = target or self.database_name

            cmd = [
                'mysql',
                '-h', self.host,
                '-P', str(self.port),
                '-u', self.username,
                target
            ]

            env = os.environ.copy()
            env['MYSQL_PWD'] = self.password

            with open(backup_path, 'rb') as sql_file:
                sql_content = sql_file.read()

            # Password + SQL via stdin pipe
            stdin_data = (self.config['password'] + '\n' + sql_content.decode('utf-8', errors='replace')).encode(
                'utf-8')

            result = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=False,
                timeout=3600
            )

            self.logger.info(f"Restore completed for {target}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Restore failed: {e.stderr.decode()}")
            raise
        except FileNotFoundError:
            raise BackupFailedException("mysql client not found. Please install MySQL client tools.")

    def selective_restore(self, backup_path: Path, tables: List[str]) -> bool:
        """Restore specific tables from backup"""
        pass
