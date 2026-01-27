from .local_storage import LocalStorage


class StorageFactory:
    """Factory for creating storage handlers"""

    _handlers = {
        'local': LocalStorage
    }

    @classmethod
    def create(cls, storage_type: str, config: dict):
        """Create appropriate storage handler based on type"""
        storage_type = storage_type.lower()

        if storage_type == 'local':
            return LocalStorage(config)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

    @classmethod
    def supported_types(cls):
        """Return list of supported storage types"""
        return ['local']
