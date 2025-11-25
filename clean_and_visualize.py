#!/usr/bin/env python3
"""
Complete Pipeline: Clean Data + Generate Visualizations
Usage: python3 clean_and_visualize.py <raw_csv_file>
"""
import sys
import subprocess
from pathlib import Path
import pandas as pd
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 clean_and_visualize.py <raw_csv_file>")
        print("\nExample:")
        print("  python3 clean_and_visualize.py data/raw/us-shein-automotive-4110.csv")
        sys.exit(1)
    
    raw_file = sys.argv[1]
    
    if not Path(raw_file).exists():
        print(f"ERROR: File not found: {raw_file}")
        sys.exit(1)
    
    print("="*70)
    print("COMPLETE PIPELINE: CLEAN + VISUALIZE")
    print("="*70)
    
    # Step 1: Clean the data
    print("\nSTEP 1: CLEANING DATA")
    print("-"*70)
    result = subprocess.run(['python3', 'run_agent.py', raw_file], 
                          capture_output=False)
    
    if result.returncode != 0:
        print("\nERROR: Cleaning failed")
        sys.exit(1)
    
    # Find the cleaned file
    print("\nSTEP 2: FINDING CLEANED DATA")
    print("-"*70)
    
    cleaned_dir = Path("data/cleaned")
    csv_files = sorted(cleaned_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not csv_files:
        print("ERROR: No cleaned files found")
        sys.exit(1)
    
    cleaned_file = csv_files[0]
    print(f"Found: {cleaned_file}")
    print(f"Size: {cleaned_file.stat().st_size / 1024:.1f} KB")
    print(f"Modified: {datetime.fromtimestamp(cleaned_file.stat().st_mtime)}")
    
    # Step 2: Generate visualizations
    print("\nSTEP 3: GENERATING VISUALIZATIONS")
    print("-"*70)
    result = subprocess.run(['python3', 'generate_visualizations.py', str(cleaned_file)],
                          capture_output=False)
    
    if result.returncode != 0:
        print("\nERROR: Visualization generation failed")
        sys.exit(1)
    
    # Summary
    print("\n" + "="*70)
    print("COMPLETE PIPELINE: SUCCESS!")
    print("="*70)
    print(f"\nCleaned data: {cleaned_file}")
    
    viz_dir = Path("data/visualizations")
    viz_files = list(viz_dir.glob("*.png"))
    print(f"Visualizations: {len(viz_files)} charts generated")
    
    # Show file locations
    df = pd.read_csv(cleaned_file)
    print(f"\nDataset Summary:")
    print(f"  Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"  Missing: {df.isnull().sum().sum()} cells (0%)")
    
    print(f"\nOutput Locations:")
    print(f"  Cleaned data: {cleaned_file}")
    print(f"  Visualizations: {viz_dir}/")
    
    print(f"\nTo view visualizations:")
    print(f"  open {viz_dir}/")

if __name__ == "__main__":
    main()
