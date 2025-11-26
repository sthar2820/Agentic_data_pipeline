#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path

from orchestrator.pipeline import DataPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Data Pipeline - Intelligent data processing with AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --file data/raw/sample.csv
  python main.py --directory data/raw/
  python main.py --file data/raw/sample.csv --config configs/custom_pipeline.yaml
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Path to a single file to process'
    )
    
    parser.add_argument(
        '--directory', '-d',
        type=str,
        help='Path to directory containing files to process'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='configs/pipeline.yaml',
        help='Path to configuration file (default: configs/pipeline.yaml)'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show pipeline configuration status'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.directory and not args.status:
        parser.error("Must specify either --file, --directory, or --status")
    
    if args.file and args.directory:
        parser.error("Cannot specify both --file and --directory")
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    try:
        # Initialize pipeline
        pipeline = DataPipeline(args.config)
        
        if args.status:
            # Show pipeline status
            status = pipeline.get_pipeline_status()
            print("\n" + "="*50)
            print("AGENTIC DATA PIPELINE STATUS")
            print("="*50)
            print(f"Pipeline: {status['pipeline_name']} v{status['version']}")
            print(f"\nAgents:")
            for name, agent_info in status['agents'].items():
                status_str = "[ENABLED]" if agent_info['enabled'] else "[DISABLED]"
                print(f"  {agent_info['name']}: {status_str}")
            print(f"\nData Paths:")
            for path_name, path_value in status['data_paths'].items():
                print(f"  {path_name}: {path_value}")
            print("="*50)
            return
        
        if args.file:
            # Process single file
            if not os.path.exists(args.file):
                print(f"Error: File not found: {args.file}")
                sys.exit(1)
            
            print(f"\nProcessing file: {args.file}")
            print("-" * 50)
            
            result = pipeline.run_pipeline(args.file)
            print_result(result)
            
        elif args.directory:
            # Process directory
            if not os.path.exists(args.directory):
                print(f"Error: Directory not found: {args.directory}")
                sys.exit(1)
            
            print(f"\nProcessing directory: {args.directory}")
            print("-" * 50)
            
            results = pipeline.run_batch_pipeline(args.directory)
            
            if not results:
                print("No supported files found in directory.")
                print("Supported formats: CSV, Excel (.xlsx/.xls), JSON, Parquet")
                return
            
            print(f"\nProcessed {len(results)} files:")
            print("="*70)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {os.path.basename(result.input_file)}")
                print_result(result, detailed=False)
    
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


def print_result(result, detailed=True):
    """Print pipeline execution result"""
    status_indicator = "[OK]" if result.status.value == "completed" else "[FAIL]"
    
    print(f"Status: {status_indicator} {result.status.value.upper()}")
    print(f"Execution time: {result.execution_time:.2f} seconds")
    
    if result.errors:
        print(f"Errors: {len(result.errors)}")
        if detailed:
            for error in result.errors:
                print(f"  - {error}")
    
    if result.status.value == "completed" and detailed:
        print(f"Output file: {result.output_file}")
        
        if result.quality_report:
            print(f"Data quality: {result.quality_report.overall_quality.value}")
            print(f"Recommendations: {len(result.quality_report.recommendations)}")
        
        if result.cleaning_report:
            orig_shape = result.cleaning_report.original_shape
            clean_shape = result.cleaning_report.cleaned_shape
            print(f"Data shape: {orig_shape} → {clean_shape}")
            print(f"Rows removed: {result.cleaning_report.rows_removed}")
        
        if result.insight_report:
            print(f"Visualizations: {len(result.insight_report.plots_generated)}")
            print(f"Key insights: {len(result.insight_report.key_insights)}")


if __name__ == "__main__":
    main()
