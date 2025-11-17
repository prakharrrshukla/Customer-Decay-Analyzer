#!/bin/bash
# Quick setup script for Customer Decay Analyzer
# Generates 100 customers with preprocessed analysis data

echo "======================================================================"
echo "🚀 Setting up Customer Decay Analyzer with 100 customers..."
echo "======================================================================"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Activating venv..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "❌ Error: Virtual environment not found"
        echo "   Please create one first: python -m venv venv"
        exit 1
    fi
fi

# Step 1: Generate 100 customers
echo "📊 Step 1/3: Generating 100 customers with realistic data..."
python scripts/generate_sample_data.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate sample data"
    exit 1
fi
echo "   ✓ Generated customers.csv, behavior_events.csv, churned_customers.csv"
echo ""

# Step 2: Generate preprocessed analysis (NO API CALLS!)
echo "🤖 Step 2/3: Generating preprocessed analysis data (no API calls)..."
python scripts/generate_preprocessed_analysis.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate preprocessed analysis"
    exit 1
fi
echo "   ✓ Generated preprocessed_analysis.json"
echo ""

# Step 3: Populate Qdrant vector database
echo "🔍 Step 3/3: Populating Qdrant vector database..."
if [ -f "scripts/populate_qdrant.py" ]; then
    python scripts/populate_qdrant.py
    if [ $? -eq 0 ]; then
        echo "   ✓ Qdrant populated successfully"
    else
        echo "   ⚠️  Qdrant population failed (optional - may need API keys)"
    fi
else
    echo "   ⚠️  populate_qdrant.py not found (skipping)"
fi
echo ""

# Display summary
echo "======================================================================"
echo "✅ Setup complete! 100 customers ready for demo"
echo "======================================================================"
echo ""
echo "📈 Risk breakdown:"
python -c "
import json
import sys

try:
    with open('data/preprocessed_analysis.json', 'r') as f:
        data = json.load(f)
    
    risk_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    for customer in data:
        risk_level = customer.get('risk_level', 'low')
        risk_counts[risk_level] += 1
    
    total = len(data)
    print(f'  Low:      {risk_counts[\"low\"]:2d} customers ({risk_counts[\"low\"]/total*100:.0f}%)')
    print(f'  Medium:   {risk_counts[\"medium\"]:2d} customers ({risk_counts[\"medium\"]/total*100:.0f}%)')
    print(f'  High:     {risk_counts[\"high\"]:2d} customers ({risk_counts[\"high\"]/total*100:.0f}%)')
    print(f'  Critical: {risk_counts[\"critical\"]:2d} customers ({risk_counts[\"critical\"]/total*100:.0f}%)')
    print()
    
    # Revenue at risk
    total_revenue = sum(c.get('estimated_revenue_at_risk', 0) for c in data)
    high_risk_revenue = sum(
        c.get('estimated_revenue_at_risk', 0)
        for c in data
        if c.get('risk_level') in ['high', 'critical']
    )
    
    print(f'💰 Revenue Analysis:')
    print(f'  Total at Risk:        ${total_revenue:,}')
    print(f'  High/Critical Risk:   ${high_risk_revenue:,}')
    
except Exception as e:
    print(f'  Error reading analysis: {e}')
    sys.exit(1)
"

echo ""
echo "======================================================================"
echo "🎯 Ready to start backend server:"
echo "   python app.py"
echo ""
echo "📌 Key features:"
echo "   • 100 customers with realistic behavior patterns"
echo "   • Preprocessed analysis (no AI API rate limits)"
echo "   • Instant loading for smooth demos"
echo "   • Proper risk distribution (40-40-20)"
echo "======================================================================"
