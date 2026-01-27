import pytest
from src.database.factory import DatabaseFactory

class TestDatabaseFactory:

    def test_mysql(self, mock_mysql_config):
        handler = DatabaseFactory.create('mysql', mock_mysql_config)
        assert handler is not None
        assert handler.database_name == 'test_db'

    def test_postgresql(self, mock_postgresql_config):
        handler = DatabaseFactory.create('postgresql', mock_postgresql_config)
        assert handler is not None
        assert handler.database_name == 'test_db'

    def test_sqlite(self, mock_sqlite_config):
        handler = DatabaseFactory.create('sqlite', mock_sqlite_config)
        assert handler is not None

    def test_mongodb(self, mock_mongodb_config):
        handler = DatabaseFactory.create('mongodb', mock_mongodb_config)
        assert handler is not None
        assert handler.database_name == 'test_db'

    def test_create_invalid(self, mock_mysql_config):
        with pytest.raises(ValueError):
            DatabaseFactory.create('invalid_db', mock_mysql_config)

    def test_supported_types(self):
        types = DatabaseFactory.supported_types()
        assert 'mysql' in types
        assert 'postgresql' in types
        assert 'mongodb' in types
        assert 'sqlite' in types
