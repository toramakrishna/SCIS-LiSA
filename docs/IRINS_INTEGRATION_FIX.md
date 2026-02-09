# IRINS and Scopus Data Integration Fix

## Problem Summary

The IRINS and Scopus-related fields (profile pictures, IRINS links, Scopus IDs, h-index) were not being populated in the database during data ingestion from the Admin Page, even though:
- The `faculty_data.json` file contained all the IRINS and Scopus data
- The database schema (Author model) had the necessary fields
- The API schemas included these fields
- The frontend components were ready to display them

## Root Cause

The **ingestion service** (`src/backend/services/ingestion_service.py`) was not loading or transferring IRINS and Scopus fields from `faculty_data.json` to the database during the ingestion pipeline.

Specifically:
1. The `load_faculty_mapping()` method was not extracting these fields from `faculty_data.json`
2. The `get_or_create_author()` method was not setting these fields when creating or updating authors
3. The `update_faculty_extended_info()` method was also missing these fields in its update logic

## Changes Made

### 1. Updated `load_faculty_mapping()` method
**File:** `src/backend/services/ingestion_service.py` (lines ~460-483)

Added the following fields to the `faculty_info` dictionary:

```python
# IRINS fields
'irins_profile': faculty.get('irins_profile'),
'irins_url': faculty.get('irins_url'),
'irins_photo_url': faculty.get('irins_photo_url'),
'photo_path': faculty.get('photo_path'),

# Scopus fields
'scopus_author_id': faculty.get('scopus_author_id'),
'scopus_url': faculty.get('scopus_url'),
'h_index': faculty.get('h_index')
```

### 2. Updated `get_or_create_author()` method
**File:** `src/backend/services/ingestion_service.py` (lines ~78-127)

**For existing authors (update section):**
```python
# IRINS fields
author.irins_profile = faculty_data.get('irins_profile') or author.irins_profile
author.irins_url = faculty_data.get('irins_url') or author.irins_url
author.irins_photo_url = faculty_data.get('irins_photo_url') or author.irins_photo_url
author.photo_path = faculty_data.get('photo_path') or author.photo_path

# Scopus fields
author.scopus_author_id = faculty_data.get('scopus_author_id') or author.scopus_author_id
author.scopus_url = faculty_data.get('scopus_url') or author.scopus_url
author.h_index = faculty_data.get('h_index') or author.h_index
```

**For new authors (create section):**
```python
# IRINS fields
irins_profile=faculty_data.get('irins_profile') if faculty_data else None,
irins_url=faculty_data.get('irins_url') if faculty_data else None,
irins_photo_url=faculty_data.get('irins_photo_url') if faculty_data else None,
photo_path=faculty_data.get('photo_path') if faculty_data else None,

# Scopus fields
scopus_author_id=faculty_data.get('scopus_author_id') if faculty_data else None,
scopus_url=faculty_data.get('scopus_url') if faculty_data else None,
h_index=faculty_data.get('h_index') if faculty_data else None
```

### 3. Updated `update_faculty_extended_info()` method
**File:** `src/backend/services/ingestion_service.py` (lines ~595-630)

Added logic to update IRINS and Scopus fields for existing faculty:

```python
# Update IRINS fields
if not author.irins_profile and faculty.get('irins_profile'):
    author.irins_profile = faculty.get('irins_profile')
if not author.irins_url and faculty.get('irins_url'):
    author.irins_url = faculty.get('irins_url')
if not author.irins_photo_url and faculty.get('irins_photo_url'):
    author.irins_photo_url = faculty.get('irins_photo_url')
if not author.photo_path and faculty.get('photo_path'):
    author.photo_path = faculty.get('photo_path')

# Update Scopus fields
if not author.scopus_author_id and faculty.get('scopus_author_id'):
    author.scopus_author_id = faculty.get('scopus_author_id')
if not author.scopus_url and faculty.get('scopus_url'):
    author.scopus_url = faculty.get('scopus_url')
if not author.h_index and faculty.get('h_index'):
    author.h_index = faculty.get('h_index')
```

### 4. Updated Migration Script
**File:** `src/backend/migrations/add_irins_profile_fields.py` (lines ~77-95)

Added Scopus field updates to the migration script:

```python
# Update Scopus fields if they exist in JSON
if 'scopus_author_id' in fac:
    author.scopus_author_id = fac['scopus_author_id']
if 'scopus_url' in fac:
    author.scopus_url = fac['scopus_url']
if 'h_index' in fac:
    author.h_index = fac['h_index']
```

## Data Flow (After Fix)

```
faculty_data.json
    ↓
load_faculty_mapping() → Extracts all fields including IRINS/Scopus
    ↓
faculty_mapping dict → Contains complete faculty information
    ↓
get_or_create_author() → Creates/updates authors with IRINS/Scopus data
    ↓
Database (authors table) → Stores complete faculty profiles
    ↓
Faculty API → Returns all fields via FacultySchema
    ↓
Frontend (FacultyCard) → Displays profile pics, IRINS links, h-index, etc.
```

## Testing Instructions

### Option 1: Re-ingest Data (Recommended for Clean State)

1. **Backup Database (if needed):**
   ```bash
   cd /workspaces/SCIS-LiSA/src/backend
   bash ../../scripts/backup_database.sh
   ```

2. **Navigate to Admin Page:**
   - Go to `http://localhost:5173/admin`
   - Use the "Ingest Data" feature
   - Select dataset path: `dataset/dblp`
   - Click "Start Ingestion"
   - Wait for completion

3. **Verify Faculty Page:**
   - Go to `http://localhost:5173/faculty`
   - You should now see:
     - Faculty profile pictures
     - H-Index badges
     - IRINS profile links (if available)
     - Scopus profile links (if available)

### Option 2: Run Migration Script (For Existing Data)

If you want to update existing faculty records without re-ingesting all publications:

```bash
cd /workspaces/SCIS-LiSA/src/backend
python3 migrations/add_irins_profile_fields.py
```

This will:
- Add missing database columns (if needed)
- Update all existing faculty with IRINS and Scopus data from `faculty_data.json`

### Option 3: Test Individual Functions

**Test loading faculty mapping:**
```python
from services.ingestion_service import DatabaseIngestionService
from config.db_config import SessionLocal

db = SessionLocal()
service = DatabaseIngestionService(db)
faculty_mapping = service.load_faculty_mapping('references/faculty_data.json')

# Check if IRINS fields are present
sample_faculty = list(faculty_mapping['by_pid'].values())[0]
print("Sample faculty data:", sample_faculty)
# Should include: irins_profile, irins_url, scopus_author_id, h_index, etc.
```

**Check database records:**
```python
from models.db_models import Author
from config.db_config import SessionLocal

db = SessionLocal()
faculty = db.query(Author).filter(Author.is_faculty == True).first()

print(f"\nFaculty: {faculty.name}")
print(f"IRINS Profile: {faculty.irins_profile}")
print(f"IRINS URL: {faculty.irins_url}")
print(f"Photo Path: {faculty.photo_path}")
print(f"Scopus ID: {faculty.scopus_author_id}")
print(f"H-Index: {faculty.h_index}")
```

## Verification Checklist

After testing, verify the following:

- [ ] Faculty profile pictures are displayed on the Faculty page
- [ ] H-Index badges are shown for faculty who have them
- [ ] IRINS profile links are clickable and point to correct IRINS pages
- [ ] Scopus profile links are present for faculty with Scopus IDs
- [ ] Photo paths are correctly served (check browser console for 404 errors)
- [ ] All IRINS fields are populated in the database (use SQL query or API)

## Expected Results

### API Response Sample
```json
{
  "id": 1,
  "name": "Siba K. Udgata",
  "designation": "Professor and Dean",
  "email": "deanscis@uohyd.ac.in",
  "phone": "91-040-23134101",
  "h_index": 18,
  "scopus_author_id": "6505814190",
  "scopus_url": "https://www.scopus.com/authid/detail.uri?authorId=6505814190",
  "irins_profile": "71829",
  "irins_url": "https://uohyd.irins.org/profile/71829",
  "irins_photo_url": "https://uohyd.irins.org/profile_images/71829.jpg",
  "photo_path": "dataset/images/faculty/71829.jpg",
  "education": "Ph.D, Berhampur University (Odisha), India",
  "areas_of_interest": "Mobile Computing, Networks and Architecture",
  ...
}
```

### Database Query
```sql
SELECT 
    name, 
    irins_profile, 
    irins_url, 
    photo_path, 
    scopus_author_id, 
    h_index
FROM authors
WHERE is_faculty = true
LIMIT 5;
```

Should return rows with populated IRINS and Scopus fields.

## Troubleshooting

### Profile pictures not showing
1. Check if `photo_path` exists in database
2. Verify the image files exist at the specified paths
3. Check frontend is correctly constructing the URL (should be `/${faculty.photo_path}`)
4. Look for 404 errors in browser console

### IRINS fields are NULL
1. Verify `faculty_data.json` contains the IRINS data
2. Run the migration script: `python3 migrations/add_irins_profile_fields.py`
3. Re-ingest data from Admin page
4. Check backend logs for any errors during ingestion

### H-Index not displayed
1. Verify `h_index` field is an integer in `faculty_data.json`
2. Check if the FacultyCard component is rendering the h_index badge
3. Inspect the API response to confirm h_index is present

## Related Files

- **Backend:**
  - `src/backend/services/ingestion_service.py` - Main ingestion logic
  - `src/backend/models/db_models.py` - Author model with IRINS fields
  - `src/backend/api/schemas.py` - FacultySchema with IRINS fields
  - `src/backend/migrations/add_irins_profile_fields.py` - Migration script
  - `src/backend/references/faculty_data.json` - Source data

- **Frontend:**
  - `src/frontend/src/components/faculty/FacultyCard.tsx` - Faculty display component
  - `src/frontend/src/types/index.ts` - Author type definition
  - `src/frontend/src/pages/FacultyPage.tsx` - Faculty list page

## Summary

This fix ensures that all IRINS and Scopus data from `faculty_data.json` is properly:
1. ✅ Loaded during the ingestion pipeline
2. ✅ Stored in the database
3. ✅ Returned by the API
4. ✅ Displayed on the frontend

The integration is now complete end-to-end.
