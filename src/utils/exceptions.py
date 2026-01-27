class DatabaseBackupException(Exception):
    """Base exception for database backup operations"""
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

class CompressionFailedException(DatabaseBackupException):
    """Raised when compression/decompression fails"""
    pass

class StorageException(DatabaseBackupException):
    """Raised when storage operation fails"""
    pass

class ConfigurationException(DatabaseBackupException):
    """Raised when configuration is invalid"""
    pass
