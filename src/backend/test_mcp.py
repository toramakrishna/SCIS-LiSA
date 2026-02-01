"""
Test MCP Agent - Quick validation script
"""

import asyncio
import json
from mcp.agent import OllamaAgent
from config.db_config import get_postgres_db


async def test_mcp_agent():
    """Test the MCP agent with sample questions"""
    
    print("="*80)
    print("MCP AGENT TEST SUITE")
    print("="*80)
    print()
    
    # Initialize agent
    agent = OllamaAgent()
    db = next(get_postgres_db())
    
    test_cases = [
        {
            "question": "Show publication trends over the last 5 years",
            "expected_viz": "line_chart"
        },
        {
            "question": "Who are the top 5 most productive faculty members?",
            "expected_viz": "bar_chart"
        },
        {
            "question": "What are the top 10 publication venues?",
            "expected_viz": "bar_chart"
        },
        {
            "question": "How many publications did Satish Srirama publish in 2024?",
            "expected_viz": "table"
        },
        {
            "question": "Show distribution of publication types",
            "expected_viz": "pie_chart"
        }
    ]
    
    results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"TEST {i}: {test['question']}")
        print(f"{'─'*80}")
        
        try:
            # Generate SQL
            gen_result = await agent.generate_sql(test['question'])
            
            if 'error' in gen_result:
                print(f"❌ FAILED - Generation Error: {gen_result['error']}")
                results['failed'] += 1
                results['errors'].append({
                    "test": i,
                    "question": test['question'],
                    "error": gen_result['error']
                })
                continue
            
            print(f"\n📝 Generated SQL:")
            print(gen_result['sql'])
            print(f"\n📊 Visualization: {gen_result['visualization']}")
            print(f"💡 Explanation: {gen_result['explanation']}")
            
            # Execute query
            try:
                data = await agent.execute_query(gen_result['sql'], db)
                print(f"\n✅ Query executed successfully - {len(data)} rows returned")
                
                # Show sample data
                if data:
                    print(f"\n📄 Sample row:")
                    print(json.dumps(data[0], indent=2, default=str))
                
                # Generate visualization
                viz_config = agent.suggest_visualization(data, gen_result['visualization'])
                print(f"\n🎨 Visualization config:")
                print(json.dumps({k: v for k, v in viz_config.items() if k != 'data'}, indent=2))
                
                results['passed'] += 1
                
            except ValueError as e:
                print(f"❌ FAILED - Execution Error: {str(e)}")
                results['failed'] += 1
                results['errors'].append({
                    "test": i,
                    "question": test['question'],
                    "error": str(e),
                    "sql": gen_result['sql']
                })
                
        except Exception as e:
            print(f"❌ FAILED - Unexpected Error: {str(e)}")
            results['failed'] += 1
            results['errors'].append({
                "test": i,
                "question": test['question'],
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {results['passed']}/{len(test_cases)}")
    print(f"❌ Failed: {results['failed']}/{len(test_cases)}")
    
    if results['errors']:
        print(f"\n⚠️  ERRORS:")
        for err in results['errors']:
            print(f"  Test {err['test']}: {err['error']}")
    
    print("\n" + "="*80)
    
    db.close()


if __name__ == "__main__":
    print("\n🚀 Starting MCP Agent Tests...")
    print("⚠️  Make sure Ollama is running: ollama serve\n")
    
    try:
        asyncio.run(test_mcp_agent())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
