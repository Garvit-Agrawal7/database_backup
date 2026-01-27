import sqlite3
from pathlib import Path

import pytest

from src.database.base import ConnectionFailedException
from src.database.sqlite_backup import SQLiteBackup


class TestSQLiteBackup:

    def setup_method(self):
        """Setup test database"""
        self.db_file = Path('test_sqlite.db')
        if self.db_file.exists():
            self.db_file.unlink()

        # Create sample data
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')
        cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', 
                      ('John Doe', 'john@example.com'))
        cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)',
                      ('Jane Doe', 'jane@example.com'))
        conn.commit()
        conn.close()

    def teardown_method(self):
        """Cleanup test database"""
        if self.db_file.exists():
            self.db_file.unlink()

    def test_connection(self):
        config = {'database': str(self.db_file)}
        backup = SQLiteBackup(config)

        assert backup.test_connection() is True

    def test_connection_invalid_file(self):
        config = {'database': '/nonexistent/path/test.db'}
        backup = SQLiteBackup(config)

        with pytest.raises(ConnectionFailedException):
            backup.test_connection()

    def test_full_backup(self, tmp_path):
        config = {'database': str(self.db_file)}
        backup = SQLiteBackup(config)

        backup_file = backup.full_backup(tmp_path)

        assert backup_file.exists()
        assert backup_file.suffix == '.db'

        # Verify backup contains data
        backup_conn = sqlite3.connect(str(backup_file))
        backup_cursor = backup_conn.cursor()
        backup_cursor.execute('SELECT COUNT(*) FROM users')
        count = backup_cursor.fetchone()[0]
        backup_conn.close()

        assert count == 2

    def test_restore(self, tmp_path):
        config = {'database': str(self.db_file)}
        backup = SQLiteBackup(config)

        # Create backup
        backup_file = backup.full_backup(tmp_path)

        # Delete original and verify
        self.db_file.unlink()
        assert not self.db_file.exists()

        # Restore
        restore_config = {'database': str(self.db_file)}
        restore_backup = SQLiteBackup(restore_config)
        restore_backup.restore(backup_file)

        assert self.db_file.exists()

        # Verify restored data
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 2
