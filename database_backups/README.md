# Database Backups

This directory contains PostgreSQL database backups for the SCISLiSA project.

## Automatic Backups

Backups are created using `scripts/backup_database.sh` and can be restored with `scripts/restore_database.sh`.

### Manual Backup
```bash
bash scripts/backup_database.sh
```

### Manual Restore
```bash
bash scripts/restore_database.sh
```

### Restore to Specific Backup
```bash
psql -U postgres -h localhost scislisa-service < database_backups/scislisa_backup_20260202_120000.sql
```

## Storage Notes

- Only the 5 most recent backups are kept
- Backups are NOT committed to Git (.gitignore)
- For production, use a managed database service (AWS RDS, Heroku, etc.)

## Codespace Persistence

When you reopen a Codespace:

1. **If paused (< 30 days)**: Database data persists automatically
2. **If deleted (> 30 days)**: Use `scripts/restore_database.sh` to restore from latest backup
3. **For permanent storage**: Export backups or use a cloud database

## GitHub Actions Integration

You can automate backups by adding to GitHub Actions (see `.github/workflows/backup-database.yml`).
