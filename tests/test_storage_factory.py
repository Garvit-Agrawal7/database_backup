import pytest
from src.storage.factory import StorageFactory

class TestStorageFactory:

    def test_create_local_storage(self):
        storage = StorageFactory.create('local', {})
        assert storage is not None

    def test_supported_types(self):
        types = StorageFactory.supported_types()
        assert 'local' in types


    def test_create_invalid_storage(self):
        """Test creating handler with invalid storage type"""
        with pytest.raises(ValueError):
            StorageFactory.create('invalid_storage', {})
