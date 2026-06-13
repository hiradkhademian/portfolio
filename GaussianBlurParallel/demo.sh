#!/bin/bash

# Quick Demo: Fast Gaussian Blur Performance Demo (5-10 minutes)
# This demo shows Sequential vs Fork/Join on a subset of representative images

echo ""
echo "=========================================="
echo "  GAUSSIAN BLUR QUICK DEMO"
echo "  Sequential vs Fork/Join Comparison"
echo "=========================================="
echo ""

# Compile if needed
echo "📦 Compiling source code..."
javac src/src/*.java 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Compilation failed"
    exit 1
fi
echo "✅ Compilation successful"
echo ""

# Create output directory
mkdir -p output

# Select demo images: one small, one medium, one large from each format
DEMO_IMAGES=(
    "OnePunchMan-800x600px.jpg.jpeg"      # Small JPEG (480K pixels) - fast
    "SoulEater-2560x1600px.jpg.jpeg"      # Medium JPEG (4.1M pixels) - moderate
    "dororo_14516x8318.jpg.jpeg"          # Large JPEG (120.7M pixels) - shows scaling
    "deathNote_4096x2304.png"             # Medium PNG (9.4M pixels)
)

echo "=========================================="
echo "DEMO CONFIGURATION"
echo "=========================================="
echo "Selected images: ${#DEMO_IMAGES[@]}"
echo ""

total_pixels=0
for img in "${DEMO_IMAGES[@]}"; do
    if [ -f "$img" ]; then
        size=$(ls -lh "$img" | awk '{print $5}')
        echo "  ✓ $img ($size)"
        # Rough pixel estimate for display
    else
        echo "  ✗ $img (NOT FOUND)"
    fi
done

echo ""
echo "=========================================="
echo "RUNNING DEMO"
echo "=========================================="
echo ""

# Run Main with demo images
echo "Processing images with default implementation..."
echo ""

java -cp . src.Main "${DEMO_IMAGES[@]}"

echo ""
echo "=========================================="
echo "DEMO COMPLETE"
echo "=========================================="
echo ""
echo "✅ Processed ${#DEMO_IMAGES[@]} images"
echo ""
echo "📂 Output images saved to: output/"
echo ""
echo "Check output/ directory for:"
echo "  • OnePunchMan_sequential.jpg"
echo "  • OnePunchMan_forkjoin.jpg"
echo "  • SoulEater_sequential.jpg"
echo "  • SoulEater_forkjoin.jpg"
echo "  • And so on..."
echo ""
