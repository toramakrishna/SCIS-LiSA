#!/usr/bin/env python3
"""
Test all suggested queries from the frontend to verify SQL generation and execution
"""
import asyncio
import json
from sqlalchemy import text
from mcp.agent import OllamaAgent
from config.db_config import engine

# All suggested queries from frontend
SUGGESTED_QUERIES = [
    'Show top 10 faculty by publication count',
    'What are the publication trends over the last 5 years?',
    'List the most cited publications',
    'Show collaborations between faculty members',
    'Which venues have the most publications?',
    'Show faculty with h-index greater than 10',
    # User mentioned this one
    'What are the top conferences where faculty publish?',
]

async def test_query(agent, question):
    """Test a single query"""
    print(f"\n{'='*80}")
    print(f"QUESTION: {question}")
    print(f"{'='*80}")
    
    try:
        # Generate SQL
        result = await agent.generate_sql(question)
        
        print(f"\n📊 Visualization: {result.get('visualization', 'N/A')}")
        print(f"💡 Explanation: {result.get('explanation', 'N/A')}")
        if result.get('note'):
            print(f"📝 Note: {result['note']}")
        
        print(f"\n🔍 SQL Query:")
        print(result['sql'])
        
        # Execute the SQL
        print(f"\n⚙️  Executing query...")
        with engine.connect() as conn:
            sql_result = conn.execute(text(result['sql']))
            rows = sql_result.fetchall()
            
            if len(rows) == 0:
                print(f"❌ NO RESULTS RETURNED - Query needs fixing!")
                return False
            else:
                print(f"✅ SUCCESS: {len(rows)} rows returned")
                
                # Show first few results
                print(f"\nSample results (first 3 rows):")
                for i, row in enumerate(rows[:3], 1):
                    print(f"  {i}. {row}")
                
                return True
                
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Test all suggested queries"""
    agent = OllamaAgent()
    
    print("=" * 80)
    print("TESTING ALL SUGGESTED QUERIES")
    print("=" * 80)
    
    results = {}
    for question in SUGGESTED_QUERIES:
        success = await test_query(agent, question)
        results[question] = '✅ PASS' if success else '❌ FAIL'
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    for question, status in results.items():
        print(f"{status} - {question}")
    
    passed = sum(1 for v in results.values() if '✅' in v)
    total = len(results)
    print(f"\n{passed}/{total} queries passed")

if __name__ == "__main__":
    asyncio.run(main())
