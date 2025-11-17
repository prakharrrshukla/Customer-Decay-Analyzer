#!/bin/bash
set -e

echo "Starting Customer Decay Analyzer..."

# Generate sample data if not exists
if [ ! -f "data/customers.csv" ]; then
    echo "Generating sample data..."
    python3 scripts/generate_sample_data.py
fi

# Generate preprocessed analysis if not exists
if [ ! -f "data/preprocessed_analysis.json" ]; then
    echo "Generating preprocessed analysis..."
    python3 scripts/generate_preprocessed_analysis.py
fi

# Start the application
echo "Starting Flask application..."
python3 app.py
