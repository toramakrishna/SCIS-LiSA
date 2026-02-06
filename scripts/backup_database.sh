#!/bin/bash

# Backup PostgreSQL database to SQL file
# This script exports the scislisa-service database for version control

set -e

BACKUP_DIR="/workspaces/SCISLiSA/database_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/scislisa_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "🔄 Backing up PostgreSQL database..."
pg_dump -U postgres -h localhost scislisa-service > "$BACKUP_FILE"

echo "✅ Database backed up to: $BACKUP_FILE"
echo "📦 File size: $(du -h "$BACKUP_FILE" | cut -f1)"

# Keep only the last 5 backups
echo "🧹 Cleaning up old backups..."
ls -t "$BACKUP_DIR"/*.sql 2>/dev/null | tail -n +6 | xargs -r rm

echo "✅ Backup complete!"
