## Authors Pulbications Extraction from DBLP Source

This document explains how the data should be extracted from the DBLP source for the faculty members of the institute.

### Steps to Extract Data from DBLP
1. Extract the faculty members' names from the scis_uoh_faculty_details.html file
2. Search the faculty names in the dblp_author_details.csv file to get their DBLP author IDs.
3. Create the exclusive list of DBLP author IDs for the faculty members along with their names (provide all the duplicate names with same pids)
4. Use the DBLP API to extract the publication data (bib format) for each author using their DBLP author IDs.
    Save the publication data in separate files named as <author_pid>.bib under dataset/dblp directory (Note: replace '/' in pid with '_')
5. Analyse the bibliography information thoroughly and then ingest the extracted publication data into the database
    First Ingest into the locally running Postgres database and then migrate to the cloud hosted MongoDB database after local verification.    
6. Refer to the sample code and sample response sections for more clarity on using the DBLP API.

## Postgres Database Details
- Host: localhost
- Port: 5432
- Database Name: scislisa-service
- Username: postgres
- Password: postgres

## DBLP Reference Documentation

### Coauthor API Example

### Sample Code
```python
import requests

url = "https://dblp.org/pid/63/2890.json?view=coauthors"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

### Sample Response
```json
{
  "nodes": [
    {
      "name": "Ramesh Bobby Addanki",
      "urlpt": "a/Addanki:Ramesh_Bobby",
      "pid": "273/4291",
      "group": 0,
      "links": 3,
      "publs": 3
    },
    {
      "name": "Vivek Singh Baghel",
      "urlpt": "b/Baghel:Vivek_Singh",
      "pid": "234/0495",
      "group": 0,
      "links": 1,
      "publs": 11
    },
    {
      "name": "Venkatesh Bandaru",
      "urlpt": "b/Bandaru:Venkatesh",
      "pid": "63/10193",
      "group": 0,
      "links": 1,
      "publs": 1
    }
  ],
  "links": [
    {
      "source": 9,
      "target": 6,
      "value": 1
    },
    {
      "source": 13,
      "target": 10,
      "value": 8
    },
    {
      "source": 15,
      "target": 3,
      "value": 1
    }
  ]
}
```

## Author Bibliography API Example

### Sample Code
```python
import requests

url = "https://dblp.org/pid/63/2890.bib"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

### Sample Response
```bibtex

@article{DBLP:journals/tjs/GautamKB25,
  author       = {Rahul Kumar Gautam and
                  Anjeneya Swami Kare and
                  S. Durga Bhavani},
  title        = {Interest maximization in social networks},
  journal      = {J. Supercomput.},
  volume       = {81},
  number       = {1},
  pages        = {146},
  year         = {2025},
  url          = {https://doi.org/10.1007/s11227-024-06598-5},
  doi          = {10.1007/S11227-024-06598-5},
  timestamp    = {Sun, 22 Dec 2024 00:00:00 +0100},
  biburl       = {https://dblp.org/rec/journals/tjs/GautamKB25.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}

@inproceedings{DBLP:conf/bigda/KammariB24,
  author       = {Monachary Kammari and
                  S. Durga Bhavani},
  editor       = {Anirban Dasgupta and
                  Rage Uday Kiran and
                  Radwa El Shawi and
                  Satish Narayana Srirama and
                  Mainak Adhikari},
  title        = {Adaptive Temporal Random Walks for Graph Representation},
  booktitle    = {Big Data and Artificial Intelligence - 12th International Conference,
                  {BDA} 2024, Hyderabad, India, December 17-20, 2024, Proceedings},
  series       = {Lecture Notes in Computer Science},
  volume       = {15526},
  pages        = {75--91},
  publisher    = {Springer},
  year         = {2024},
  url          = {https://doi.org/10.1007/978-3-031-81821-9\_5},
  doi          = {10.1007/978-3-031-81821-9\_5},
  timestamp    = {Tue, 01 Apr 2025 01:00:00 +0200},
  biburl       = {https://dblp.org/rec/conf/bigda/KammariB24.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```


### Clarifications

Technology Stack: The README mentions Node.js/Express, but I recommend Python FastAPI for better integration with AI/data processing. Is this acceptable?
Ans: Yes, Python FastAPI is desirable for the backend implementation.

Database Migration: Should I implement MongoDB migration in this phase, or focus on Postgres first and validate data before cloud migration?
Ans: Focus on Postgres first and validate data before cloud migration.

AI Models: Are you planning to use specific Ollama models (e.g., llama3, mistral)? Do you have Ollama installed locally?
Ans: Yes, we plan to use llama3 and mistral models. Ollama is installed locally.

Frontend Preferences: Any specific design preferences or should I create a modern, clean dashboard-style UI?
Ans: Create a modern, clean dashboard-style UI which supports interactive visualizations including charts, graphs, tables, summaries and insights etc..
