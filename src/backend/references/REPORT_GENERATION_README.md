# Publication Report Generation - Quick Start

## What's New

The SCIS-LiSA system can now automatically generate **standardized publication reports** in SCIS format when users request them through the Query page.

## How to Use

### From Query Page

Simply ask natural language questions like:

```
Generate publication report for Satish Narayana Srirama
```

```
List all publications of Siba Kumar Udgata in SCIS format
```

```
Show publications by Salman Abdul Moiz in the format mentioned
```

The system will automatically:
1. ✅ Detect it's a report request
2. ✅ Query ALL publications for that faculty member
3. ✅ Organize by categories (A: Books, B: Papers, C: Conferences)
4. ✅ Format in SCIS standard citation style
5. ✅ Return with download option

## Report Format

Publications are organized in three categories:

- **Category A**: Books (Authored/Edited/Chapters)
- **Category B**: Research Papers (Journal Publications)
- **Category C**: Conference Proceedings

Each publication follows SCIS citation format:
```
[Category] [Number]. [Type]: [Authors], [Role], [Title], [Venue], [Year], [Pages].
```

## Example Output

```
XII. School of Computer and Information Sciences

Satish Narayana Srirama
A 1. Books Authored: R. Buyya, C. Vecchiola, S. T. Selvi, S. Poojara, S. N. Srirama, 
     Corresponding Author, Mastering Cloud Computing: Powering AI, Big Data, and IoT 
     Applications, 2nd Edition, Mc Graw Hill, India, ISBN-13: 978-93-5532-950-9, 01/07/2024.

B 1. Research Papers: T. R. Chhetri, C. K. Dehury, B. Varghese, Anna Fensel, S. N. Srirama, 
     Rance J. DeLong, Co Author, Enabling privacy-aware interoperable and quality IoT data 
     sharing with context, Web of Science, 157, Future Generation Computer Systems - Journal, 
     164-179, 01/08/2024.

C 1. Conference Proceedings: Chinmaya Kumar Dehury, Satish Narayana Srirama, Integrating 
     Serverless and DRL for Infrastructure Management in Streaming Data Processing across 
     Edge-Cloud Continuum, 93-101, New Jersey, USA, 23/07/2024.
```

## Files Created

1. **`publication_report_prompt.md`** - Format specifications and prompt template
2. **`scis_publications_analysis_2024-2025.md`** - Complete 2024-25 publication analysis
3. **`test_report_generation.py`** - Test script for verification

## Files Modified

1. **`agent.py`** - Enhanced with report detection and generation
2. **`schema_context.py`** - Added publication_report example

## Testing

```bash
cd /home/24mcpc14/tork/github.com/toramakrishna/SCIS-LiSA/src/backend

# Quick test
python test_report_generation.py

# Detailed test with full output
python test_report_generation.py --detailed
```

## Documentation

See `/docs/PUBLICATION_REPORT_ENHANCEMENT.md` for complete documentation including:
- Technical implementation details
- SQL query structure
- Frontend integration guide
- Troubleshooting tips

## Key Features

✅ **Automatic Detection** - No special commands needed
✅ **Complete Data** - Returns ALL publications (no limits)
✅ **Proper Categorization** - A/B/C categories as per SCIS standard
✅ **All Metadata** - Authors, venue, volume, pages, DOI, etc.
✅ **Flexible Names** - Handles name variations automatically
✅ **Download Ready** - Formatted for official use

## Keywords That Trigger Report Mode

- "generate report"
- "publication report"
- "in SCIS format"
- "in the format"
- "format as mentioned"
- "category A/B/C"
- "standard format"

## Support

- **Documentation**: `/docs/PUBLICATION_REPORT_ENHANCEMENT.md`
- **Format Guide**: `/src/backend/references/publication_report_prompt.md`
- **Example Report**: `/src/backend/references/scis_publications.md`
- **Test Script**: `/src/backend/test_report_generation.py`
