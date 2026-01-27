DEFAULT_BACKUP_DIR = './backups'
DEFAULT_LOG_DIR = './logs'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_COMPRESSION_LEVEL = 6  # 1-9, 6 is balanced
DEFAULT_CONNECTION_TIMEOUT = 30
DEFAULT_BACKUP_TIMEOUT = 3600
MAX_PARALLEL_BACKUPS = 3

# Database specific defaults
DATABASE_DEFAULTS = {
    'mysql': {
        'port': 3306,
        'driver': 'mysql+pymysql'
    },
    'postgresql': {
        'port': 5432,
        'driver': 'postgresql+psycopg2'
    },
    'mongodb': {
        'port': 27017,
    },
    'sqlite': {
        'port': None,  # SQLite doesn't use ports
    }
}

# Storage defaults
STORAGE_DEFAULTS = {
    's3': {
        'region': 'us-east-1',
        'prefix': 'backups/'
    },
    'gcs': {
        'prefix': 'backups/'
    },
    'azure': {
        'prefix': 'backups/'
    }
}
