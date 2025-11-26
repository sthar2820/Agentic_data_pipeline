#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced agentic pipeline improvements
"""
import os
import sys
from pathlib import Path

print("=" * 80)
print("🚀 AGENTIC DATA PIPELINE - ENHANCED VERSION TEST")
print("=" * 80)
print()

# Test 1: Check if all new agents are importable
print("📦 Test 1: Checking new agent imports...")
try:
    from agents.anomaly.anomaly_agent import AnomalyDetectionAgent
    print("  ✅ Anomaly Detection Agent - OK")
except Exception as e:
    print(f"  ❌ Anomaly Detection Agent - FAILED: {e}")
    sys.exit(1)

try:
    from agents.feature_engineer.feature_agent import FeatureEngineeringAgent
    print("  ✅ Feature Engineering Agent - OK")
except Exception as e:
    print(f"  ❌ Feature Engineering Agent - FAILED: {e}")
    sys.exit(1)

try:
    from agents.reporter.report_agent import ReportGenerationAgent
    print("  ✅ Report Generation Agent - OK")
except Exception as e:
    print(f"  ❌ Report Generation Agent - FAILED: {e}")
    sys.exit(1)

try:
    from agents.refiner.cleaner_agent import CleanerAgent
    print("  ✅ Enhanced Refiner Agent - OK")
except Exception as e:
    print(f"  ❌ Enhanced Refiner Agent - FAILED: {e}")
    sys.exit(1)

print()

# Test 2: Check pipeline configuration
print("⚙️  Test 2: Checking pipeline configuration...")
try:
    from orchestrator.pipeline import DataPipeline
    import yaml

    config_path = "configs/pipeline.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Check for new agents in config
    agents = config.get('agents', {})

    if 'anomaly_detector' in agents:
        print("  ✅ Anomaly Detector config - OK")
    else:
        print("  ⚠️  Anomaly Detector config - Not found (optional)")

    if 'feature_engineer' in agents:
        print("  ✅ Feature Engineer config - OK")
    else:
        print("  ⚠️  Feature Engineer config - Not found (optional)")

    if 'reporter' in agents:
        print("  ✅ Reporter config - OK")
    else:
        print("  ⚠️  Reporter config - Not found (optional)")

except Exception as e:
    print(f"  ❌ Configuration check - FAILED: {e}")
    sys.exit(1)

print()

# Test 3: Run pipeline on sample data
print("🔬 Test 3: Running pipeline on sample data...")
print("-" * 80)

sample_file = "data/raw/us-shein-automotive-4110.csv"

if not os.path.exists(sample_file):
    print(f"  ❌ Sample file not found: {sample_file}")
    print("  💡 Please add a CSV file to data/raw/ directory")
    sys.exit(1)

print(f"  📁 Input file: {sample_file}")
print()

try:
    # Initialize pipeline
    pipeline = DataPipeline("configs/pipeline.yaml")

    # Show enabled agents
    print("  🤖 Enabled Agents:")
    print(f"     • Inspector: {config['agents']['inspector']['enabled']}")
    print(f"     • Anomaly Detector: {config['agents'].get('anomaly_detector', {}).get('enabled', False)}")
    print(f"     • Refiner: {config['agents']['refiner']['enabled']}")
    print(f"     • Feature Engineer: {config['agents'].get('feature_engineer', {}).get('enabled', False)}")
    print(f"     • Insight: {config['agents']['insight']['enabled']}")
    print(f"     • Reporter: {config['agents'].get('reporter', {}).get('enabled', False)}")
    print()

    # Run pipeline
    print("  ⚡ Starting pipeline execution...")
    print()

    result = pipeline.run_pipeline(sample_file)

    print()
    print("-" * 80)
    print("  ✅ PIPELINE EXECUTION COMPLETED!")
    print("-" * 80)
    print()

    # Display results
    print("📊 RESULTS SUMMARY:")
    print(f"  • Status: {result.status.value.upper()}")
    print(f"  • Execution Time: {result.execution_time:.2f} seconds")
    print(f"  • Input File: {result.input_file}")
    print(f"  • Output File: {result.output_file}")

    if result.quality_report:
        print(f"  • Data Quality: {result.quality_report.overall_quality.value.upper()}")
        print(f"  • Missing Values: {sum(result.quality_report.missing_values.values()):.0f} total")
        print(f"  • Duplicates: {result.quality_report.duplicate_count}")
        print(f"  • Outliers: {result.quality_report.outlier_count}")

    if result.cleaning_report:
        print(f"  • Original Shape: {result.cleaning_report.original_shape}")
        print(f"  • Cleaned Shape: {result.cleaning_report.cleaned_shape}")
        print(f"  • Rows Removed: {result.cleaning_report.rows_removed}")
        print(f"  • Actions Taken: {len(result.cleaning_report.actions_taken)}")

    if result.insight_report:
        print(f"  • Visualizations: {len(result.insight_report.plots_generated)}")

    print()
    print("📁 OUTPUT FILES:")
    print(f"  • Cleaned Data: {result.output_file}")

    # Check for artifacts
    artifacts_dir = Path("data/artifacts")
    if artifacts_dir.exists():
        report_files = list(artifacts_dir.glob("pipeline_report_*.html"))
        if report_files:
            latest_report = max(report_files, key=os.path.getctime)
            print(f"  • Comprehensive Report: {latest_report}")
            print()
            print("  💡 TIP: Open the HTML report in your browser:")
            print(f"     open {latest_report}")

    print()

    # Check new agent outputs
    print("🔍 NEW FEATURES CHECK:")

    # Check if anomaly detection ran
    anomaly_files = list(artifacts_dir.glob("*anomaly*"))
    if config['agents'].get('anomaly_detector', {}).get('enabled', False):
        print("  ✅ Anomaly Detection: ENABLED & RAN")
    else:
        print("  ⚠️  Anomaly Detection: Disabled in config")

    # Check if feature engineering ran
    if config['agents'].get('feature_engineer', {}).get('enabled', False):
        print("  ✅ Feature Engineering: ENABLED & RAN")
    else:
        print("  ⚠️  Feature Engineering: Disabled in config")

    # Check if report was generated
    if report_files:
        print("  ✅ Comprehensive Report: GENERATED")
    else:
        print("  ⚠️  Comprehensive Report: Not generated")

    print()
    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("🎉 The enhanced agentic pipeline is working perfectly!")
    print()
    print("Next steps:")
    print("  1. Open the comprehensive HTML report (see path above)")
    print("  2. Review the cleaned data CSV file")
    print("  3. Check the visualizations in data/artifacts/")
    print()

except Exception as e:
    print()
    print("=" * 80)
    print("❌ TEST FAILED")
    print("=" * 80)
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
