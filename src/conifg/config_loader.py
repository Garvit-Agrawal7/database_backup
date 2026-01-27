import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class ConfigLoader:
    """Load configuration from YAML files with environment variable substitution"""

    @staticmethod
    def load(config_path):
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Substitute environment variables
        return ConfigLoader._substitute_env_vars(config)

    @staticmethod
    def _substitute_env_vars(obj):
        """Recursively substitute ${VAR} with environment variables"""
        if isinstance(obj, dict):
            return {k: ConfigLoader._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ConfigLoader._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            var_name = obj[2:-1]
            return os.getenv(var_name, obj)
        return obj
