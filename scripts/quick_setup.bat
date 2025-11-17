@echo off
REM Quick setup script for Customer Decay Analyzer (Windows)
REM Generates 100 customers with preprocessed analysis data

echo ======================================================================
echo 🚀 Setting up Customer Decay Analyzer with 100 customers...
echo ======================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Error: Virtual environment not found
    echo    Please create one first: python -m venv venv
    exit /b 1
)

REM Activate virtual environment
echo ⚙️  Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Step 1: Generate 100 customers
echo 📊 Step 1/3: Generating 100 customers with realistic data...
python scripts\generate_sample_data.py
if errorlevel 1 (
    echo ❌ Failed to generate sample data
    exit /b 1
)
echo    ✓ Generated customers.csv, behavior_events.csv, churned_customers.csv
echo.

REM Step 2: Generate preprocessed analysis
echo 🤖 Step 2/3: Generating preprocessed analysis data (no API calls)...
python scripts\generate_preprocessed_analysis.py
if errorlevel 1 (
    echo ❌ Failed to generate preprocessed analysis
    exit /b 1
)
echo    ✓ Generated preprocessed_analysis.json
echo.

REM Step 3: Populate Qdrant (optional)
echo 🔍 Step 3/3: Populating Qdrant vector database...
if exist "scripts\populate_qdrant.py" (
    python scripts\populate_qdrant.py
    if errorlevel 1 (
        echo    ⚠️  Qdrant population failed (optional - may need API keys^)
    ) else (
        echo    ✓ Qdrant populated successfully
    )
) else (
    echo    ⚠️  populate_qdrant.py not found (skipping^)
)
echo.

REM Display summary
echo ======================================================================
echo ✅ Setup complete! 100 customers ready for demo
echo ======================================================================
echo.

echo 📈 Risk breakdown:
python -c "import json; data = json.load(open('data/preprocessed_analysis.json')); risk_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}; [risk_counts.update({c.get('risk_level', 'low'): risk_counts[c.get('risk_level', 'low')] + 1}) for c in data]; total = len(data); print(f\"  Low:      {risk_counts['low']:2d} customers ({risk_counts['low']/total*100:.0f}%%)\"); print(f\"  Medium:   {risk_counts['medium']:2d} customers ({risk_counts['medium']/total*100:.0f}%%)\"); print(f\"  High:     {risk_counts['high']:2d} customers ({risk_counts['high']/total*100:.0f}%%)\"); print(f\"  Critical: {risk_counts['critical']:2d} customers ({risk_counts['critical']/total*100:.0f}%%)\"); print(); total_revenue = sum(c.get('estimated_revenue_at_risk', 0) for c in data); high_risk_revenue = sum(c.get('estimated_revenue_at_risk', 0) for c in data if c.get('risk_level') in ['high', 'critical']); print(f\"💰 Revenue Analysis:\"); print(f\"  Total at Risk:        ${total_revenue:,}\"); print(f\"  High/Critical Risk:   ${high_risk_revenue:,}\")"

echo.
echo ======================================================================
echo 🎯 Ready to start backend server:
echo    python app.py
echo.
echo 📌 Key features:
echo    • 100 customers with realistic behavior patterns
echo    • Preprocessed analysis (no AI API rate limits^)
echo    • Instant loading for smooth demos
echo    • Proper risk distribution (40-40-20^)
echo ======================================================================
echo.

pause
