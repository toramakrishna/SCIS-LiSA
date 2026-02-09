#!/usr/bin/env python3
"""
Test script for publication report generation
Tests the enhanced agent.py with report generation capability
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp.agent import OllamaAgent


async def test_report_generation():
    """Test various report generation queries"""
    
    print("=" * 80)
    print("Testing Publication Report Generation")
    print("=" * 80)
    
    agent = OllamaAgent()
    
    test_queries = [
        # Basic report requests
        "Generate publication report for Satish Narayana Srirama",
        "Generate publication report for Siba Kumar Udgata in SCIS format",
        "List all publications of Salman Abdul Moiz in the format mentioned in scis_publications.md",
        
        # Report with specific formatting
        "Show all publications by Anjeneya Swami Kare in the below format:\nCategory Number. Type: Authors, Title, Venue, Year",
        
        # Regular queries (should not trigger report mode)
        "How many publications does Satish Srirama have?",
        "Show publication trends over the years",
        "List recent publications by Udgata"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_queries)}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        try:
            result = await agent.generate_sql(query)
            
            print("\n📊 RESULT:")
            print(f"   Visualization Type: {result.get('visualization', 'N/A')}")
            print(f"   Is Report Mode: {result.get('visualization') == 'report'}")
            
            if 'sql' in result and result['sql']:
                print(f"\n📝 SQL Query:")
                print(f"   {result['sql'][:200]}...")
            
            if 'explanation' in result:
                print(f"\n💡 Explanation:")
                print(f"   {result['explanation']}")
            
            if 'note' in result:
                print(f"\n📌 Note:")
                print(f"   {result['note']}")
            
            if result.get('visualization') == 'report':
                print(f"\n✅ REPORT MODE ACTIVATED")
                if 'report_format' in result:
                    print(f"   Report Format: {result['report_format'][:100]}...")
                if 'categorization' in result:
                    print(f"   Categories: {result['categorization']}")
            
            if 'error' in result:
                print(f"\n❌ ERROR: {result['error']}")
            
        except Exception as e:
            print(f"\n❌ Exception occurred: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()  # Blank line between tests
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)


async def test_single_report():
    """Test a single report generation with detailed output"""
    
    print("=" * 80)
    print("Detailed Single Report Test")
    print("=" * 80)
    
    agent = OllamaAgent()
    
    query = "Generate publication report for Satish Narayana Srirama in SCIS standard format"
    
    print(f"\nQuery: {query}\n")
    
    result = await agent.generate_sql(query)
    
    print("\n" + "=" * 80)
    print("COMPLETE RESULT JSON:")
    print("=" * 80)
    print(json.dumps(result, indent=2))
    print()


if __name__ == "__main__":
    # Check if detailed mode requested
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        asyncio.run(test_single_report())
    else:
        asyncio.run(test_report_generation())
