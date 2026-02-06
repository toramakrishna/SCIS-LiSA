#!/bin/bash

# Restore PostgreSQL database from backup
# Restores the most recent database backup

set -e

BACKUP_DIR="/workspaces/SCISLiSA/database_backups"

# Find the most recent backup
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.sql 2>/dev/null | head -n1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "⚠️  No database backup found in $BACKUP_DIR"
    echo "Starting with empty database..."
    exit 0
fi

echo "🔄 Restoring database from: $LATEST_BACKUP"

# Drop existing data if any
psql -U postgres -h localhost -c "DROP DATABASE IF EXISTS \"scislisa-service\";" 2>/dev/null || true
psql -U postgres -h localhost -c "CREATE DATABASE \"scislisa-service\";" || true

# Restore from backup
psql -U postgres -h localhost scislisa-service < "$LATEST_BACKUP"

echo "✅ Database restored successfully!"
