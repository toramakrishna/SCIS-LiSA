# SCISLiSA Data Persistence Guide

## Overview

When you work in GitHub Codespaces, your PostgreSQL data persistence depends on the Codespace lifecycle.

## Data Persistence Timeline

| Timeline | Status | Data | Solution |
|----------|--------|------|----------|
| **0-30 days** (Paused) | ✅ Active | ✅ Persists | Auto-restored on resume |
| **30+ days** (Auto-deleted) | ❌ Deleted | ❌ Lost | Use backup script |
| **Permanent** | ♾️ Always available | ✅ Persists | Cloud PostgreSQL |

## Recommended Workflow

### 1. Local Development (Current Setup)
```bash
# On every work session end:
bash scripts/backup_database.sh

# On next Codespace startup:
bash scripts/restore_database.sh
```

### 2. Production Setup (Recommended)
Use a cloud PostgreSQL service:

**AWS RDS:**
```bash
# Update .env
DATABASE_URL=postgresql://user:password@rds-instance.amazonaws.com:5432/scislisa-service
```

**Heroku PostgreSQL:**
```bash
# Update .env
DATABASE_URL=$(heroku config:get DATABASE_URL -a your-app-name)
```

**Azure Database for PostgreSQL:**
```bash
# Update .env
DATABASE_URL=postgresql://user@servername:password@servername.postgres.database.azure.com:5432/scislisa-service
```

## Automated Backups

### Option 1: Manual Backup (Easiest)
```bash
# Before closing Codespace
bash scripts/backup_database.sh

# When reopening Codespace
bash scripts/restore_database.sh
```

### Option 2: GitHub Actions (Automated)
Create `.github/workflows/backup-database.yml`:
```yaml
name: Backup Database
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Backup PostgreSQL
        env:
          PGPASSWORD: postgres
        run: |
          pg_dump -U postgres -h localhost scislisa-service > backup.sql
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: database-backup
          path: backup.sql
```

## Importing Data

### From DBLP BibTeX Files
```bash
cd /workspaces/SCISLiSA/src/backend
python services/ingestion_service.py
```

### From SQL Backup
```bash
bash scripts/restore_database.sh
```

### From Cloud Database
Just update the `DATABASE_URL` in `.env`

## Backup File Location
```
/workspaces/SCISLiSA/database_backups/
```

**Note:** These files are `.gitignore`d to avoid large binary files in Git.

## Checking Database Status
```bash
# List all backups
ls -lh database_backups/

# View latest backup size
du -h database_backups/scislisa_backup_*.sql | sort -h | tail -1

# Check current database tables
psql -U postgres -h localhost -d scislisa-service -c "\dt"
```

## Best Practices

1. **Always backup before major changes**
   ```bash
   bash scripts/backup_database.sh
   ```

2. **Test restore on empty database**
   ```bash
   bash scripts/restore_database.sh
   ```

3. **Keep backup files in repository root** (gitignored automatically)

4. **For important data, use a cloud service:**
   - AWS RDS (managed, automated backups)
   - Heroku Postgres (simple, included in plans)
   - Azure Database (enterprise-grade)
   - Google Cloud SQL (scalable)

5. **Update production to use cloud PostgreSQL** instead of local

## Troubleshooting

### Backup fails: "Connection refused"
PostgreSQL not running. Start it:
```bash
# PostgreSQL should auto-start in Codespaces
# If not, restart the Codespace
```

### Restore fails: "Database does not exist"
Script will create it automatically. If manual:
```bash
psql -U postgres -h localhost -c "CREATE DATABASE \"scislisa-service\";"
```

### Lost data due to Codespace deletion
Use the most recent backup:
```bash
bash scripts/restore_database.sh
```

If no backup exists, data is permanently lost. This is why cloud databases are recommended.

## Summary

| Approach | Cost | Effort | Reliability |
|----------|------|--------|-------------|
| Manual backups | Free | Low | Medium |
| GitHub Actions | Free | Medium | High |
| Cloud PostgreSQL | $$/month | Low | Very High |

**Recommendation:** Use manual backups for development, cloud PostgreSQL for production.
