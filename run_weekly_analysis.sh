#!/bin/bash
# USA Sector Rotation - Weekly Analysis Pipeline
# Run this script weekly to update all analysis and reports

set -e

cd "$(dirname "$0")"

echo "=================================================="
echo "USA Sector Rotation - Weekly Analysis"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="

# Step 1: Check for latest Sector-Leaders-Usa data
echo ""
echo "[1/4] Checking Sector-Leaders-Usa data..."
LATEST_RANKING=$(ls -t /mnt/nas/WWAI/Sector-Rotation/Sector-Leaders-Usa/results/combined_score_ranking_*.csv 2>/dev/null | head -1)
if [ -z "$LATEST_RANKING" ]; then
    echo "ERROR: No Sector-Leaders-Usa rankings found"
    echo "Run Sector-Leaders-Usa analysis first"
    exit 1
fi
echo "Latest ranking: $LATEST_RANKING"

# Step 2: Generate actionable tickers
echo ""
echo "[2/4] Generating actionable tickers..."
python generate_actionable_tickers.py

# Step 3: Generate investment reports
echo ""
echo "[3/4] Generating investment reports..."
python generate_investment_report.py

# Step 4: Validate data
echo ""
echo "[4/4] Validating master data..."
python scripts/validate_master_csv.py

# Summary
echo ""
echo "=================================================="
echo "Weekly Analysis Complete"
echo "=================================================="
echo ""
echo "Output Files:"
ls -la data/*.csv data/*.json 2>/dev/null | tail -6
echo ""
ls -la analysis/*.md 2>/dev/null | tail -3
echo ""
ls -la reports/*.md 2>/dev/null | tail -3
echo ""
echo "Dashboard: ./run_dashboard.sh (port 8001)"
echo "=================================================="
