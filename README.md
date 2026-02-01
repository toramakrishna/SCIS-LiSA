# SCISLiSA - SCIS Literature and Scholarship Analytics

A production-ready data analytics platform for faculty publication tracking and research collaboration analysis.

## 🎯 Objective

Create an Agentic AI-enabled interactive web application using Model Context Protocol that provides complete information, analysis, and visualization of faculty publications by retrieving data from various sources like DBLP, Scopus, Google Scholar, Semantic Scholar, ORCID, etc.

### Current Status: Phase 1 Complete ✅

**DBLP Backend Pipeline** - Production-ready with 100% data accuracy
- ✅ 34/34 faculty publication counts verified against live DBLP
- ✅ 1,321 publications ingested with zero errors
- ✅ 1,128 authors tracked (faculty + collaborators)
- ✅ 3,019 collaboration relationships mapped

## 📊 Features

### Phase 1: DBLP Data Pipeline (Completed)
- **Data Retrieval**: DBLP BibTeX ingestion with intelligent parsing
- **Author Matching**: Name-based faculty identification with duplicate handling
- **Data Integrity**: 100% verified accuracy with comprehensive validation tools
- **Deduplication**: DBLP key-based publication deduplication
- **Multi-PID Tracking**: Co-authored papers attributed to all faculty authors

### Phase 2: Multi-Source Integration (Planned)
- Data Retrieval from Scopus, Google Scholar, Semantic Scholar, ORCID
- Cross-source publication matching and merging
- Citation count aggregation

### Phase 3: Analytics & Visualization (Planned)
- Publication trends over time
- Citation analysis and h-index tracking
- Collaboration network graphs
- Interactive dashboards with D3.js

### Phase 4: AI Assistant (Planned)
- Agentic AI for querying publication data
- Natural language interaction
- Model Context Protocol integration
- Locally hosted Ollama models

## 🏗️ Architecture

```
SCISLiSA/
├── src/
│   ├── backend/           # ✅ Python data ingestion (DBLP complete)
│   │   ├── services/      # Core ETL pipeline
│   │   ├── models/        # PostgreSQL ORM models
│   │   ├── parsers/       # BibTeX parsing
│   │   ├── utils/         # Verification & reporting tools
│   │   └── references/    # Faculty mapping data
│   └── frontend/          # 🔜 React.js (planned)
├── dataset/
│   └── dblp/             # BibTeX source files (46 files)
└── docs/                 # Documentation
```

## 🚀 Quick Start

See **[Backend README](src/backend/README.md)** for complete setup instructions.

```bash
# Clone and setup
git clone https://github.com/drtoramakrishna/SCISLiSA.git
cd SCISLiSA/src/backend

# Install dependencies
pip install -r requirements.txt

# Run DBLP ingestion pipeline
python3 services/ingestion_service.py
python3 utils/merge_faculty_duplicates.py
python3 utils/verify_dblp_counts.py
```

## 📚 Documentation

- **[Backend README](src/backend/README.md)** - Quick start and structure
- **[Pipeline Guide](src/backend/PIPELINE_GUIDE.md)** - Detailed architecture
- **[Data Verification Report](src/backend/DATA_VERIFICATION_REPORT.md)** - Known limitations
- **[Pre-Commit Checklist](src/backend/PRE_COMMIT_CHECKLIST.md)** - Testing guide

## 🔧 Technologies Used

### Current (Phase 1)
- **Backend**: Python 3.9+, SQLAlchemy
- **Database**: PostgreSQL (Docker)
- **Data Source**: DBLP BibTeX files
- **Parsing**: bibtexparser
- **Validation**: requests, BeautifulSoup4 (DBLP API)

### Planned (Future Phases)
- **Frontend**: React.js, D3.js
- **APIs**: Scopus, Google Scholar, Semantic Scholar, ORCID
- **AI**: Ollama (local models), Model Context Protocol
- **Additional DB**: MongoDB (for unstructured data)

## 📈 Current Statistics

```
Database: scislisa-service
Publications: 1,321 (100% unique)
Authors: 1,128 (18 faculty matched, 1,110 collaborators)
Venues: 685 (journals + conferences)
Collaborations: 3,019 (co-authorship relationships)
Faculty Coverage: 34/34 verified (100% accuracy)
Data Quality: Zero errors
```

## 🤝 Contributing

This project follows standard Python development practices:
- **Code Style**: PEP 8
- **Logging**: Python logging module
- **Testing**: Run pre-commit checklist before pushing
- **Documentation**: Update README when adding features

## 👥 Authors

- **Dr. Toramakrishna** - Lead Developer
- School of Computer and Information Sciences, University of Hyderabad

## 🙏 Acknowledgments

- DBLP Computer Science Bibliography for publication data
- Faculty of SCIS, University of Hyderabad

---

**Phase 1 Status**: Production-ready ✅  
**Last Updated**: December 2024  
**Version**: 1.0.0

## MongoDB Details
username: drtorkrishna_db_user
password: <password>