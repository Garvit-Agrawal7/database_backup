from pathlib import Path
import re

def validate_connection_config(config: dict, db_type: str) -> bool:
    """Validate database connection configuration"""
    required_fields = ['username', 'database']

    if db_type == 'sqlite':
        required_fields = ['database']

    for field in required_fields:
        if field not in config or not config[field]:
            raise ValueError(f"Missing required field: {field}")

    return True

def validate_file_path(path: str) -> Path:
    """Validate and convert file path"""
    try:
        p = Path(path)
        if not p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
        return p
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")

def validate_backup_type(backup_type: str) -> bool:
    """Validate backup type"""
    valid_types = ['full', 'incremental', 'differential']
    if backup_type not in valid_types:
        raise ValueError(f"Invalid backup type. Must be one of: {', '.join(valid_types)}")
    return True

def validate_database_type(db_type: str) -> bool:
    """Validate database type"""
    valid_types = ['mysql', 'postgresql', 'mongodb', 'sqlite']
    if db_type.lower() not in valid_types:
        raise ValueError(f"Invalid database type. Must be one of: {', '.join(valid_types)}")
    return True

def sanitize_command_input(input_str: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    invalid_char = [';', '|', '&', '$', '`', '(', ')', '<', '>', '\n', '\r']
    for char in invalid_char:
        input_str = input_str.replace(char, '')
    return input_str
