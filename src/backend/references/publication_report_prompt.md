# Publication Report Generation Prompt Template

## Purpose
This prompt template is designed to generate faculty research publication reports in the standardized format used by the School of Computer and Information Sciences (SCIS).

## Format Specification

### Structure
```
XII. School of Computer and Information Sciences

[Faculty Name]
[Category] [Number]. [Publication Type]: [Authors], [Author Role], [Title], [Indexing], [Volume/Issue], [Journal/Book/Conference Name], [Pages], [Date].
```

### Categories
- **A**: Books (Authored, Edited, Chapters)
- **B**: Research Papers (Journal Publications)
- **C**: Conference Proceedings

### Publication Types
1. **Category A:**
   - Books Authored
   - Books Edited
   - Books Chapter (Authorship)

2. **Category B:**
   - Research Papers

3. **Category C:**
   - Conference Proceedings

### Field Descriptions
1. **Authors**: Full list of authors (first name, last name)
2. **Author Role**: Co Author, Corresponding Author, First Author, etc.
3. **Title**: Full title of the publication
4. **Indexing**: Scopus, Web of Science, etc. (for research papers)
5. **Volume/Issue**: Journal volume/issue or Book ISBN
6. **Journal/Book/Conference Name**: Full name of the publication venue
7. **Pages**: Page numbers or article number
8. **Date**: Publication date in DD/MM/YYYY format

## Prompt for Report Generation

```
You are tasked with generating a research publication report for faculty members of the School of Computer and Information Sciences (SCIS) for the academic year 2024-2025.

INPUT DATA:
[Provide faculty publication data in any format - BibTeX, CSV, JSON, or plain text]

OUTPUT FORMAT:
Generate the report following this exact structure:

XII. School of Computer and Information Sciences

[Faculty Name]
[For each publication, organize by category (A, B, C) and number sequentially]
[Category] [Number]. [Publication Type]: [Full Citation Details]

REQUIREMENTS:
1. Group publications by faculty member
2. Within each faculty section, organize publications by category:
   - Category A: Books (Authored/Edited/Chapters)
   - Category B: Research Papers
   - Category C: Conference Proceedings
3. Number publications sequentially within each category
4. Include complete citation information:
   - All authors in order
   - Author role (Co Author, Corresponding Author, etc.)
   - Complete title
   - For research papers: Indexing (Scopus/Web of Science), Volume, Journal name, Pages
   - For books: ISBN, Editors, Publisher, Location
   - For conferences: Conference name, Volume/Series, ISBN (if applicable), Pages, Location
   - Publication date in DD/MM/YYYY format
5. Use proper formatting with consistent spacing and punctuation
6. Ensure dates are within academic year 2024-2025 (April 2024 - March 2025)

CITATION FORMAT EXAMPLES:

A 1. Books Authored: [Authors], [Role], [Title], [Edition], [Publisher], [Location], [ISBN], [Date].

A 2. Books Edited: [Editors], [Role], [Book Title], [Publisher], [Location], [Scope], [ISBN], [Date].

A 3. Books Chapter (Authorship): [Authors], [Chapter Title] in [Book Title] (ISBN: [ISBN]), Editor(s): [Editors], [Publisher], [Location], [Date], pp. [Pages].

B 1. Research Papers: [Authors], [Role], [Paper Title], [Indexing], [Volume], [Journal Name], [Pages], [Date].

C 1. Conference Proceedings: [Authors], [Role], [Paper Title], [Conference Series], [Volume], [ISBN], [Pages], [Conference Full Name], [Location], [Date].

QUALITY CHECKS:
- Verify all dates are in DD/MM/YYYY format
- Ensure proper capitalization of titles and names
- Check that ISBNs are complete and correctly formatted
- Confirm journal volumes and page numbers are accurate
- Validate that author roles are specified
- Ensure proper use of commas and periods in citations
```

## Usage Instructions

### For Manual Report Generation:
1. Copy the prompt template above
2. Replace `[Provide faculty publication data...]` with actual publication data
3. Submit to an AI system or use as a guide for manual compilation
4. Review and verify the output against source data

### For Automated Processing:
1. Parse source publication data (BibTeX, database exports, etc.)
2. Structure data according to the format specification
3. Apply the prompt template to generate formatted output
4. Validate against format requirements
5. Perform quality checks

## Data Collection Guidelines

### Required Information for Each Publication:
- [ ] Complete author list with proper name formatting
- [ ] Publication title (exactly as published)
- [ ] Publication venue (journal, book, conference)
- [ ] Publication date
- [ ] Volume/Issue or ISBN
- [ ] Page numbers or article number
- [ ] Author's role (Co Author, Corresponding Author, etc.)
- [ ] For research papers: Indexing information (Scopus/Web of Science)
- [ ] For books: Publisher, location, ISBN
- [ ] For conferences: Conference name, location, series information

### Common Data Sources:
- Faculty CVs
- Institutional repositories
- Google Scholar profiles
- DBLP database
- Scopus/Web of Science databases
- Publisher websites
- Conference proceedings

## Quality Assurance Checklist

- [ ] All faculty members included
- [ ] Publications organized by category (A, B, C)
- [ ] Sequential numbering within categories
- [ ] Complete citation information
- [ ] Consistent date format (DD/MM/YYYY)
- [ ] Proper author role identification
- [ ] ISBN/ISSN accuracy
- [ ] Journal/Conference names spelled correctly
- [ ] Page numbers included
- [ ] Proper punctuation and formatting
- [ ] Publications fall within target academic year

## Academic Year Definitions

### Standard Academic Year (India):
- **Start**: April 1, 2024
- **End**: March 31, 2025

### Calendar Year Alternative:
- **2024**: January 1, 2024 - December 31, 2024
- **2025**: January 1, 2025 - December 31, 2025

**Note**: Confirm the specific academic year definition with institutional requirements.

## Example Output Format

See `scis_publications.md` for complete examples of properly formatted publications.

## Contact & Support

For questions about format specifications or report generation:
- Review existing publications in `scis_publications.md`
- Consult institutional publication guidelines
- Verify citation formats with faculty members
