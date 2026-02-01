Database Export - 2026-02-01 04:32:51
================================================================================

This directory contains CSV exports of the SCISLiSA database.

Main Tables:
  - publications.csv: All publications (1,301 records)
  - authors.csv: All authors (1,090 records)
  - venues.csv: All venues (670 records)
  - collaborations.csv: Author-publication relationships
  - data_sources.csv: Data source tracking

Faculty-Specific Data:
  - faculty_authors.csv: 34 faculty members
  - faculty_publications.csv: Publications with faculty authors
  - publication_authors.csv: Detailed author-publication mapping

Statistics:
  - summary_statistics.csv: Overall database statistics
  - faculty_publication_stats.csv: Per-faculty publication counts
  - top_venues.csv: Top 50 venues by publication count

Notes:
  - Array fields (like source_pids) are semicolon-separated
  - Empty cells represent NULL values
  - All dates are in ISO format (YYYY-MM-DD)
