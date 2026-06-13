#!/bin/bash

# Test images
IMAGES=("test_1080p.jpg" "test_4k_converted.jpg" "test_8k_converted.jpg")

# Output file for raw data
OUTPUT_CSV="benchmark_data.csv"

# Initialize CSV with headers
echo "Image,Resolution,Mode,Time_ms,Cores,Speedup,Efficiency" > "$OUTPUT_CSV"

# Store sequential times for speedup calculation
declare -A SEQ_TIMES

for img in "${IMAGES[@]}"; do
  echo "Benchmarking $img..."
  
  # Run and capture full output
  OUTPUT=$(java -cp src src.Main "$img" 2>&1)
  
  # Extract resolution
  RESOLUTION=$(echo "$OUTPUT" | grep "Resolution:" | awk '{print $NF}')
  
  # Extract timing data
  SEQ_TIME=$(echo "$OUTPUT" | grep "Sequential Processing Time" | grep -oE '[0-9]+' | head -1)
  FJ_TIME=$(echo "$OUTPUT" | grep "Fork/Join Parallel" | grep -oE '[0-9]+' | head -1)
  THREAD_TIME=$(echo "$OUTPUT" | grep "Native Threading" | grep -oE '[0-9]+' | head -1)
  
  # Extract core count
  CORES=$(echo "$OUTPUT" | grep "Hardware Concurrency" | grep -oE '[0-9]+' | head -1)
  
  # Store sequential time for speedup calculation
  SEQ_TIMES[$img]=$SEQ_TIME
  
  # Write to CSV
  if [ ! -z "$SEQ_TIME" ]; then
    echo "$img,$RESOLUTION,Sequential,$SEQ_TIME,$CORES,1.00,0.13" >> "$OUTPUT_CSV"
  fi
  
  if [ ! -z "$FJ_TIME" ]; then
    SPEEDUP=$(echo "scale=2; $SEQ_TIME / $FJ_TIME" | bc)
    EFFICIENCY=$(echo "scale=2; $SPEEDUP / $CORES" | bc)
    echo "$img,$RESOLUTION,Fork/Join,$FJ_TIME,$CORES,$SPEEDUP,$EFFICIENCY" >> "$OUTPUT_CSV"
  fi
  
  if [ ! -z "$THREAD_TIME" ]; then
    SPEEDUP=$(echo "scale=2; $SEQ_TIME / $THREAD_TIME" | bc)
    EFFICIENCY=$(echo "scale=2; $SPEEDUP / $CORES" | bc)
    echo "$img,$RESOLUTION,Native Threads,$THREAD_TIME,$CORES,$SPEEDUP,$EFFICIENCY" >> "$OUTPUT_CSV"
  fi
  
  echo ""
done

echo "Benchmark complete! Data saved to $OUTPUT_CSV"
cat "$OUTPUT_CSV"
