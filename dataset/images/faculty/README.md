# Faculty Profile Images

This directory contains profile photos downloaded from IRINS (Indian Research Information Network System).

## Source
Photos are downloaded from: https://uohyd.irins.org/profile_images/

## Naming Convention
Images are named with their IRINS profile ID:
- `71829.jpg` - Profile photo for IRINS profile 71829
- `112626.png` - Profile photo for IRINS profile 112626
- etc.

## Auto-generated
These images are automatically downloaded when running the IRINS extraction script:
```bash
cd /workspaces/SCIS-LiSA/src/backend
python3 extract_irins_profiles.py
```

## Usage
The `photo_path` field in `faculty_data.json` references these images:
```json
{
  "name": "Faculty Name",
  "irins_profile": "71829",
  "photo_path": "dataset/images/faculty/71829.jpg"
}
```
