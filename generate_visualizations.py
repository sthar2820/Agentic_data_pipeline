#!/usr/bin/env python3
"""
Generate visualizations for cleaned data
Usage: python3 generate_visualizations.py <cleaned_csv_file>
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

def create_visualizations(csv_file: str):
    """Generate comprehensive visualizations"""
    
    if not Path(csv_file).exists():
        print(f"ERROR: File not found: {csv_file}")
        sys.exit(1)
    
    # Load cleaned data
    print(f"Loading: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")
    
    # Create output directory
    viz_dir = Path("data/visualizations")
    viz_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(csv_file).stem
    
    print("\nGenerating visualizations...")
    
    # 1. Missing values heatmap
    print("  - Missing values heatmap")
    fig, ax = plt.subplots(figsize=(10, 4))
    missing_data = df.isnull().astype(int) * 100
    sns.heatmap(missing_data, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                cbar_kws={'label': 'Missing %'}, ax=ax)
    plt.title(f'Missing Values Heatmap - {filename}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    output = f"{viz_dir}/{filename}_missing_values_{timestamp}.png"
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {output}")
    
    # 2. Data type distribution
    print("  - Data type distribution")
    fig, ax = plt.subplots(figsize=(8, 5))
    dtype_counts = df.dtypes.value_counts()
    dtype_counts.plot(kind='bar', ax=ax, color='steelblue')
    plt.title(f'Data Type Distribution - {filename}', fontsize=14, fontweight='bold')
    plt.xlabel('Data Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    output = f"{viz_dir}/{filename}_dtypes_{timestamp}.png"
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {output}")
    
    # 3. Column statistics summary
    print("  - Column statistics")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    stats_text = "Column Statistics Summary\n" + "="*50 + "\n\n"
    for col in df.columns:
        stats_text += f"{col}:\n"
        stats_text += f"  Type: {df[col].dtype}\n"
        stats_text += f"  Non-null: {df[col].notna().sum():,}\n"
        stats_text += f"  Unique: {df[col].nunique()}\n"
        if df[col].dtype in ['int64', 'float64']:
            stats_text += f"  Mean: {df[col].mean():.2f}\n"
            stats_text += f"  Std: {df[col].std():.2f}\n"
        stats_text += "\n"
    
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
            fontfamily='monospace', fontsize=9, verticalalignment='top')
    ax.axis('off')
    plt.tight_layout()
    output = f"{viz_dir}/{filename}_statistics_{timestamp}.png"
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {output}")
    
    # 4. Cardinality analysis
    print("  - Cardinality analysis")
    fig, ax = plt.subplots(figsize=(10, 5))
    cardinality = df.nunique()
    cardinality.plot(kind='barh', ax=ax, color='coral')
    plt.title(f'Column Cardinality - {filename}', fontsize=14, fontweight='bold')
    plt.xlabel('Unique Values')
    plt.tight_layout()
    output = f"{viz_dir}/{filename}_cardinality_{timestamp}.png"
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {output}")
    
    # 5. Text length analysis (for string columns)
    text_cols = df.select_dtypes(include=['object']).columns
    if len(text_cols) > 0:
        print("  - Text length analysis")
        fig, axes = plt.subplots(1, min(3, len(text_cols)), figsize=(15, 4))
        if len(text_cols) == 1:
            axes = [axes]
        
        for idx, col in enumerate(text_cols[:3]):
            ax = axes[idx]
            text_lengths = df[col].astype(str).str.len()
            ax.hist(text_lengths, bins=30, color='skyblue', edgecolor='black')
            ax.set_title(f'{col}', fontsize=11, fontweight='bold')
            ax.set_xlabel('Text Length')
            ax.set_ylabel('Frequency')
        
        plt.tight_layout()
        output = f"{viz_dir}/{filename}_text_analysis_{timestamp}.png"
        plt.savefig(output, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"    Saved: {output}")
    
    # 6. Summary report
    print("  - Summary report")
    fig = plt.figure(figsize=(12, 8))
    
    summary_text = f"""
CLEANED DATA VISUALIZATION REPORT
{'='*60}

Dataset: {filename}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATASET OVERVIEW
{'-'*60}
Shape: {df.shape[0]:,} rows x {df.shape[1]} columns
Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB
Duplicates: {df.duplicated().sum()}

MISSING DATA
{'-'*60}
"""
    
    for col in df.columns:
        missing = df[col].isnull().sum()
        missing_pct = (missing / len(df)) * 100
        summary_text += f"{col}: {missing} ({missing_pct:.1f}%)\n"
    
    summary_text += f"\nCOLUMN TYPES\n{'-'*60}\n"
    for col in df.columns:
        summary_text += f"{col}: {df[col].dtype}\n"
    
    summary_text += f"\nCOLUMN CARDINALITY\n{'-'*60}\n"
    for col in df.columns:
        unique = df[col].nunique()
        summary_text += f"{col}: {unique} unique values\n"
    
    ax = fig.add_subplot(111)
    ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
            fontfamily='monospace', fontsize=9, verticalalignment='top')
    ax.axis('off')
    plt.tight_layout()
    output = f"{viz_dir}/{filename}_summary_report_{timestamp}.png"
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {output}")
    
    print(f"\nAll visualizations saved to: {viz_dir}/")
    print(f"Total files: 6 visualizations generated")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_visualizations.py <cleaned_csv_file>")
        print("\nExample:")
        print("  python3 generate_visualizations.py data/cleaned/us-shein-automotive-4110_cleaned_20251110_110119.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    create_visualizations(csv_file)
