import logging
import sys
from datetime import datetime
from pathlib import Path
import os
import click
import yaml
from dotenv import load_dotenv

from src.database.factory import DatabaseFactory
from src.storage.factory import StorageFactory
from src.compression.compressor import GzipCompressor
from src.utils.exceptions import DatabaseBackupException
from src.utils.logger import setup_logger


load_dotenv()
setup_logger()


logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """Database Backup Utility CLI"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = {}
    ctx.obj['verbose'] = verbose

    if config:
        try:
            with open(config, 'r') as f:
                ctx.obj['config'] = yaml.safe_load(f)
            click.echo(click.style(f"✓ Loaded config from {config}", fg='green'))
        except Exception as e:
            click.echo(click.style(f"✗ Error loading config: {e}", fg='red'), err=True)
            sys.exit(1)


# ===== BACKUP COMMANDS =====
@cli.group()
def backup():
    pass


@backup.command(name='create')
@click.option('--db-type', '-t', required=True,
              type=click.Choice(['mysql', 'postgresql', 'mongodb', 'sqlite']),
              help='Database type')
@click.option('--host', '-h', help='Database host')
@click.option('--port', '-p', type=int, help='Database port')
@click.option('--username', '-u', help='Database username')
@click.option('--password', help='Database password')
@click.option('--database', '-d', required=True, help='Database name/path')
@click.option('--output', '-o', type=click.Path(), default='./backups', help='Output directory')
@click.option('--compress/--no-compress', default=True, help='Compress backup file')
@click.option('--backup-type', type=click.Choice(['full', 'incremental', 'differential']),
              default='full', help='Backup type')
@click.option('--storage', type=click.Choice(['local', 's3', 'gcs', 'azure']),
              default='local', help='Storage destination')
@click.pass_context
def backup_create(ctx, db_type, host, port, username, database, password, output, compress, backup_type, storage):

    click.echo(click.style(f"\n📦 Starting {backup_type} backup for {db_type}...", fg='cyan'))
    try:
        config = creds_manager(db_type, host, port, database, username, password)

        db_handler = DatabaseFactory.create(db_type, config)

        # Test connection
        click.echo("🔗 Testing database connection...")
        if not db_handler.test_connection():
            click.echo(click.style("✗ Connection failed!", fg='red'), err=True)
            sys.exit(1)

        click.echo(click.style("✓ Connection successful!", fg='green'))

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        click.echo(f"📝 Creating {backup_type} backup...")

        start_time = datetime.now()

        if backup_type == 'full':
            backup_file = db_handler.full_backup(output_path, compress=compress)
        elif backup_type == 'incremental':
            backup_file = db_handler.incremental_backup(output_path)
        else:
            backup_file = db_handler.differential_backup(output_path)

        if compress:
            click.echo("🗜️ Compressing backup...")
            compressor = GzipCompressor()
            backup_file = compressor.compress(backup_file)

        if storage != 'local':
            click.echo(f"☁️ Uploading to {storage}...")
            storage_handler = StorageFactory.create(storage, ctx.obj['config'])
            storage_handler.upload(backup_file)

        duration = (datetime.now() - start_time).total_seconds()
        file_size = backup_file.stat().st_size  # In Bytes

        click.echo(click.style(f"\n✓ Backup completed successfully!", fg='green'))
        click.echo(f"   📂 File: {backup_file}")
        click.echo(f"   💾 Size: {file_size/1024/1024:.3f} MB")
        click.echo(f"   ⏱️ Time: {duration:.2f} seconds")

    except DatabaseBackupException as e:
        click.echo(click.style(f"✗ Backup failed: {str(e)}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"✗ Unexpected error: {str(e)}", fg='red'), err=True)
        logger.exception("Unexpected error during backup")
        sys.exit(1)


@backup.command(name='test-connection')
@click.option('--db-type', '-t', required=True,
              type=click.Choice(['mysql', 'postgresql', 'mongodb', 'sqlite']),
              help='Database type')
@click.option('--host', '-h', default='localhost', help='Database host')
@click.option('--port', '-p', type=int, help='Database port')
@click.option('--username', '-u', help='Database username')
@click.option('--password', help='Database password')
@click.option('--database', '-d', help='Database name/path')
def backup_test_connection(db_type, host, port, username, password, database):

    click.echo(f"🔗 Testing connection to {db_type} at {host}...")

    try:
        config = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'database': database
        }

        db_handler = DatabaseFactory.create(db_type, config)

        if db_handler.test_connection():
            click.echo(click.style("✓ Connection successful!", fg='green'))
        else:
            click.echo(click.style("✗ Connection failed!", fg='red'), err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'), err=True)
        sys.exit(1)


# ===== RESTORE COMMANDS =====
@cli.group()
def restore():
    pass


@restore.command(name='from-file')
@click.option('--db-type', '-t', required=True,
              type=click.Choice(['mysql', 'postgresql', 'mongodb', 'sqlite']),
              help='Database type')
@click.option('--backup-file', '-f', required=True, type=click.Path(exists=True),
              help='Path to backup file')
@click.option('--host', '-h', help='Database host')
@click.option('--port', '-p', type=int, help='Database port')
@click.option('--username', '-u', help='Database username')
@click.option('--password', help='Database password')
@click.option('--database', '-d', help='Target database name')
@click.confirmation_option(prompt='Are you sure you want to restore? This may overwrite existing data.')
def restore_file(db_type, backup_file, host, port, username, password, database):
    """Restore database from backup file"""

    click.echo(click.style(f"\n🔄 Starting restore for {db_type}...", fg='cyan'))

    try:
        backup_path = Path(backup_file)

        if backup_path.suffix == '.gz':
            click.echo("📦 Decompressing backup...")
            compressor = GzipCompressor()
            backup_path = compressor.decompress(backup_path)

        config = creds_manager(db_type, host, port, database, username, password, backup_path)

        db_handler = DatabaseFactory.create(db_type, config)

        click.echo("📥 Restoring database...")
        start_time = datetime.now()

        db_handler.restore(backup_path, database)

        duration = (datetime.now() - start_time).total_seconds()

        click.echo(click.style(f"\n✓ Restore completed successfully!", fg='green'))
        click.echo(f"   ⏱️ Time: {duration:.2f} seconds")

    except DatabaseBackupException as e:
        click.echo(click.style(f"✗ Restore failed: {str(e)}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"✗ Unexpected error: {str(e)}", fg='red'), err=True)
        logger.exception("Unexpected error during restore")
        sys.exit(1)


# ===== INFO COMMANDS =====
@cli.command()
def version():
    """Shows version information"""
    click.echo("Database Backup Utility v1.0")
    click.echo("Python database backup and restore tool")


@cli.command()
def info():
    """Show supported databases and storage backends"""
    click.echo(click.style("\n=== Supported Databases ===", fg='cyan'))
    click.echo("  • MySQL (via mysqldump)")
    click.echo("  • PostgreSQL (via pg_dump)")
    click.echo("  • MongoDB (via mongodump)")
    click.echo("  • SQLite (via Python sqlite3)")

    click.echo(click.style("\n=== Storage Backends ===", fg='cyan'))
    click.echo("  • Local filesystem")
    click.echo("  • AWS S3 (Coming soon)")
    click.echo("  • Google Cloud Storage (Coming soon)")
    click.echo("  • Azure Blob Storage (Coming soon)")

    click.echo(click.style("\n=== Backup Types ===", fg='cyan'))
    click.echo("  • Full Backup, entire database")
    click.echo("  • Incremental Backup, changes since last backup (Coming soon)")
    click.echo("  • Differential Backup, changes since last full backup (Coming soon)")


def creds_manager(db_type: str, host: str, port: int, database:str =None, username:str = None, password:str = None, backup_path: Path = None):
    """Retrieves credentials from .env file for each type of database"""
    if db_type == 'sqlite':
        return {
            'database': database
        }
    elif db_type == 'mongodb':
        if not username:
            username = os.getenv('MONGODB_USERNAME')
        if not password:
            password = os.getenv('MONGODB_PASSWORD')
        if not host:
            host = os.getenv('MONGODB_DATABASE')

    else:
        if password is None:
            if db_type == 'postgresql':
                password = os.getenv('POSTGRES_PASSWORD') or click.prompt('Password', hide_input=True)
            elif db_type == 'mysql':
                password = os.getenv('MYSQL_PASSWORD') or click.prompt('Password', hide_input=True)

    return {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'database': database or backup_path.stem
    }


if __name__ == '__main__':
    cli()
