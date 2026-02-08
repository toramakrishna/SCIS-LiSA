#!/usr/bin/env python3
"""
Final verification of all updated suggested queries
"""
import requests
import json

API_URL = "http://localhost:8000/api/v1/mcp/query"

# Updated suggested queries from frontend
QUERIES = [
    'Show top 10 faculty by publication count',
    'What are the publication trends over the last 5 years?',
    'List the most cited publications',
    'Show collaboration network between faculty members',
    'What are the top conferences where faculty publish?',
    'Show all faculty with h-index greater than 10',
]

print("="*80)
print("FINAL VERIFICATION OF ALL SUGGESTED QUERIES")
print("="*80)
print()

results = []

for query in QUERIES:
    print(f"Testing: {query}")
    
    response = requests.post(
        API_URL,
        json={"question": query},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        row_count = data.get('row_count', 0)
        viz_type = data.get('visualization', {}).get('type', 'unknown')
        error = data.get('error')
        sql = data.get('sql', '')
        has_limit = 'LIMIT' in sql
        
        if error:
            status = f"❌ ERROR: {error}"
            results.append((query, status))
        elif row_count == 0:
            status = "❌ NO RESULTS"
            results.append((query, status))
        else:
            status = f"✅ {row_count} rows, {viz_type}"
            if not has_limit:
                status += " (no LIMIT)"
            results.append((query, status))
        
        print(f"  {status}")
    else:
        status = f"❌ HTTP {response.status_code}"
        results.append((query, status))
        print(f"  {status}")
    
    print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
for query, status in results:
    print(f"{status[:2]} {query}")
    print(f"   {status[2:]}")

passed = sum(1 for _, s in results if '✅' in s)
total = len(results)
print(f"\n{passed}/{total} queries passed")
print()
