#!/usr/bin/env python3
"""
Test script to showcase the Enhanced Inspector Agent features
"""
import pandas as pd
import yaml
from agents.inspector.inspector_agent import InspectorAgent

def test_inspector():
    # Load config
    with open('configs/pipeline.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Load data
    data = pd.read_csv('data/raw/us-shein-appliances-3987.csv')
    
    # Initialize Inspector
    inspector = InspectorAgent(config['agents']['inspector']['config'])
    
    # Analyze
    print("=" * 80)
    print("🔍 ENHANCED INSPECTOR AGENT - Detailed Analysis Report")
    print("=" * 80)
    print(f"\n📊 Dataset: {data.shape[0]} rows × {data.shape[1]} columns\n")
    
    report = inspector.analyze_data(data)
    
    # Display Results
    print("\n" + "=" * 80)
    print("📋 QUALITY ASSESSMENT")
    print("=" * 80)
    print(f"\n🎯 Overall Quality: {report.overall_quality.value.upper()}")
    print(f"📅 Timestamp: {report.timestamp}")
    
    print("\n" + "-" * 80)
    print("📊 CORE METRICS")
    print("-" * 80)
    print(f"Missing Values (avg): {sum(report.missing_values.values())/len(report.missing_values):.2f}%")
    print(f"Duplicate Rows: {report.duplicate_count}")
    print(f"Outliers Detected: {report.outlier_count}")
    
    print("\n" + "-" * 80)
    print("🎨 ENHANCED FEATURES")
    print("-" * 80)
    
    # Cardinality Analysis
    print("\n1️⃣  Cardinality Analysis:")
    for col, card in list(report.cardinality_analysis.items())[:5]:
        print(f"   • {col}: {card}")
    
    # Skewness Analysis
    if report.skewness_analysis:
        print("\n2️⃣  Skewness Analysis:")
        for col, skew in list(report.skewness_analysis.items())[:3]:
            print(f"   • {col}: {skew}")
    
    # Pattern Analysis
    if report.pattern_analysis:
        print("\n3️⃣  Pattern Analysis:")
        for col, patterns in list(report.pattern_analysis.items())[:3]:
            print(f"   • {col}:")
            print(f"     - Consistency: {patterns['consistency_pct']}%")
            print(f"     - Pattern Diversity: {patterns['pattern_diversity']}")
    
    # Consistency Issues
    if report.consistency_issues:
        print("\n4️⃣  Consistency Issues:")
        for col, issues in list(report.consistency_issues.items())[:3]:
            print(f"   • {col}:")
            for issue in issues:
                print(f"     - {issue}")
    
    # Column Quality Scores
    print("\n5️⃣  Column Quality Scores (Top 5):")
    sorted_scores = sorted(report.column_quality_scores.items(), key=lambda x: x[1], reverse=True)
    for col, score in sorted_scores[:5]:
        status = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
        print(f"   {status} {col}: {score:.3f}")
    
    # Outlier Details
    if report.outlier_details:
        print("\n6️⃣  Outlier Details:")
        for col, details in list(report.outlier_details.items())[:3]:
            print(f"   • {col}:")
            print(f"     - Count: {details['count']} ({details['percentage']}%)")
            print(f"     - Bounds: [{details['lower_bound']}, {details['upper_bound']}]")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("💡 SMART RECOMMENDATIONS")
    print("=" * 80)
    for i, rec in enumerate(report.recommendations, 1):
        print(f"\n{i}. {rec}")
    
    # Column Statistics Sample
    print("\n" + "=" * 80)
    print("📈 COLUMN STATISTICS (Sample)")
    print("=" * 80)
    for col, stats in list(report.column_stats.items())[:3]:
        print(f"\n{col}:")
        for key, value in stats.items():
            if key not in ['patterns']:  # Skip patterns for brevity
                print(f"  • {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✓ Analysis Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_inspector()
