#!/usr/bin/env python3
"""
Comprehensive Single Graph Generator
Creates a single 3-panel visualization showing Sequential, Fork/Join, and Combined results
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Color scheme
COLOR_PNG = '#95E1D3'         # Light green
COLOR_JPEG = '#FFE66D'        # Yellow

def read_combined_results(filename):
    """Parse combined results CSV"""
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip summary sections
            if not row['Seq Avg (ms)'] or not row['FJ Avg (ms)']:
                continue
            
            img_file = row['Image File']
            img_name = img_file.split('-')[0]
            
            # Determine type
            img_type = 'PNG' if (img_file.endswith('.png')) else 'JPEG'
            
            data.append({
                'name': img_name,
                'seq': float(row['Seq Avg (ms)']),
                'fj': float(row['FJ Avg (ms)']),
                'speedup': float(row['Speedup (S)']),
                'efficiency': float(row['Efficiency (%)']),
                'type': img_type,
                'full_name': img_file
            })
    
    return data

def create_comprehensive_graph(data):
    """Create a single 3-panel comprehensive graph"""
    
    # Separate PNG and JPEG data, maintaining order
    images = [d['name'] for d in data]
    seq_times = [d['seq'] for d in data]
    fj_times = [d['fj'] for d in data]
    speedups = [d['speedup'] for d in data]
    types = [d['type'] for d in data]
    
    # Create figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    fig.suptitle('Gaussian Blur Benchmark - Comprehensive Performance Analysis (Sequential | Fork/Join | Combined)', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    x_pos = np.arange(len(images))
    bar_width = 0.35
    
    # ==================== SUBPLOT 1: Sequential Times ====================
    ax1 = axes[0]
    
    # Separate colors for PNG and JPEG
    colors_seq = [COLOR_PNG if t == 'PNG' else COLOR_JPEG for t in types]
    
    bars1 = ax1.bar(x_pos, seq_times, color=colors_seq, alpha=0.85, 
                    edgecolor='black', linewidth=1.2)
    
    ax1.set_xlabel('Image', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Sequential Blur Execution Times', fontsize=13, fontweight='bold', pad=10)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(images, rotation=45, ha='right', fontsize=9)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, v in enumerate(seq_times):
        ax1.text(i, v + max(seq_times)*0.02, f'{v:.0f}', 
                ha='center', va='bottom', fontsize=7, fontweight='bold')
    
    # Legend for first subplot
    png_patch = mpatches.Patch(color=COLOR_PNG, label='PNG', alpha=0.85)
    jpeg_patch = mpatches.Patch(color=COLOR_JPEG, label='JPEG', alpha=0.85)
    ax1.legend(handles=[png_patch, jpeg_patch], fontsize=10, loc='upper left')
    
    # ==================== SUBPLOT 2: Fork/Join Times ====================
    ax2 = axes[1]
    
    colors_fj = [COLOR_PNG if t == 'PNG' else COLOR_JPEG for t in types]
    
    bars2 = ax2.bar(x_pos, fj_times, color=colors_fj, alpha=0.85, 
                    edgecolor='black', linewidth=1.2)
    
    ax2.set_xlabel('Image', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('Fork/Join Blur Execution Times', fontsize=13, fontweight='bold', pad=10)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(images, rotation=45, ha='right', fontsize=9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, v in enumerate(fj_times):
        ax2.text(i, v + max(fj_times)*0.02, f'{v:.0f}', 
                ha='center', va='bottom', fontsize=7, fontweight='bold')
    
    # Legend for second subplot
    ax2.legend(handles=[png_patch, jpeg_patch], fontsize=10, loc='upper left')
    
    # ==================== SUBPLOT 3: Speedup Results ====================
    ax3 = axes[2]
    
    colors_speedup = [COLOR_PNG if t == 'PNG' else COLOR_JPEG for t in types]
    
    bars3 = ax3.bar(x_pos, speedups, color=colors_speedup, alpha=0.85, 
                    edgecolor='black', linewidth=1.2)
    
    # Add reference lines
    ax3.axhline(y=8, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Ideal (8 cores)')
    ax3.axhline(y=4, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='Good (4x)')
    
    ax3.set_xlabel('Image', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Speedup (×)', fontsize=12, fontweight='bold')
    ax3.set_title('Fork/Join Speedup Performance', fontsize=13, fontweight='bold', pad=10)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(images, rotation=45, ha='right', fontsize=9)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, v in enumerate(speedups):
        ax3.text(i, v + max(speedups)*0.02, f'{v:.2f}x', 
                ha='center', va='bottom', fontsize=7, fontweight='bold')
    
    # Legend for third subplot (with format types)
    lines = [mpatches.Patch(color=COLOR_PNG, label='PNG', alpha=0.85),
             mpatches.Patch(color=COLOR_JPEG, label='JPEG', alpha=0.85)]
    ax3.legend(handles=lines, fontsize=10, loc='upper left')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    plt.savefig('GaussianBlur_Comprehensive_Graph.png', dpi=300, bbox_inches='tight')
    print("✅ Generated: GaussianBlur_Comprehensive_Graph.png")
    plt.close()

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("  GENERATING COMPREHENSIVE 3-PANEL BENCHMARK GRAPH")
    print("="*70 + "\n")
    
    # Check if file exists
    if not Path('GaussianBlur_Combined_Results.csv').exists():
        print("❌ Error: GaussianBlur_Combined_Results.csv not found!")
        return
    
    # Parse data
    print("📖 Reading benchmark data...")
    data = read_combined_results('GaussianBlur_Combined_Results.csv')
    print(f"✅ Loaded {len(data)} image results")
    
    # Generate graph
    print("\n📊 Generating comprehensive 3-panel graph...\n")
    create_comprehensive_graph(data)
    
    print("="*70)
    print("✅ COMPREHENSIVE GRAPH GENERATION COMPLETE!")
    print("="*70)
    print("\n📊 Generated file:")
    print("  • GaussianBlur_Comprehensive_Graph.png")
    print("\n📈 This single graph contains:")
    print("  Panel 1: Sequential Blur execution times (PNG + JPEG)")
    print("  Panel 2: Fork/Join Blur execution times (PNG + JPEG)")
    print("  Panel 3: Fork/Join Speedup results (PNG + JPEG)")
    print("\n🎨 High-resolution PNG file (300 DPI)\n")

if __name__ == '__main__':
    main()
