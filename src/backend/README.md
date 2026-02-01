# SCISLiSA Backend

Backend service for the SCIS Literature and Scholarship Analytics system.

## Overview

Production-ready data ingestion and processing pipeline for faculty publication analytics. Processes DBLP BibTeX files, matches faculty members, prevents duplicates, and creates a comprehensive research database.

## Verified Results

✅ **34/34 faculty** - 100% publication count accuracy  
✅ **18/18 matched faculty** - 100% data integrity  
✅ **1,321 publications** - All unique, properly deduplicated  
✅ **1,128 authors** - Faculty and co-authors correctly identified  
✅ **3,019 collaborations** - Co-authorship relationships tracked  

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (Docker or local)
- DBLP BibTeX files in `../dataset/dblp/`

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure PostgreSQL is running
docker ps | grep postgres

# Create database
docker exec postgres psql -U postgres -c "CREATE DATABASE \"scislisa-service\";"
```

### Run Complete Pipeline

```bash
# 1. Run ingestion
python3 services/ingestion_service.py

# 2. Merge duplicate author records (for name variations)
python3 utils/merge_faculty_duplicates.py

# 3. Verify data integrity
python3 utils/verify_dblp_counts.py
```

## Structure

```
src/backend/
├── config/          # Database configuration
├── models/          # SQLAlchemy ORM models
├── parsers/         # BibTeX parsing logic
├── services/        # Core ingestion service
├── sources/         # Data source adapters (DBLP)
├── utils/           # Verification and reporting tools
├── references/      # Faculty data and DBLP matching
└── PIPELINE_GUIDE.md  # Detailed documentation
```

## Database Schema

**Authors**: Faculty members and co-authors with statistics  
**Publications**: Research papers with full metadata  
**Collaborations**: Co-authorship relationships  
**Venues**: Journals and conferences  
**DataSource**: Source tracking and sync info

**Multi-PID Support:**
Co-authored papers between faculty are tracked with multiple source PIDs:
```python
source_pids: ['50/971', '91/1525']  # Paper by Subba Rao & Chakravarthy
```

## Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 15+ (Docker recommended)
- Required packages in `requirements.txt`

### Installation

1. **Start PostgreSQL:**
```bash
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
docker exec postgres psql -U postgres -c "CREATE DATABASE \"scislisa-service\";"
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify faculty DBLP PIDs:**
```bash
python3 references/match_dblp_pids.py
```

## Usage

### Run Complete Ingestion Pipeline

```bash
cd src/backend
python3 services/ingestion_service.py
```

**Output:**
```
Step 1: Initializing database schema...
✓ Database schema initialized

Step 2: Parsing BibTeX files...
✓ Parsed 1321 unique publications from 46 files

Step 3: Loading faculty mapping...
✓ Loaded 34 faculty members

Step 4: Ingesting data into PostgreSQL...
✓ Data ingestion complete

Publications Added: 1321
Authors Added: 77
Errors: 0
```

### Generate Faculty Report

```bash
python3 utils/faculty_report.py
```

Shows ranked list of faculty by publication count with co-authorship statistics.

### Validate Against DBLP

```bash
python3 utils/verify_dblp_counts.py
```

Fetches publication counts from DBLP website and compares with database.
**Expected result:** 34/34 exact matches (100%)

### View Database Statistics

```bash
python3 utils/show_db_stats.py
```

## Data Flow

```
DBLP Website
    ↓
[Download .bib files]
    ↓
BibTeX Parser (bibtex_parser.py)
    ├─ Extract publications
    ├─ Deduplicate by DBLP key + DOI
    └─ Track source PIDs
    ↓
Ingestion Service (ingestion_service.py)
    ├─ Create publications
    ├─ Link authors
    ├─ Mark faculty by PID
    └─ Build relationships
    ↓
PostgreSQL Database
    ↓
[Faculty Report / API / Web Interface]
```

## Key Implementation Details

### Deduplication Strategy

**CORRECT (Current):**
- Deduplicate by DBLP key (always unique)
- Deduplicate by DOI (if present)
- ❌ NOT by title (can have variations)

**Example Issue (Fixed):**
Two different papers had similar titles but different DBLP keys:
- `DBLP:journals/ijnsec/VB14` - Vol 16(3)
- `DBLP:journals/ijnsec/RaoB14` - Vol 16(4)

Title normalization incorrectly treated them as duplicates. Now fixed!

### Multi-PID Tracking

Publications appearing in multiple faculty .bib files are aggregated:

```python
# parse_all_bib_files() in bibtex_parser.py
if dblp_key in publication_index:
    # Add this faculty's PID to existing publication
    existing_pub['source_pids'].append(source_pid)
else:
    # New publication
    pub['source_pids'] = [source_pid]
    publication_index[dblp_key] = pub
```

### Faculty Identification

**PID-First Approach:**
- Mark ALL authors from faculty publications as potential faculty
- Use `source_pids` to identify which faculty authored the paper
- No name matching required (handles name variations automatically)

## Validation Results

### Final Statistics (Validated 2026-02-01)

| Metric | Count |
|--------|-------|
| Total Publications | 1,321 |
| Faculty Authors | 34 |
| Total Authors (including collaborators) | 77 |
| Co-authored Papers | 443 |
| Venues | 685 |
| **DBLP Match Rate** | **100%** ✓ |

### Top Faculty by Publications

1. Satish Srirama - 197 publications
2. Bapi Raju S. - 139 publications  
3. Arun K Pujari - 113 publications
4. Alok Singh - 97 publications
5. Atul Negi - 91 publications

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker restart postgres
```

### Ingestion Errors
```bash
# Drop and recreate database
docker exec postgres psql -U postgres -c "DROP DATABASE \"scislisa-service\";"
docker exec postgres psql -U postgres -c "CREATE DATABASE \"scislisa-service\";"

# Re-run ingestion
python3 services/ingestion_service.py
```

### DBLP Validation Mismatches
If validation shows mismatches:
1. Check if .bib files are up to date
2. Verify faculty DBLP PIDs in `references/dblp/faculty_dblp_matched.json`
3. Re-run ingestion pipeline

## Next Steps

- [x] Build FastAPI REST API
- [x] Implement MCP agent with Ollama
- [ ] Create React frontend with D3.js visualizations
- [ ] Add Google Scholar integration
- [ ] Implement citation analysis
- [ ] Deploy to production

## License

Academic use for University of Hyderabad, School of Computer and Information Sciences.
