# Database Backup Utility - Complete Usage Guide

## Getting Started

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd db-backup-cli
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Install Cloud Storage Support**
   ```bash
   pip install boto3 google-cloud-storage azure-storage-blob
   ```

5. **Setup Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database passwords and API credentials
   ```

## CLI Commands

### Main Entry Point

```bash
python -m src.cli [OPTIONS] COMMAND [ARGS]

Global Options:
  -c, --config TEXT    Path to configuration file
  -v, --verbose        Enable verbose output
  --help              Show help message
```

### Available Commands

#### 1. Information Commands

**Show Version**
```bash
python -m src.cli version
```
Output: Database Backup Utility v1.0.0

**Show Info**
```bash
python -m src.cli info
```
Shows:
- Supported Databases (MySQL, PostgreSQL, MongoDB, SQLite)
- Storage Backends (Local, S3, GCS, Azure)
- Backup Types (Full, Incremental, Differential)

#### 2. Backup Commands

**Test Connection**
```bash
python -m src.cli backup test-connection \
  --db-type mysql|postgresql|mongodb|sqlite \
  --host localhost \
  [--port PORT] \
  [--username USERNAME] \
  [--password PASSWORD] \
  [--database DATABASE]
```

Examples:
```bash
# Test MySQL connection
python -m src.cli backup test-connection \
  --db-type mysql \
  --host db.example.com \
  --username backup_user

# Test PostgreSQL connection
python -m src.cli backup test-connection \
  --db-type postgresql \
  --host localhost \
  --username postgres

# Test MongoDB connection
python -m src.cli backup test-connection \
  --db-type mongodb \
  --host mongo.example.com \
  --username admin

# Test SQLite connection (no credentials needed)
python -m src.cli backup test-connection \
  --db-type sqlite \
  --database ./data/app.db
```

**Create Backup**
```bash
python -m src.cli backup create \
  --db-type mysql|postgresql|mongodb|sqlite \
  --host localhost \
  --port PORT \
  --username USERNAME \
  --password \
  --database DATABASE \
  --output ./backups \
  --compress|--no-compress \
  --backup-type full|incremental|differential \
  --storage local|s3|gcs|azure
```

Examples:
```bash
# MySQL: Full backup with compression
python -m src.cli backup create \
  --db-type mysql \
  --host localhost \
  --username backup_user \
  --password \
  --database myapp \
  --output ./backups \
  --compress \
  --backup-type full

# PostgreSQL: Full backup to local storage
python -m src.cli backup create \
  --db-type postgresql \
  --host db.example.com \
  --username postgres \
  --password \
  --database analytics \
  --output ./backups \
  --compress

# MongoDB: Full backup to S3
python -m src.cli backup create \
  --db-type mongodb \
  --host mongo.example.com \
  --username admin \
  --password \
  --database myapp \
  --storage s3 \
  --compress

# SQLite: Full backup
python -m src.cli backup create \
  --db-type sqlite \
  --database ./data/app.db \
  --output ./backups \
  --compress

# Large backup without compression (faster)
python -m src.cli backup create \
  --db-type postgresql \
  --host localhost \
  --username postgres \
  --database large_db \
  --output ./backups \
  --no-compress
```

#### 3. Restore Commands

**Restore from File**
```bash
python -m src.cli restore from-file \
  --db-type mysql|postgresql|mongodb|sqlite \
  --backup-file /path/to/backup.sql.gz \
  --host localhost \
  --port PORT \
  --username USERNAME \
  --password \
  --database TARGET_DATABASE
```

Examples:
```bash
# MySQL: Restore from compressed backup
python -m src.cli restore from-file \
  --db-type mysql \
  --backup-file ./backups/myapp_full_20241110_120000.sql.gz \
  --host localhost \
  --username root \
  --password \
  --database myapp_restored

# PostgreSQL: Restore to different host
python -m src.cli restore from-file \
  --db-type postgresql \
  --backup-file ./backups/analytics_full_20241110_120000.sql.gz \
  --host recovery-host.example.com \
  --username postgres \
  --password \
  --database analytics_recovered

# SQLite: Restore to new location
python -m src.cli restore from-file \
  --db-type sqlite \
  --backup-file ./backups/app_full_20241110_120000.db.gz \
  --database ./data/app_restored.db

# MongoDB: Restore to different cluster
python -m src.cli restore from-file \
  --db-type mongodb \
  --backup-file ./backups/myapp_full_20241110_120000.bson.gz \
  --host recovery-mongo.example.com \
  --username admin \
  --password \
  --database myapp
```

### Environment Variables (.env)

```bash
# Database Passwords
MYSQL_PASSWORD=mysql_password_here
POSTGRES_PASSWORD=postgres_password_here
MONGODB_PASSWORD=mongodb_password_here

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Google Cloud Storage
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcs-service-account.json

# Azure
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...

# Application
LOG_LEVEL=INFO
BACKUP_BASE_DIR=/var/backups
```

## Database-Specific Setup

### MySQL Setup

1. **Install MySQL Client**
   ```bash
   apt-get install mysql-client  # Linux
   brew install mysql-client     # macOS
   # Windows: Download from mysql.com
   ```

2. **Create Backup User**
   ```sql
   mysql -u root -p
   CREATE USER 'backup_user'@'localhost' IDENTIFIED BY 'password';
   GRANT SELECT, LOCK TABLES, RELOAD, REPLICATION CLIENT ON *.* TO 'backup_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Backup Commands**
   ```bash
   # Test connection
   python -m src.cli backup test-connection \
     --db-type mysql \
     --host localhost \
     --username backup_user

   # Create backup
   python -m src.cli backup create \
     --db-type mysql \
     --host localhost \
     --username backup_user \
     --database myapp

   # Restore backup
   python -m src.cli restore from-file \
     --db-type mysql \
     --backup-file ./backups/myapp_full_20241110_120000.sql.gz \
     --host localhost \
     --username root \
     --database myapp_restored
   ```

### PostgreSQL Setup

1. **Install PostgreSQL Client**
   ```bash
   apt-get install postgresql-client  # Linux
   brew install postgresql            # macOS
   ```

2. **Update Authentication**
   Edit `/etc/postgresql/*/main/pg_hba.conf`:
   ```
   local   all    all                                 md5
   host    all    all        127.0.0.1/32            md5
   host    all    all        ::1/128                 md5
   ```

3. **Create Backup User**
   ```sql
   psql -U postgres
   CREATE USER backup_user PASSWORD 'password';
   ALTER ROLE backup_user WITH NOSUPERUSER;
   GRANT CONNECT ON DATABASE myapp TO backup_user;
   ```

4. **Backup Commands**
   ```bash
   # Test connection
   python -m src.cli backup test-connection \
     --db-type postgresql \
     --host localhost \
     --username backup_user

   # Create backup
   python -m src.cli backup create \
     --db-type postgresql \
     --host localhost \
     --username backup_user \
     --database myapp

   # Restore backup
   python -m src.cli restore from-file \
     --db-type postgresql \
     --backup-file ./backups/myapp_full_20241110_120000.sql.gz \
     --host localhost \
     --username postgres \
     --database myapp_restored
   ```

### MongoDB Setup

1. **Install MongoDB Client Tools**
   ```bash
   apt-get install mongodb-database-tools  # Linux
   brew install mongodb-database-tools     # macOS
   ```

2. **Create Backup User**
   ```bash
   use admin
   db.createUser({
     user: "backup_user",
     pwd: "password",
     roles: [{role: "backup", db: "admin"}]
   })
   ```

3. **Backup Commands**
   ```bash
   # Test connection
   python -m src.cli backup test-connection \
     --db-type mongodb \
     --host localhost \
     --username admin

   # Create backup
   python -m src.cli backup create \
     --db-type mongodb \
     --host localhost \
     --username admin \
     --database myapp

   # Restore backup
   python -m src.cli restore from-file \
     --db-type mongodb \
     --backup-file ./backups/myapp_full_20241110_120000.bson.gz \
     --host localhost \
     --username admin \
     --database myapp
   ```

### SQLite Setup

1. **No Installation Required**
   Uses Python's built-in sqlite3 module

2. **Backup Commands**
   ```bash
   # Test connection
   python -m src.cli backup test-connection \
     --db-type sqlite \
     --database ./data/app.db

   # Create backup
   python -m src.cli backup create \
     --db-type sqlite \
     --database ./data/app.db \
     --output ./backups

   # Restore backup
   python -m src.cli restore from-file \
     --db-type sqlite \
     --backup-file ./backups/app_full_20241110_120000.db.gz \
     --database ./data/app_restored.db
   ```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_cli.py -v

# Run specific test
pytest tests/test_compression.py::TestGzipCompressor::test_compress_file -v

# Run tests with detailed output
pytest -vv --tb=short
```

## Troubleshooting

### Connection Issues

**MySQL: "mysqladmin: command not found"**
- Install MySQL client tools
- Verify PATH includes MySQL bin directory

**PostgreSQL: "FATAL: Ident authentication failed"**
- Check pg_hba.conf authentication method
- Set PGPASSWORD environment variable
- Ensure pg_hba.conf uses "md5" or "scram-sha-256"

**MongoDB: "mongosh not found"**
- Install MongoDB database tools
- Verify MongoDB client is in PATH

### Backup Issues

**"Connection refused"**
- Verify database is running
- Check host and port settings
- Verify firewall rules
- Ensure credentials are correct

**"Permission denied"**
- Check database user permissions
- Verify output directory is writable
- Check file system permissions

**"Out of disk space"**
- Check available disk space
- Consider compression (--compress)
- Implement backup rotation
- Move old backups to external storage

### Restore Issues

**"Database already exists"**
- Drop existing database before restore
- Or specify different database name

**"Syntax error in restore"**
- Verify backup file is not corrupted
- Ensure backup file matches database type
- Check decompress was successful

## Performance Tips

1. **Compression**
   - Default level 6 is balanced
   - Use level 1 for faster backups of large databases
   - Use level 9 for maximum compression of small databases

2. **Timing**
   - Run backups during off-peak hours
   - Monitor backup duration
   - Consider incremental backups for large databases

3. **Storage**
   - Use SSD for faster I/O
   - Consider local backups first, then upload to cloud
   - Implement backup rotation policies

4. **Network**
   - Check bandwidth for cloud uploads
   - Consider multipart uploads for large files
   - Monitor network conditions

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Command-line syntax error
- `3` - Connection failed
- `4` - Backup failed
- `5` - Restore failed
