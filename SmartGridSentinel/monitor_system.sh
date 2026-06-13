#!/bin/bash

# SmartGrid Sentinel - Multi-Terminal System Monitor
# Opens 4 organized terminals for monitoring the entire system
# Usage: ./monitor_system.sh

set -e

PROJECT_DIR="/Users/hiradkhademian/Desktop/smartgrid-sentinel"

# Helper function to open terminal with command
open_terminal() {
    local command="$1"
    
    osascript << EOF
tell application "Terminal"
    activate
    tell application "System Events"
        keystroke "t" using command down
    end tell
    delay 0.3
    tell front window
        do script "cd '$PROJECT_DIR' && $command" in current tab
    end tell
end tell
EOF
    sleep 1
}

# Open Terminal 1: System Orchestration with Logging
echo "Opening Terminal 1: System Orchestration..."
osascript << 'EOF'
tell application "Terminal"
    activate
    do script "cd '/Users/hiradkhademian/Desktop/smartgrid-sentinel' && clear && echo '▶ SmartGrid Sentinel - System Orchestration' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '' && ./run_with_logging.sh"
end tell
EOF
sleep 2

# Open Terminal 2: Data Flow Monitoring
echo "Opening Terminal 2: Data Flow..."
osascript << 'EOF'
tell application "Terminal"
    do script "cd '/Users/hiradkhademian/Desktop/smartgrid-sentinel' && clear && echo '▶ SmartGrid Sentinel - Data Flow (Ingestion → Analysis → Regional)' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '' && docker compose logs -f --timestamps ingestion real_time_analysis trend_regional_analysis"
end tell
EOF
sleep 1

# Open Terminal 3: Actions Monitoring
echo "Opening Terminal 3: Actions..."
osascript << 'EOF'
tell application "Terminal"
    do script "cd '/Users/hiradkhademian/Desktop/smartgrid-sentinel' && clear && echo '▶ SmartGrid Sentinel - Actions (Commands & Acknowledgments)' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '' && docker compose logs -f --timestamps action_gateway mock_engine"
end tell
EOF
sleep 1

# Open Terminal 4: Error Handling
echo "Opening Terminal 4: Errors..."
osascript << 'EOF'
tell application "Terminal"
    do script "cd '/Users/hiradkhademian/Desktop/smartgrid-sentinel' && clear && echo '▶ SmartGrid Sentinel - Error Handling (DLQ Monitoring)' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '' && docker compose logs -f --timestamps dlq_monitor"
end tell
EOF
sleep 1

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  SmartGrid Sentinel - Multi-Terminal Monitor Started           ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║  Terminal 1: System Orchestration                             ║"
echo "║              └─ Run: ./run_with_logging.sh                    ║"
echo "║              └─ Status: Starting all 11 services + logging    ║"
echo "║                                                                ║"
echo "║  Terminal 2: Data Flow                                        ║"
echo "║              └─ Ingestion → Real-Time Analysis → Trends       ║"
echo "║              └─ Watch: Telemetry flowing through system       ║"
echo "║                                                                ║"
echo "║  Terminal 3: Actions                                          ║"
echo "║              └─ Action Gateway → Mock Engine                  ║"
echo "║              └─ Watch: Commands dispatched & acknowledged     ║"
echo "║                                                                ║"
echo "║  Terminal 4: Error Handling                                   ║"
echo "║              └─ DLQ Monitor                                   ║"
echo "║              └─ Watch: Failed messages & DLQ events           ║"
echo "║                                                                ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  Expected Duration: ~15 minutes for full system run            ║"
echo "║  Output Files:                                                 ║"
echo "║    - system_logs.txt (raw logs)                                ║"
echo "║    - grid_sentinel_logs.xlsx (professional Excel report)       ║"
echo "║                                                                ║"
echo "║  Ctrl+C in Terminal 1 to stop the system                      ║"
echo "║  Ctrl+C in other terminals to stop monitoring                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
