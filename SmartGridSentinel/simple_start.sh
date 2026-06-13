#!/bin/bash

# SmartGrid Sentinel - Simple Startup with Logging
# Starts Docker Compose and captures logs to file + Excel
# Usage: ./simple_start.sh

set -e

PROJECT_DIR="/Users/hiradkhademian/Desktop/smartgrid-sentinel"
LOG_FILE="$PROJECT_DIR/system_logs.txt"
EXCEL_FILE="$PROJECT_DIR/grid_sentinel_logs.xlsx"

# Use conda's Python with correct NumPy version
PYTHON_CMD="/opt/homebrew/Caskroom/miniconda/base/bin/python"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  SmartGrid Sentinel - Simple Startup                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Clean previous logs
echo "🧹 Clearing previous logs..."
> "$LOG_FILE"

# Step 2: Start Docker Compose
echo "🚀 Starting Docker Compose (bringing up 10 services)..."
cd "$PROJECT_DIR"
docker compose up -d > /dev/null 2>&1

# Step 3: Capture logs in background
echo "📝 Capturing logs to: $LOG_FILE"
docker compose logs --timestamps -f > "$LOG_FILE" 2>&1 &
LOG_PID=$!
echo "📌 Log capture PID: $LOG_PID"

# Step 4: Wait for services to initialize
echo "⏳ Waiting 10 seconds for services to initialize..."
sleep 10

# Step 5: Generate Excel
echo "📊 Generating Excel report..."
if $PYTHON_CMD "$PROJECT_DIR/parse_logs_to_excel.py" 2>/dev/null; then
    echo "✓ Excel report generated successfully"
else
    echo "⚠️  Excel generation failed (will try again later)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✓ System Started                                              ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║  📁 Raw Logs:  $LOG_FILE                     ║"
echo "║  📊 Excel:     $EXCEL_FILE                       ║"
echo "║                                                                ║"
echo "║  View organized logs in THIS terminal:                        ║"
echo "║    ./simple_monitor.sh data      # Data flow                  ║"
echo "║    ./simple_monitor.sh actions   # Commands                   ║"
echo "║    ./simple_monitor.sh errors    # Errors                     ║"
echo "║    ./simple_monitor.sh all       # Everything                 ║"
echo "║                                                                ║"
echo "║  Or open a new terminal and run:                              ║"
echo "║    docker compose logs -f --timestamps                        ║"
echo "║                                                                ║"
echo "║  Stop services:                                                ║"
echo "║    docker compose down                                        ║"
echo "║                                                                ║"
echo "║  Stop log capture:                                             ║"
echo "║    kill $LOG_PID                                              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Keep the main script running so services stay up
echo "✓ Press Ctrl+C to stop services"
wait
