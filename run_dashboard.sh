#!/bin/bash
# USA Sector Rotation Dashboard Launcher

cd "$(dirname "$0")"

echo "=================================================="
echo "USA Sector Rotation Dashboard"
echo "=================================================="

# Check if data exists
if [ ! -f "data/consolidated_ticker_analysis_*.json" ] 2>/dev/null; then
    echo "Generating initial data..."
    python generate_actionable_tickers.py
fi

# Start the dashboard
echo ""
echo "Starting dashboard on port 8001..."
echo "Access at: http://localhost:8001"
echo ""

cd dashboard/backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
