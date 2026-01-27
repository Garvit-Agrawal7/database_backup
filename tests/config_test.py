import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def backup_dir():
    """Create a temporary directory for backups"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_mysql_config():
    """Mock MySQL configuration"""
    return {
        'host': 'localhost',
        'port': 3306,
        'username': 'test_user',
        'password': 'test_pass',
        'database': 'test_db'
    }

@pytest.fixture
def mock_postgresql_config():
    """Mock PostgreSQL configuration"""
    return {
        'host': 'localhost',
        'port': 5432,
        'username': 'postgres',
        'password': 'test_pass',
        'database': 'test_db'
    }

@pytest.fixture
def mock_sqlite_config(backup_dir):
    """Mock SQLite configuration"""
    return {
        'database': str(backup_dir / 'test.db')
    }

@pytest.fixture
def mock_mongodb_config():
    """Mock MongoDB configuration"""
    return {
        'host': 'localhost',
        'port': 27017,
        'username': 'admin',
        'password': 'test_pass',
        'database': 'test_db'
    }
