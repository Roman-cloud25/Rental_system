#!/bin/bash

BACKUP_DIR="/backups"

DB_NAME="${DB_NAME:-rental_db}"
DB_USER="${DB_USER:-rental_user}"
DB_PASSWORD="${DB_PASSWORD:-rental_password}"
DB_HOST="${DB_HOST:-db}"

mkdir -p $BACKUP_DIR

DATE=$(date +\%Y\%m\%d_\%H\%M\%S)

echo "Creating backup at $DATE..."
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Check if the backup was created successfully
if [ -f "$BACKUP_DIR/backup_$DATE.sql" ]; then
    echo "Backup created: $BACKUP_DIR/backup_$DATE.sql"
    find $BACKUP_DIR -type f -name "*.sql" -mtime +30 -delete
    echo "Old backups (over 30 days) removed"
else
    echo "Backup failed!"
fi