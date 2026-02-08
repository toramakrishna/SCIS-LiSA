# SCISLiSA Backend - Production Pipeline

## Overview
This is the data ingestion and processing pipeline for the SCIS Literature and Scholarship Analytics (SCISLiSA) system.

## Structure

```
src/backend/
├── config/          # Database configuration
├── models/          # SQLAlchemy ORM models
├── parsers/         # BibTeX parsing logic
├── services/        # Core ingestion service
├── sources/         # Data source adapters (DBLP)
├── utils/           # Utility scripts for verification and reporting
├── references/      # Faculty data and DBLP matching
└── main.py          # Main entry point
```

## Core Components

### 1. Data Ingestion Pipeline (`services/ingestion_service.py`)
- Parses BibTeX files from DBLP
- Matches faculty members by name
- Prevents duplicate publications
- Creates author and collaboration records
- Updates publication statistics

### 2. Database Models (`models/db_models.py`)
- **Author**: Faculty members and co-authors
- **Publication**: Research papers with metadata
- **Collaboration**: Co-authorship relationships
- **Venue**: Journals and conferences
- **DataSource**: Source tracking

### 3. BibTeX Parser (`parsers/bibtex_parser.py`)
- Extracts publication data from .bib files
- Handles duplicate detection within files
- Tracks source PIDs for faculty attribution

## Usage

### Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure PostgreSQL is running (via Docker)
docker ps | grep postgres

# Ensure database exists
docker exec postgres psql -U postgres -c "CREATE DATABASE \"scislisa-service\";"
```

### Run Full Ingestion
```bash
python3 services/ingestion_service.py
```

This will:
1. Initialize database schema
2. Parse all BibTeX files from `../dataset/dblp/`
3. Load faculty mapping from `references/dblp/faculty_dblp_matched.json`
4. Ingest publications with proper author attribution
5. Create collaboration records
6. Update statistics

### Verification Scripts

After ingestion, verify data integrity:

```bash
# Verify publication counts against DBLP
python3 utils/verify_dblp_counts.py

# Check faculty data mapping
python3 utils/verify_faculty_data.py

# Comprehensive verification
python3 utils/comprehensive_verification.py

# Database statistics
python3 utils/show_db_stats.py

# Faculty publication report
python3 utils/faculty_report.py
```

### Merge Duplicate Authors
If name variations create duplicate author records:

```bash
python3 utils/merge_faculty_duplicates.py
```

## Data Flow

1. **BibTeX Files** (`../dataset/dblp/*.bib`)
   - Downloaded from DBLP for each faculty member
   - Named with DBLP PID (e.g., `01_1744-1.bib` for PID `01/1744-1`)

2. **Faculty Mapping** (`references/dblp/faculty_dblp_matched.json`)
   - Maps faculty names to DBLP PIDs
   - Contains email, designation, department

3. **Parsing**
   - Extracts publications from BibTeX
   - Tracks source PID from filename
   - Deduplicates within files

4. **Ingestion**
   - Matches faculty by comparing author names with faculty mapping
   - Creates/updates author records
   - Links publications to authors
   - Generates collaboration records

5. **Verification**
   - Compares counts with live DBLP data
   - Validates author data integrity
   - Checks for duplicate records

## Key Features

### Name Matching Logic
- Normalizes names (lowercase, no dots/commas)
- Only assigns faculty data when author name matches faculty name
- Prevents co-authors from getting faculty emails/PIDs

### Duplicate Prevention
- Uses `dblp_key` as primary identifier
- Tracks publications across multiple faculty files via `source_pids`
- Handles co-authored papers between faculty

### Statistics Tracking
- `total_publications`: Count per author
- `total_collaborations`: Unique co-author relationships
- Venue statistics (total/faculty publications)

## Database Configuration

PostgreSQL connection settings in `config/db_config.py`:
- **Database**: `scislisa-service`
- **User**: `postgres`
- **Password**: `postgres`
- **Host**: `localhost`
- **Port**: `5432`

## Known Limitations

### Name Variations (17/35 faculty affected)
Some faculty members appear as co-authors due to name format differences between our records and DBLP:

**Examples:**
- Our record: "Satish Srirama" → DBLP: "Satish Narayana Srirama"
- Our record: "Bapi Raju S." → DBLP: "Raju S. Bapi"

**Solution**: Use `merge_faculty_duplicates.py` to consolidate records after ingestion.

### Publication Count Verification
The `verify_dblp_counts.py` script queries by `source_pids`, so it correctly shows all 34 faculty members even if only 18 are marked as `is_faculty=true` in the authors table.

## Verification Results

✅ **34/34 faculty** - 100% publication count accuracy  
✅ **18/18 matched faculty** - 100% data integrity (name, email, designation, PID)  
✅ **1,110 co-authors** - Correctly marked, no faculty data contamination  
✅ **1,321 publications** - All unique, properly deduplicated  
✅ **3,019 collaborations** - Co-authorship relationships tracked  

## Maintenance

### Re-running Ingestion
To re-ingest data:

```bash
# Drop and recreate database
docker exec postgres psql -U postgres -c "DROP DATABASE \"scislisa-service\";"
docker exec postgres psql -U postgres -c "CREATE DATABASE \"scislisa-service\";"

# Run ingestion
python3 services/ingestion_service.py
```

### Adding New Faculty
1. Update `references/dblp/faculty_dblp_matched.json`
2. Download BibTeX file to `../dataset/dblp/`
3. Re-run ingestion

## Error Handling

The ingestion service:
- Logs all operations via Python logging
- Commits in batches (every 100 publications)
- Rolls back on errors
- Tracks statistics (successes/failures)
- Continues processing after individual errors

## Performance

Typical ingestion performance:
- **~1,321 publications** in ~30 seconds
- **~1,128 authors** created
- **~3,019 collaborations** identified
- **~685 venues** catalogued

## Future Enhancements

1. **Fuzzy Name Matching**: Handle name variations automatically
2. **Incremental Updates**: Only process new publications
3. **API Integration**: Direct DBLP API instead of static files
4. **Citation Analysis**: Parse citation networks
5. **Impact Metrics**: Calculate h-index, citations
