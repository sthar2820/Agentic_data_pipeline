#!/usr/bin/env python3
"""
Quality Checker - Shows what's needed to achieve EXCELLENT data quality
"""
import pandas as pd
import sys

def check_quality_requirements(file_path):
    """Analyze current data quality and show improvement recommendations"""
    
    print("=" * 70)
    print("📊 DATA QUALITY ANALYSIS - Path to EXCELLENT Quality")
    print("=" * 70)
    
    # Load data
    data = pd.read_csv(file_path)
    total_rows = len(data)
    
    print(f"\n📁 File: {file_path}")
    print(f"📐 Shape: {data.shape[0]} rows × {data.shape[1]} columns")
    print(f"📋 Columns: {', '.join(data.columns.tolist())}")
    
    # 1. Missing Values Analysis
    print("\n" + "─" * 70)
    print("1️⃣  MISSING VALUES ANALYSIS")
    print("─" * 70)
    missing_pct = {}
    for col in data.columns:
        pct = (data[col].isnull().sum() / total_rows * 100)
        missing_pct[col] = round(pct, 2)
    
    avg_missing = sum(missing_pct.values()) / len(missing_pct)
    missing_penalty = avg_missing * 0.5
    
    print(f"Average missing: {avg_missing:.2f}%")
    print(f"Penalty: -{missing_penalty:.2f} points")
    
    if avg_missing > 30:
        print(f"❌ ISSUE: Average missing values too high!")
        print(f"   Target: < 30% | Current: {avg_missing:.2f}%")
        print(f"   Action: Remove or impute missing values")
    else:
        print(f"✅ GOOD: Missing values within acceptable range")
    
    # Show worst columns
    worst_missing = sorted(missing_pct.items(), key=lambda x: x[1], reverse=True)[:3]
    if worst_missing[0][1] > 0:
        print(f"\n   Worst columns:")
        for col, pct in worst_missing:
            if pct > 0:
                print(f"   - {col}: {pct:.1f}% missing")
    
    # 2. Duplicates Analysis
    print("\n" + "─" * 70)
    print("2️⃣  DUPLICATES ANALYSIS")
    print("─" * 70)
    duplicate_count = data.duplicated().sum()
    dup_pct = (duplicate_count / total_rows * 100)
    dup_penalty = min(dup_pct * 2, 20)
    
    print(f"Duplicate rows: {duplicate_count} ({dup_pct:.2f}%)")
    print(f"Penalty: -{dup_penalty:.2f} points")
    
    if dup_pct > 7.5:
        print(f"❌ ISSUE: Too many duplicates!")
        print(f"   Target: < 7.5% | Current: {dup_pct:.2f}%")
        print(f"   Action: Remove {duplicate_count} duplicate rows")
    else:
        print(f"✅ GOOD: Duplicates within acceptable range")
    
    # 3. Outliers Analysis (simplified IQR method)
    print("\n" + "─" * 70)
    print("3️⃣  OUTLIERS ANALYSIS")
    print("─" * 70)
    numeric_cols = data.select_dtypes(include=['number']).columns
    outlier_rows = set()
    
    for col in numeric_cols:
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
        outlier_rows.update(data[outlier_mask].index.tolist())
    
    outlier_count = len(outlier_rows)
    outlier_pct = (outlier_count / total_rows * 100)
    outlier_penalty = min(outlier_pct, 10)
    
    print(f"Rows with outliers: {outlier_count} ({outlier_pct:.2f}%)")
    print(f"Penalty: -{outlier_penalty:.2f} points")
    
    if outlier_pct > 10:
        print(f"❌ ISSUE: Too many outliers!")
        print(f"   Target: < 10% | Current: {outlier_pct:.2f}%")
        print(f"   Action: Review and handle {outlier_count} rows with outliers")
    else:
        print(f"✅ GOOD: Outliers within acceptable range")
    
    # 4. Column Quality Score (simplified)
    print("\n" + "─" * 70)
    print("4️⃣  COLUMN QUALITY SCORES")
    print("─" * 70)
    
    column_quality_scores = {}
    for col in data.columns:
        score = 1.0
        
        # Completeness (40% weight)
        completeness_penalty = (missing_pct[col] / 100) * 0.4
        score -= completeness_penalty
        
        # Cardinality (25% weight)
        unique_count = data[col].nunique()
        if unique_count == 1:
            score -= 0.25  # Constant column
        
        # Pattern consistency for text columns (15% weight)
        if data[col].dtype == 'object':
            non_null = data[col].dropna()
            if len(non_null) > 0:
                # Check if values have consistent patterns
                str_lengths = non_null.astype(str).str.len()
                cv = str_lengths.std() / str_lengths.mean() if str_lengths.mean() > 0 else 0
                if cv > 0.5:
                    score -= 0.1
        
        column_quality_scores[col] = max(0.0, min(1.0, round(score, 3)))
    
    avg_quality = sum(column_quality_scores.values()) / len(column_quality_scores)
    quality_penalty = (1 - avg_quality) * 30
    
    print(f"Average column quality: {avg_quality:.3f}")
    print(f"Penalty: -{quality_penalty:.2f} points")
    
    if avg_quality < 0.5:
        print(f"❌ ISSUE: Column quality too low!")
        print(f"   Target: > 0.5 | Current: {avg_quality:.3f}")
    else:
        print(f"✅ GOOD: Column quality is acceptable")
    
    # Show worst columns
    worst_quality = sorted(column_quality_scores.items(), key=lambda x: x[1])[:3]
    print(f"\n   Column quality scores:")
    for col, score in worst_quality:
        status = "✅" if score >= 0.5 else "⚠️"
        print(f"   {status} {col}: {score:.3f}")
    
    # Final Score Calculation
    print("\n" + "=" * 70)
    print("🎯 FINAL QUALITY SCORE")
    print("=" * 70)
    
    final_score = 100 - missing_penalty - dup_penalty - outlier_penalty - quality_penalty
    
    print(f"\nBase score:           100.00")
    print(f"Missing penalty:      -{missing_penalty:.2f}")
    print(f"Duplicate penalty:    -{dup_penalty:.2f}")
    print(f"Outlier penalty:      -{outlier_penalty:.2f}")
    print(f"Column quality:       -{quality_penalty:.2f}")
    print(f"{'─' * 40}")
    print(f"FINAL SCORE:          {final_score:.2f}")
    
    if final_score >= 85:
        quality = "🌟 EXCELLENT"
        color = "\033[92m"  # Green
    elif final_score >= 70:
        quality = "✅ GOOD"
        color = "\033[93m"  # Yellow
    elif final_score >= 50:
        quality = "⚠️  FAIR"
        color = "\033[93m"  # Yellow
    else:
        quality = "❌ POOR"
        color = "\033[91m"  # Red
    
    reset = "\033[0m"
    print(f"\n{color}Quality Rating: {quality}{reset}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("💡 RECOMMENDATIONS TO REACH EXCELLENT (≥85)")
    print("=" * 70)
    
    points_needed = 85 - final_score
    if points_needed > 0:
        print(f"\n🎯 You need {points_needed:.2f} more points to reach EXCELLENT\n")
        
        if avg_missing > 5:
            potential_gain = min((avg_missing - 5) * 0.5, missing_penalty)
            print(f"1. Reduce missing values from {avg_missing:.1f}% to <5%")
            print(f"   → Potential gain: +{potential_gain:.2f} points")
        
        if dup_pct > 0:
            potential_gain = dup_penalty
            print(f"2. Remove all {duplicate_count} duplicate rows")
            print(f"   → Potential gain: +{potential_gain:.2f} points")
        
        if outlier_pct > 5:
            potential_gain = min(outlier_pct - 5, outlier_penalty)
            print(f"3. Handle outliers (reduce from {outlier_pct:.1f}% to <5%)")
            print(f"   → Potential gain: +{potential_gain:.2f} points")
        
        if avg_quality < 0.8:
            potential_gain = min((0.8 - avg_quality) * 30, quality_penalty * 0.5)
            print(f"4. Improve column quality (current: {avg_quality:.3f}, target: >0.8)")
            print(f"   → Potential gain: +{potential_gain:.2f} points")
            print(f"   Actions: Fix constant columns, standardize formats, clean text")
    else:
        print("\n🎉 Congratulations! Your data already has EXCELLENT quality!")
        print("   Keep up the good work maintaining data standards.")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_quality.py <csv_file>")
        sys.exit(1)
    
    check_quality_requirements(sys.argv[1])
