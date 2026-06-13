#!/bin/bash

# SmartGrid Sentinel - Simple Docker Compose Monitor
# Shows organized logs directly in terminal using Docker Compose filtering
# Usage: ./simple_monitor.sh [option]
# Options: all (default), data, actions, errors

OPTION="${1:-all}"
PROJECT_DIR="/Users/hiradkhademian/Desktop/smartgrid-sentinel"

cd "$PROJECT_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  SmartGrid Sentinel - Docker Compose Monitor                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

case "$OPTION" in
    all)
        echo "📊 Showing ALL services (all 10 containers)"
        echo "Use Ctrl+C to stop monitoring"
        echo ""
        docker compose logs -f --timestamps
        ;;
    
    data)
        echo "📊 Data Flow: Ingestion → Real-Time Analysis → Trends"
        echo "Use Ctrl+C to stop monitoring"
        echo ""
        docker compose logs -f --timestamps ingestion-service real_time_analysis trend_regional_analysis
        ;;
    
    actions)
        echo "⚙️  Actions: Commands & Acknowledgments"
        echo "Use Ctrl+C to stop monitoring"
        echo ""
        docker compose logs -f --timestamps action_gateway mock_engine
        ;;
    
    errors)
        echo "❌ Errors: DLQ Monitoring & Failures"
        echo "Use Ctrl+C to stop monitoring"
        echo ""
        docker compose logs -f --timestamps dlq_monitor | grep -v "Polling"
        ;;
    
    help)
        echo "Usage: ./simple_monitor.sh [option]"
        echo ""
        echo "Options:"
        echo "  all      - Show all services (default)"
        echo "  data     - Show data flow (Ingestion → Analysis → Regional)"
        echo "  actions  - Show actions (Commands & Acknowledgments)"
        echo "  errors   - Show errors (DLQ Monitoring)"
        echo "  help     - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./simple_monitor.sh               # All services"
        echo "  ./simple_monitor.sh data          # Data flow only"
        echo "  ./simple_monitor.sh actions       # Actions only"
        echo "  ./simple_monitor.sh errors        # Errors only"
        ;;
    
    *)
        echo "❌ Unknown option: $OPTION"
        echo ""
        echo "Use: ./simple_monitor.sh help"
        exit 1
        ;;
esac
