# IRINS Data Extraction Script - Pre-Run Verification

## What the script will do:

### 1. Extract from HTML
- **IRINS Profile IDs** (e.g., 71829, 107769, etc.)
- **IRINS Profile URLs** (e.g., https://uohyd.irins.org/profile/71829)
- **Photo URLs** (e.g., https://uohyd.irins.org/profile_images/71311.png)

### 2. Download Photos
- Creates directory: `dataset/images/faculty/`
- Downloads all faculty profile photos from IRINS
- Saves them locally with original filenames (e.g., 71311.png, 112626.png)

### 3. Update JSON
For each matched faculty, adds these new fields to `faculty_data.json`:
- `irins_profile`: The profile ID number
- `irins_url`: Full IRINS profile URL
- `irins_photo_url`: Original photo URL from IRINS
- `photo_path`: Local path to downloaded photo (e.g., "dataset/images/faculty/71311.png")

### 4. Preserves Existing Data
**IMPORTANT:** The script does NOT modify:
- ✓ `designation` field (remains unchanged)
- ✓ `name`, `email`, `phone` fields
- ✓ `education`, `areas_of_interest` fields
- ✓ All existing DBLP data

### 5. Name Matching Strategy
The script uses intelligent name matching:
- Removes titles (Prof, Dr, Mr, etc.)
- Handles name variations (e.g., "Dr Vineet C Padmanabhan Nair" matches "Vineet C. P. Nair")
- Matches on name similarity (60%+ overlap)

## Expected Output:

Based on the 29 faculty in HTML and 34 in JSON:
- **~25 matches expected** (faculty with IRINS profiles)
- **~25 photos will be downloaded**
- **~9 faculty without IRINS profiles** (newer faculty or not in IRINS system)

## Files Modified:
- `references/faculty_data.json` - Updated with IRINS data
- `dataset/images/faculty/` - New directory with downloaded photos

## Files Created:
- Multiple `.jpg`, `.png`, `.JPG`, `.PNG` files in `dataset/images/faculty/`

## To Run:
```bash
cd /workspaces/SCIS-LiSA/src/backend
python3 extract_irins_profiles.py
```

## Verification Checklist:
- [ ] Directory structure looks correct
- [ ] Script will download photos to `dataset/images/faculty/`
- [ ] JSON will be updated with new fields
- [ ] Designation field will NOT be modified
- [ ] Ready to run the script
