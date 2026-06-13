#!/usr/bin/env python3
"""
Gaussian Blur Benchmark Visualization Generator
Generates comprehensive graphs comparing Sequential, Fork/Join, and Combined results
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from pathlib import Path

# Color scheme
COLOR_SEQUENTIAL = '#FF6B6B'  # Red
COLOR_FORKJOIN = '#4ECDC4'    # Teal
COLOR_PNG = '#95E1D3'         # Light green
COLOR_JPEG = '#FFE66D'        # Yellow

def read_csv_data(filename):
    """Read benchmark CSV file and return parsed data"""
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def parse_combined_results(filename):
    """Parse combined results CSV with all metrics"""
    images = []
    sequential_times = []
    forkjoin_times = []
    speedups = []
    efficiencies = []
    pixels = []
    image_types = []
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip summary sections (rows with None/empty values)
            if not row['Seq Avg (ms)'] or not row['FJ Avg (ms)']:
                continue
            
            img_file = row['Image File']
            images.append(img_file.split('-')[0])  # Extract image name without size
            sequential_times.append(float(row['Seq Avg (ms)']))
            forkjoin_times.append(float(row['FJ Avg (ms)']))
            speedups.append(float(row['Speedup (S)']))
            efficiencies.append(float(row['Efficiency (%)']))
            
            # Calculate pixels from width and height
            width = float(row['Width'])
            height = float(row['Height'])
            total_pixels = (width * height) / 1_000_000  # Convert to megapixels
            pixels.append(total_pixels)
            
            # Determine image type from extension
            if img_file.endswith('.jpg') or img_file.endswith('.jpeg'):
                image_types.append('JPEG')
            else:
                image_types.append('PNG')
    
    return {
        'images': images,
        'sequential': sequential_times,
        'forkjoin': forkjoin_times,
        'speedups': speedups,
        'efficiencies': efficiencies,
        'pixels': pixels,
        'types': image_types
    }

def create_execution_time_comparison(data):
    """Create side-by-side execution time comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    images = data['images']
    x_pos = np.arange(len(images))
    width = 0.35
    
    # Sequential times
    ax1.bar(x_pos, data['sequential'], color=COLOR_SEQUENTIAL, alpha=0.8, edgecolor='black', linewidth=1.2)
    ax1.set_xlabel('Image', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Sequential Blur Execution Times', fontsize=14, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(images, rotation=45, ha='right', fontsize=9)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, v in enumerate(data['sequential']):
        ax1.text(i, v + max(data['sequential'])*0.02, f'{v:.0f}', 
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Fork/Join times
    ax2.bar(x_pos, data['forkjoin'], color=COLOR_FORKJOIN, alpha=0.8, edgecolor='black', linewidth=1.2)
    ax2.set_xlabel('Image', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('Fork/Join Blur Execution Times', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(images, rotation=45, ha='right', fontsize=9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, v in enumerate(data['forkjoin']):
        ax2.text(i, v + max(data['forkjoin'])*0.02, f'{v:.0f}', 
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graph_execution_times.png', dpi=300, bbox_inches='tight')
    print("✅ Generated: graph_execution_times.png")
    plt.close()

def create_combined_execution_comparison(data):
    """Create combined sequential vs fork/join bars"""
    fig, ax = plt.subplots(figsize=(16, 7))
    
    images = data['images']
    x_pos = np.arange(len(images))
    width = 0.35
    
    bars1 = ax.bar(x_pos - width/2, data['sequential'], width, 
                   label='Sequential', color=COLOR_SEQUENTIAL, alpha=0.85, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x_pos + width/2, data['forkjoin'], width, 
                   label='Fork/Join', color=COLOR_FORKJOIN, alpha=0.85, edgecolor='black', linewidth=1.2)
    
    ax.set_xlabel('Image', fontsize=13, fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontsize=13, fontweight='bold')
    ax.set_title('Sequential vs Fork/Join Execution Time Comparison', fontsize=15, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(images, rotation=45, ha='right', fontsize=10)
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('graph_combined_execution.png', dpi=300, bbox_inches='tight')
    print("✅ Generated: graph_combined_execution.png")
    plt.close()

def create_speedup_chart(data):
    """Create speedup visualization"""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    images = data['images']
    x_pos = np.arange(len(images))
    speedups = data['speedups']
    colors = [COLOR_PNG if t == 'PNG' else COLOR_JPEG for t in data['types']]
    
    bars = ax.bar(x_pos, speedups, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)
    
    # Add horizontal line for ideal speedup (8 cores)
    ax.axhline(y=8, color='red', linestyle='--', linewidth=2, label='Ideal (8 cores)', alpha=0.7)
    ax.axhline(y=4, color='orange', linestyle='--', linewidth=1.5, label='Good scaling', alpha=0.5)
    
    ax.set_xlabel('Image', fontsize=13, fontweight='bold')
    ax.set_ylabel('Speedup (×)', fontsize=13, fontweight='bold')
    ax.set_title('Fork/Join Speedup Comparison (Sequential vs Fork/Join)', fontsize=15, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(images, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(0, max(speedups) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, v in enumerate(speedups):
        ax.text(i, v + max(speedups)*0.02, f'{v:.2f}x', 
               ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Create custom legend
    png_patch = mpatches.Patch(color=COLOR_PNG, label='PNG Images', alpha=0.85)
    jpeg_patch = mpatches.Patch(color=COLOR_JPEG, label='JPEG Images', alpha=0.85)
    ax.legend(handles=[png_patch, jpeg_patch], fontsize=11, loc='upper right')
    
    plt.tight_layout()
    plt.savefig('graph_speedup.png', dpi=300, bbox_inches='tight')
    print("✅ Generated: graph_speedup.png")
    plt.close()

def create_efficiency_chart(data):
    """Create efficiency visualization"""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    images = data['images']
    x_pos = np.arange(len(images))
    efficiencies = data['efficiencies']
    colors = [COLOR_PNG if t == 'PNG' else COLOR_JPEG for t in data['types']]
    
    bars = ax.bar(x_pos, efficiencies, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)
    
    # Add horizontal lines for efficiency thresholds
    ax.axhline(y=50, color='green', linestyle='--', linewidth=2, label='Excellent (50%)', alpha=0.7)
    ax.axhline(y=12.5, color='orange', linestyle='--', linewidth=1.5, label='Poor (12.5%)', alpha=0.5)
    
    ax.set_xlabel('Image', fontsize=13, fontweight='bold')
    ax.set_ylabel('Efficiency (%)', fontsize=13, fontweight='bold')
    ax.set_title('Fork/Join Parallel Efficiency (Speedup / Available Cores)', fontsize=15, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(images, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(0, max(efficiencies) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, v in enumerate(efficiencies):
        ax.text(i, v + max(efficiencies)*0.02, f'{v:.1f}%', 
               ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Create custom legend
    png_patch = mpatches.Patch(color=COLOR_PNG, label='PNG Images', alpha=0.85)
    jpeg_patch = mpatches.Patch(color=COLOR_JPEG, label='JPEG Images', alpha=0.85)
    ax.legend(handles=[png_patch, jpeg_patch], fontsize=11, loc='upper right')
    
    plt.tight_layout()
    plt.savefig('graph_efficiency.png', dpi=300, bbox_inches='tight')
    print("✅ Generated: graph_efficiency.png")
    plt.close()

def create_pixels_vs_performance(data):
    """Create scatter plot: pixels vs speedup and efficiency"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Separate PNG and JPEG data
    png_pixels = [p for p, t in zip(data['pixels'], data['types']) if t == 'PNG']
    png_speedups = [s for s, t in zip(data['speedups'], data['types']) if t == 'PNG']
    jpeg_pixels = [p for p, t in zip(data['pixels'], data['types']) if t == 'JPEG']
    jpeg_speedups = [s for s, t in zip(data['speedups'], data['types']) if t == 'JPEG']
    
    # Speedup vs Pixels
    ax1.scatter(png_pixels, png_speedups, s=150, color=COLOR_PNG, alpha=0.7, 
               edgecolor='black', linewidth=1.5, label='PNG', marker='o')
    ax1.scatter(jpeg_pixels, jpeg_speedups, s=150, color=COLOR_JPEG, alpha=0.7, 
               edgecolor='black', linewidth=1.5, label='JPEG', marker='s')
    
    ax1.set_xlabel('Image Size (Megapixels)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Speedup (×)', fontsize=12, fontweight='bold')
    ax1.set_title('Image Size vs Speedup Performance', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Add trend line
    all_pixels = data['pixels']
    all_speedups = data['speedups']
    z = np.polyfit(all_pixels, all_speedups, 2)
    p = np.poly1d(z)
    x_trend = np.linspace(min(all_pixels), max(all_pixels), 100)
    ax1.plot(x_trend, p(x_trend), "r--", alpha=0.5, linewidth=2, label='Trend')
    
    # Efficiency vs Pixels
    png_eff = [e for e, t in zip(data['efficiencies'], data['types']) if t == 'PNG']
    jpeg_eff = [e for e, t in zip(data['efficiencies'], data['types']) if t == 'JPEG']
    
    ax2.scatter(png_pixels, png_eff, s=150, color=COLOR_PNG, alpha=0.7, 
               edgecolor='black', linewidth=1.5, label='PNG', marker='o')
    ax2.scatter(jpeg_pixels, jpeg_eff, s=150, color=COLOR_JPEG, alpha=0.7, 
               edgecolor='black', linewidth=1.5, label='JPEG', marker='s')
    
    ax2.set_xlabel('Image Size (Megapixels)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Efficiency (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Image Size vs Parallel Efficiency', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('graph_pixels_vs_performance.png', dpi=300, bbox_inches='tight')
    print("✅ Generated: graph_pixels_vs_performance.png")
    plt.close()

def create_format_comparison(data):
    """Create PNG vs JPEG comparison"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Separate data by format
    png_indices = [i for i, t in enumerate(data['types']) if t == 'PNG']
    jpeg_indices = [i for i, t in enumerate(data['types']) if t == 'JPEG']
    
    png_speedups = [data['speedups'][i] for i in png_indices]
    jpeg_speedups = [data['speedups'][i] for i in jpeg_indices]
    png_eff = [data['efficiencies'][i] for i in png_indices]
    jpeg_eff = [data['efficiencies'][i] for i in jpeg_indices]
    
    # Speedup comparison
    formats = ['PNG', 'JPEG']
    avg_speedups = [np.mean(png_speedups), np.mean(jpeg_speedups)]
    bars = ax1.bar(formats, avg_speedups, color=[COLOR_PNG, COLOR_JPEG], alpha=0.85, 
                   edgecolor='black', linewidth=2, width=0.5)
    ax1.set_ylabel('Average Speedup (×)', fontsize=12, fontweight='bold')
    ax1.set_title('Average Speedup Comparison', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, 4)
    for i, v in enumerate(avg_speedups):
        ax1.text(i, v + 0.1, f'{v:.2f}x', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Efficiency comparison
    avg_eff = [np.mean(png_eff), np.mean(jpeg_eff)]
    bars = ax2.bar(formats, avg_eff, color=[COLOR_PNG, COLOR_JPEG], alpha=0.85, 
                   edgecolor='black', linewidth=2, width=0.5)
    ax2.set_ylabel('Average Efficiency (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Average Efficiency Comparison', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 50)
    for i, v in enumerate(avg_eff):
        ax2.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Speedup distribution
    positions = [1, 2]
    ax3.boxplot([png_speedups, jpeg_speedups], positions=positions, widths=0.5,
               patch_artist=True,
               boxprops=dict(facecolor=COLOR_PNG, alpha=0.7),
               medianprops=dict(color='red', linewidth=2))
    ax3.scatter([1]*len(png_speedups), png_speedups, color=COLOR_PNG, s=80, alpha=0.6, zorder=3)
    ax3.scatter([2]*len(jpeg_speedups), jpeg_speedups, color=COLOR_JPEG, s=80, alpha=0.6, zorder=3)
    ax3.set_xticklabels(formats)
    ax3.set_ylabel('Speedup (×)', fontsize=12, fontweight='bold')
    ax3.set_title('Speedup Distribution', fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # Efficiency distribution
    ax4.boxplot([png_eff, jpeg_eff], positions=positions, widths=0.5,
               patch_artist=True,
               boxprops=dict(facecolor=COLOR_PNG, alpha=0.7),
               medianprops=dict(color='red', linewidth=2))
    ax4.scatter([1]*len(png_eff), png_eff, color=COLOR_PNG, s=80, alpha=0.6, zorder=3)
    ax4.scatter([2]*len(jpeg_eff), jpeg_eff, color=COLOR_JPEG, s=80, alpha=0.6, zorder=3)
    ax4.set_xticklabels(formats)
    ax4.set_ylabel('Efficiency (%)', fontsize=12, fontweight='bold')
    ax4.set_title('Efficiency Distribution', fontsize=13, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graph_format_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Generated: graph_format_comparison.png")
    plt.close()

def create_summary_dashboard(data):
    """Create a comprehensive summary dashboard"""
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    images = data['images']
    x_pos = np.arange(len(images))
    
    # 1. Execution times comparison (top left)
    ax1 = fig.add_subplot(gs[0, 0:2])
    width = 0.35
    ax1.bar(x_pos - width/2, data['sequential'], width, label='Sequential', 
           color=COLOR_SEQUENTIAL, alpha=0.8, edgecolor='black')
    ax1.bar(x_pos + width/2, data['forkjoin'], width, label='Fork/Join', 
           color=COLOR_FORKJOIN, alpha=0.8, edgecolor='black')
    ax1.set_ylabel('Time (ms)', fontsize=11, fontweight='bold')
    ax1.set_title('Execution Time Comparison', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(images, rotation=45, ha='right', fontsize=8)
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Key metrics (top right)
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.axis('off')
    
    avg_speedup = np.mean(data['speedups'])
    avg_eff = np.mean(data['efficiencies'])
    best_speedup = max(data['speedups'])
    worst_speedup = min(data['speedups'])
    
    metrics_text = f"""
    📊 OVERALL METRICS
    ─────────────────
    Avg Speedup:  {avg_speedup:.2f}x
    Avg Efficiency: {avg_eff:.1f}%
    
    Best Speedup: {best_speedup:.2f}x
    Worst Speedup: {worst_speedup:.2f}x
    
    Total Images: {len(images)}
    PNG Images: {sum(1 for t in data['types'] if t == 'PNG')}
    JPEG Images: {sum(1 for t in data['types'] if t == 'JPEG')}
    """
    ax2.text(0.1, 0.5, metrics_text, fontsize=11, family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            verticalalignment='center')
    
    # 3. Speedup chart (middle left)
    ax3 = fig.add_subplot(gs[1, 0:2])
    colors = [COLOR_PNG if t == 'PNG' else COLOR_JPEG for t in data['types']]
    ax3.bar(x_pos, data['speedups'], color=colors, alpha=0.8, edgecolor='black')
    ax3.axhline(y=8, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Ideal (8 cores)')
    ax3.set_ylabel('Speedup (×)', fontsize=11, fontweight='bold')
    ax3.set_title('Speedup Performance', fontsize=12, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(images, rotation=45, ha='right', fontsize=8)
    ax3.grid(axis='y', alpha=0.3)
    ax3.legend(fontsize=9)
    
    # 4. Format comparison (middle right)
    ax4 = fig.add_subplot(gs[1, 2])
    png_speedups = [s for s, t in zip(data['speedups'], data['types']) if t == 'PNG']
    jpeg_speedups = [s for s, t in zip(data['speedups'], data['types']) if t == 'JPEG']
    
    box_data = [png_speedups, jpeg_speedups]
    bp = ax4.boxplot(box_data, labels=['PNG', 'JPEG'], patch_artist=True)
    for patch, color in zip(bp['boxes'], [COLOR_PNG, COLOR_JPEG]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax4.set_ylabel('Speedup (×)', fontsize=11, fontweight='bold')
    ax4.set_title('Format Comparison', fontsize=12, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    # 5. Efficiency chart (bottom left)
    ax5 = fig.add_subplot(gs[2, 0:2])
    ax5.bar(x_pos, data['efficiencies'], color=colors, alpha=0.8, edgecolor='black')
    ax5.set_ylabel('Efficiency (%)', fontsize=11, fontweight='bold')
    ax5.set_xlabel('Image', fontsize=11, fontweight='bold')
    ax5.set_title('Parallel Efficiency', fontsize=12, fontweight='bold')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(images, rotation=45, ha='right', fontsize=8)
    ax5.grid(axis='y', alpha=0.3)
    
    # 6. Pixels vs Speedup (bottom right)
    ax6 = fig.add_subplot(gs[2, 2])
    for i, (px, sp, img_type) in enumerate(zip(data['pixels'], data['speedups'], data['types'])):
        color = COLOR_PNG if img_type == 'PNG' else COLOR_JPEG
        ax6.scatter(px, sp, s=120, color=color, alpha=0.7, edgecolor='black', linewidth=1)
    
    ax6.set_xlabel('Pixels (M)', fontsize=10, fontweight='bold')
    ax6.set_ylabel('Speedup (×)', fontsize=10, fontweight='bold')
    ax6.set_title('Size vs Speedup', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    plt.suptitle('Gaussian Blur Benchmark - Comprehensive Dashboard', 
                fontsize=16, fontweight='bold', y=0.995)
    
    plt.savefig('graph_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ Generated: graph_dashboard.png")
    plt.close()

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("  GENERATING COMPREHENSIVE BENCHMARK GRAPHS")
    print("="*60 + "\n")
    
    # Check if combined results file exists
    if not Path('GaussianBlur_Combined_Results.csv').exists():
        print("❌ Error: GaussianBlur_Combined_Results.csv not found!")
        return
    
    # Parse data
    print("📖 Reading benchmark data...")
    data = parse_combined_results('GaussianBlur_Combined_Results.csv')
    
    # Generate graphs
    print("\n📊 Generating graphs...\n")
    
    create_execution_time_comparison(data)
    create_combined_execution_comparison(data)
    create_speedup_chart(data)
    create_efficiency_chart(data)
    create_pixels_vs_performance(data)
    create_format_comparison(data)
    create_summary_dashboard(data)
    
    print("\n" + "="*60)
    print("✅ GRAPH GENERATION COMPLETE!")
    print("="*60)
    print("\n📊 Generated graphs:")
    print("  • graph_execution_times.png - Sequential & Fork/Join times")
    print("  • graph_combined_execution.png - Side-by-side comparison")
    print("  • graph_speedup.png - Speedup performance chart")
    print("  • graph_efficiency.png - Parallel efficiency analysis")
    print("  • graph_pixels_vs_performance.png - Size correlation")
    print("  • graph_format_comparison.png - PNG vs JPEG analysis")
    print("  • graph_dashboard.png - Comprehensive summary dashboard")
    print("\n🎨 All graphs saved as high-resolution PNG files (300 DPI)\n")

if __name__ == '__main__':
    main()
