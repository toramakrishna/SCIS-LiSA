#!/bin/bash
# Test all suggested queries through the API

API_URL="http://localhost:8000/api/v1/mcp/query"

echo "Testing all suggested queries through the API"
echo "============================================="
echo ""

queries=(
    "Show top 10 faculty by publication count"
    "What are the publication trends over the last 5 years?"
    "List the most cited publications"
    "Show collaborations between faculty members"
    "Which venues have the most publications?"
    "Show faculty with h-index greater than 10"
)

for query in "${queries[@]}"; do
    echo "Testing: $query"
    echo "---"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"question\": \"$query\"}")
    
    # Check if we got an error
    error=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('error', ''))")
    row_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('row_count', 0))")
    viz_type=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('visualization', {}).get('type', 'unknown'))")
    
    if [ -n "$error" ]; then
        echo "❌ ERROR: $error"
    elif [ "$row_count" = "0" ]; then
        echo "❌ NO RESULTS (0 rows)"
    else
        echo "✅ SUCCESS: $row_count rows, visualization: $viz_type"
    fi
    
    echo ""
done

echo "All tests completed!"
