import logging
from pathlib import Path


class LocalStorage:
    """Local filesystem storage handler"""

    def __init__(self, config: dict = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

    def upload(self, file_path: Path) -> str:
        """Backup file is already local, just return path"""
        self.logger.info(f"Backup file already at: {file_path}")
        return str(file_path)

    def download(self, file_path: Path, destination: Path) -> Path:
        """Local storage doesn't require download"""
        return file_path

    def list_backups(self, directory: Path) -> list:
        """List all backup files in directory"""
        backups = []
        for file in directory.glob('*'):
            if file.is_file():
                backups.append({
                    'name': file.name,
                    'size': file.stat().st_size,
                    'modified': file.stat().st_mtime,
                    'path': str(file)
                })
        return sorted(backups, key=lambda x: x['modified'], reverse=True)
