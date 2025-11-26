#!/usr/bin/env python3
"""
Simple Inspector Agent Runner
Usage: python3 run_agent.py <csv_file>
Automatically analyzes and cleans data, saves to data/cleaned/
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import yaml
from agents.inspector.inspector_agent import InspectorAgent
from agents.refiner.cleaner_agent import CleanerAgent


def main():
    # Check arguments
    if len(sys.argv) < 2:
        print("ERROR: Usage: python3 run_agent.py <csv_file>")
        print("\nExample:")
        print("  python3 run_agent.py data/raw/us-shein-beauty_and_health-4267.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Validate file
    if not Path(csv_file).exists():
        print(f"ERROR: File not found: {csv_file}")
        sys.exit(1)
    
    try:
        # Load config
        with open('configs/pipeline.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Load data
        print(f"\nLoading: {csv_file}")
        data = pd.read_csv(csv_file)
        print(f"Loaded: {data.shape[0]:,} rows x {data.shape[1]} columns")
        
        # Run Inspector
        print(f"\nAnalyzing data quality...")
        inspector_config = config['agents']['inspector']['config']
        inspector_config['dataset_name'] = Path(csv_file).stem
        inspector = InspectorAgent(inspector_config)
        report = inspector.analyze_data(data)
        
        # Display summary
        print("\n" + "=" * 70)
        print("QUALITY ASSESSMENT")
        print("=" * 70)
        print(f"Overall Quality: {report.overall_quality.value.upper()}")
        avg_missing = sum(report.missing_values.values()) / len(report.missing_values)
        avg_quality = sum(report.column_quality_scores.values()) / len(report.column_quality_scores)
        print(f"Missing Values: {avg_missing:.1f}% average")
        print(f"Duplicates: {report.duplicate_count} rows")
        print(f"Outliers: {report.outlier_count}")
        print(f"Column Quality: {avg_quality:.3f} average")
        
        print(f"\nTOP RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations[:5], 1):
            print(f"{i}. {rec}")
        
        # Auto-clean
        print("\n" + "=" * 70)
        print("AUTO-CLEANING DATA...")
        print("=" * 70)
        
        cleaner_config = config['agents']['refiner']['config']
        cleaner = CleanerAgent(cleaner_config)
        cleaned_data, cleaning_report = cleaner.clean_data(data)
        
        print(f"Cleaning complete!")
        print(f"   Original: {data.shape[0]:,} rows x {data.shape[1]} columns")
        print(f"   Cleaned:  {cleaned_data.shape[0]:,} rows x {cleaned_data.shape[1]} columns")
        print(f"   Removed:  {cleaning_report.rows_removed:,} rows")
        print(f"   Dropped:  {len(cleaning_report.columns_dropped)} columns")
        
        # Save cleaned data
        Path("data/cleaned").mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(csv_file).stem
        output_file = f"data/cleaned/{filename}_cleaned_{timestamp}.csv"
        cleaned_data.to_csv(output_file, index=False)
        
        print(f"\nSAVED TO:")
        print(f"   Cleaned data: {output_file}")
        print(f"   Quality report: data/artifacts/{Path(csv_file).stem}_*_dq_report.json")
        print(f"   Clean plan: data/artifacts/{Path(csv_file).stem}_*_clean_plan.json")
        
        # Verify cleaned data quality
        print("\n" + "=" * 70)
        print("VERIFYING CLEANED DATA QUALITY...")
        print("=" * 70)
        
        inspector2 = InspectorAgent({'dataset_name': f'{filename}_cleaned'})
        report2 = inspector2.analyze_data(cleaned_data)
        
        avg_missing2 = sum(report2.missing_values.values()) / len(report2.missing_values)
        avg_quality2 = sum(report2.column_quality_scores.values()) / len(report2.column_quality_scores)
        
        print(f"New Quality: {report2.overall_quality.value.upper()}")
        print(f"Missing Values: {avg_missing2:.1f}% average")
        print(f"Duplicates: {report2.duplicate_count} rows")
        print(f"Column Quality: {avg_quality2:.3f} average")
        
        print("\n" + "=" * 70)
        print("SUCCESS! Data cleaned and saved.")
        print("=" * 70)
        print(f"\nQuality improved: {report.overall_quality.value.upper()} -> {report2.overall_quality.value.upper()}")
        print(f"Use cleaned data at: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\nWARNING: Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
