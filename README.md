# Database Backup Utility CLI

A comprehensive, enterprise-grade Python command-line tool for backing up and restoring databases across multiple database management systems (DBMS).

## Features

**Multi-Database Support**
- MySQL (via mysqldump)
- PostgreSQL (via pg_dump)
- MongoDB (via mongodump)
- SQLite (via Python sqlite3)

**Flexible Backup Types**
- Full backups (entire database)
- Incremental backups (changes since last backup)
- Differential backups (changes since last full backup)

**Advanced Features**
- Automatic compression with gzip
- Connection testing and validation
- Detailed logging and error reporting
- Progress indicators and user-friendly CLI
- Cross-platform compatibility (Windows, Linux, macOS)

## Installation

### Prerequisites
- Database client tools (mysqldump, pg_dump, mongodump, etc.)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/Garvit-Agrawal7/database_backup

# Install dependencies
pip install -r requirements.txt

# (Optional) Install with development tools
pip install -e ".[dev]"
```

## Quick Start

## 1. Test Database Connection
# Test MySQL connection
```bash
# Test MySQL connection
db-backup backup test-connection \
  --db-type mysql \
  --host localhost \
  --username root \
  --database mydb
```
# Test PostgreSQL connection
```bash
db-backup backup test-connection \
  --db-type postgresql \
  --host localhost \
  --username postgres \
  --database mydb
```

## 2. Create a Full Backup

# Backup MySQL database with compression
```bash
db-backup backup create \
  --db-type mysql \
  --host localhost \
  --username backup_user \
  --database production_db \
  --output ./backups \
  --compress \
  --backup-type full
```

# Backup to PostgreSQL
```bash
db-backup backup create \
  --db-type postgresql \
  --host localhost \
  --username postgres \
  --database production_db \
  --output ./backups \
  --compress \
  --backup-type full
```
Create the database 'production_db'. (You have to manually do it in PostgreSQL) <br>
Use and enter your password;
```bash
psql -h localhost -p 5432 -U postgres
```
```
CREATE DATABASE production_db;
```
<br><br>

## 3. Restore from Backup
# Restore MySQL database from compressed backup
```bash
db-backup restore from-file \
  --db-type mysql \
  --backup-file ./backups/production_db_full_20260117_164545.sql.gz \
  --host localhost \
  --username root \
  --database production_db
```

# Restore PostgreSQL database
```bash
db-backup restore from-file \
  --db-type postgresql \
  --backup-file ./backups/production_db_full_20260115_195507.sql.gz \
  --host localhost \
  --username postgres \
  --database production_restored
```

## Configuration

### Using Configuration Files

Create a YAML configuration file:

```yaml
# config/production.yaml
databases:
  - name: production_mysql
    type: mysql
    connection:
      host: localhost
      port: 3306
      username: backup_user
      password: \${MYSQL_PASSWORD}
      database: myapp_production

    backup:
      type: full
      compress: true
      output_dir: /backups/mysql

  - name: analytics_postgres
    type: postgresql
    connection:
      host: analytics.example.com
      port: 5432
      username: postgres
      password: \${POSTGRES_PASSWORD}
      database: analytics

    backup:
      type: full
      compress: true
      output_dir: /backups/postgresql
      
# Logging Configuration
logging:
  level: INFO
  directory: logs
```

### Environment Variables
Create a `.env` file in the project root:

```bash
# Database Passwords
MYSQL_PASSWORD=your_mysql_password
POSTGRES_PASSWORD=your_postgres_password
MONGODB_DATABASE=database_name
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_monogdb_password

# Application
LOG_LEVEL=INFO
BACKUP_BASE_DIR=/var/backups
```

## Usage Examples

### MySQL Backups

```bash
# Test connection
db-backup backup test-connection \
  --db-type mysql \
  --host localhost \
  --username root

# Full backup
db-backup backup create \
  --db-type mysql \
  --host localhost \
  --username root \
  --database myapp \
  --output ./backups \
  --compress

# Restore backup
db-backup restore from-file \
  --db-type mysql \
  --backup-file ./backups/production_db_full_20260115_200917.sql.gz \
  --host localhost \
  --username root \
  --database myapp_restored
```

### PostgreSQL Backups

```bash
# Full backup
db-backup backup create \
  --db-type postgresql \
  --host localhost \
  --username postgres \
  --database myapp \
  --output ./backups \
  --compress

# Restore backup
db-backup restore from-file \
  --db-type postgresql \
  --backup-file ./backups/production_db_full_20260115_195507.sql.gz \
  --host localhost \
  --username postgres \
  --database myapp_restored
```

### SQLite Backups

```bash
# Backup SQLite database
db-backup backup create \
  --db-type sqlite \
  --database ./data/app.db \
  --output ./backups \
  --compress \
  --backup-type full

# Restore SQLite database
db-backup restore from-file \
  --db-type sqlite \
  --backup-file ./backups/app_full_20260118_174105.db.gz \
  --database ./data/app_restored.db
```

### MongoDB Backups

```bash
# Full backup
db-backup backup create \
  --db-type mongodb \
  --database myapp \
  --output ./backups \
  --compress

# Restore backup
db-backup restore from-file \
  --db-type mongodb \
  --backup-file ./backups/cluster0.ihf2qmn.mongodb.net/_full_20260119_091132 \
  --database myapp_restored
```


## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/config_test.py -v
```

## Security Best Practices

1. **Never commit sensitive data**: Use `.env` files for credentials (excluded from git)
2. **Use environment variables**: Passwords are passed via environment, not command-line
3. **Prevent command injection**: All database commands use argument lists, not shell=True
4. **Secure credential handling**: Passwords are passed via environment variables (MYSQL_PWD, PGPASSWORD)
5. **Input validation**: All user inputs are sanitized
6. **Least privilege**: Use dedicated backup users with minimal necessary permissions

## Troubleshooting

### MySQL Issues

**Error: mysqldump: command not found**
- Install MySQL client: `apt-get install mysql-client` (Linux) or download from mysql.com

**Error: Access denied for user**
- Verify username and password
- Check MySQL user permissions: `GRANT SELECT, LOCK TABLES, RELOAD, REPLICATION CLIENT ON *.* TO 'backup_user'@'localhost';`

### PostgreSQL Issues

**Error: psql: command not found**
- Install PostgreSQL client: `apt-get install postgresql-client` (Linux)

**Error: FATAL: Ident authentication failed**
- Update PostgreSQL `pg_hba.conf` to allow password authentication
- Ensure PGPASSWORD environment variable is set

### MongoDB Issues

**Error: mongodump: command not found**
- Install MongoDB tools: `apt-get install mongodb-database-tools` (Linux)

**Error: authentication failed**
- Verify MongoDB credentials and authentication database
- Check user permissions in MongoDB

## Performance Optimization Tips

1. **Use fast storage**: Place backups on SSD for faster I/O
2. **Compression level**: Use level 6 (default) for balanced speed/size
3. **Large databases**: Use --no-compress for very large files to save CPU
4. **Scheduling**: Run backups during off-peak hours
5. **Connection pooling**: Implement for multiple concurrent backups (future enhancement)

## Contributing

Contributions are welcome!
