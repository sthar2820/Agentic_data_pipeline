#!/usr/bin/env python3
"""
Comprehensive Data Visualization and Analysis Report Generator
Generates detailed visualizations, charts, and HTML reports for cleaned datasets
Usage: python3 generate_comprehensive_report.py <cleaned_csv_file>
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import warnings

warnings.filterwarnings('ignore')

# Configure matplotlib
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

sns.set_style("whitegrid")
sns.set_palette("husl")


class ComprehensiveReportGenerator:
    """Generate comprehensive data analysis reports and visualizations"""
    
    def __init__(self, csv_file: str, output_dir: str = "data/visualizations"):
        """Initialize the report generator"""
        self.csv_file = Path(csv_file)
        if not self.csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = pd.read_csv(self.csv_file)
        self.filename = self.csv_file.stem
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n{'='*70}")
        print(f"COMPREHENSIVE REPORT GENERATOR")
        print(f"{'='*70}")
        print(f"Dataset: {self.filename}")
        print(f"Shape: {self.df.shape[0]:,} rows × {self.df.shape[1]} columns")
        print(f"Memory: {self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        print(f"Output: {self.output_dir}/")
        
    def _save_figure(self, fig, name: str, dpi: int = 150) -> Path:
        """Save figure with consistent naming"""
        output_path = self.output_dir / f"{self.filename}_{name}_{self.timestamp}.png"
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        size_kb = output_path.stat().st_size / 1024
        print(f"  ✓ {name:<40} ({size_kb:>6.1f} KB)")
        return output_path
    
    def _get_quality_color(self, percentage: float) -> str:
        """Get color based on quality percentage"""
        if percentage >= 80:
            return '#2ca02c'  # Green - Excellent
        elif percentage >= 60:
            return '#ff7f0e'  # Orange - Good
        elif percentage >= 40:
            return '#ff9800'  # Dark Orange - Fair
        else:
            return '#d62728'  # Red - Poor
    
    def generate_all(self):
        """Generate all visualizations and reports"""
        print(f"\nGenerating visualizations...\n")
        
        self.plot_missing_values_analysis()
        self.plot_data_types_analysis()
        self.plot_cardinality_analysis()
        self.plot_numeric_distributions()
        self.plot_categorical_analysis()
        self.plot_data_quality_scorecard()
        self.plot_summary_statistics()
        self.generate_html_report()
        self.generate_json_report()
        
        print(f"\n{'='*70}")
        print(f"✓ All visualizations generated successfully!")
        print(f"{'='*70}\n")
    
    def plot_missing_values_analysis(self):
        """Analyze and visualize missing values"""
        print("Generating missing values analysis...")
        
        fig = plt.figure(figsize=(14, 8))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. Missing percentage by column (bar)
        ax1 = fig.add_subplot(gs[0, :])
        missing_pct = (self.df.isnull().sum() / len(self.df)) * 100
        colors = [self._get_quality_color(100 - x) for x in missing_pct]
        missing_pct.plot(kind='bar', ax=ax1, color=colors, edgecolor='black', alpha=0.8)
        ax1.set_title('Missing Data by Column (%)', fontsize=13, fontweight='bold', pad=10)
        ax1.set_ylabel('Missing Percentage (%)', fontweight='bold')
        ax1.set_xlabel('Columns', fontweight='bold')
        ax1.axhline(y=20, color='orange', linestyle='--', alpha=0.5, linewidth=1.5)
        ax1.axhline(y=50, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Missing data heatmap
        ax2 = fig.add_subplot(gs[1, 0])
        missing_matrix = self.df.isnull().astype(int)
        if missing_matrix.sum().sum() == 0:
            ax2.text(0.5, 0.5, 'No Missing Values', ha='center', va='center', 
                    fontsize=14, fontweight='bold', transform=ax2.transAxes)
            ax2.set_title('Missing Data Pattern', fontsize=12, fontweight='bold')
        else:
            sns.heatmap(missing_matrix, cmap='RdYlGn_r', cbar_kws={'label': 'Missing'}, 
                       ax=ax2, yticklabels=False, xticklabels=True)
            ax2.set_title('Missing Data Pattern', fontsize=12, fontweight='bold')
        
        # 3. Data completeness summary
        ax3 = fig.add_subplot(gs[1, 1])
        completeness = (self.df.notna().sum() / len(self.df)) * 100
        completeness.plot(kind='barh', ax=ax3, color='#2ca02c', edgecolor='black', alpha=0.8)
        ax3.set_xlabel('Completeness (%)', fontweight='bold')
        ax3.set_title('Data Completeness by Column', fontsize=12, fontweight='bold')
        ax3.set_xlim(0, 105)
        ax3.grid(axis='x', alpha=0.3)
        
        self._save_figure(fig, '01_missing_values_analysis', dpi=150)
    
    def plot_data_types_analysis(self):
        """Analyze data types"""
        print("Generating data types analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Data type distribution
        dtype_counts = self.df.dtypes.value_counts()
        axes[0, 0].bar(range(len(dtype_counts)), dtype_counts.values, 
                       color='steelblue', edgecolor='black', alpha=0.8)
        axes[0, 0].set_xticks(range(len(dtype_counts)))
        axes[0, 0].set_xticklabels([str(x) for x in dtype_counts.index], rotation=45)
        axes[0, 0].set_title('Data Type Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_ylabel('Count', fontweight='bold')
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Column memory usage
        memory_usage = self.df.memory_usage(deep=True) / 1024
        axes[0, 1].barh(range(len(memory_usage)), memory_usage.values, 
                        color='coral', edgecolor='black', alpha=0.8)
        axes[0, 1].set_yticks(range(len(memory_usage)))
        axes[0, 1].set_yticklabels(memory_usage.index)
        axes[0, 1].set_title('Memory Usage by Column (KB)', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Memory (KB)', fontweight='bold')
        axes[0, 1].grid(axis='x', alpha=0.3)
        
        # 3. Numeric columns summary
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            numeric_summary = []
            for col in numeric_cols:
                numeric_summary.append({
                    'Column': col,
                    'Min': self.df[col].min(),
                    'Max': self.df[col].max(),
                    'Mean': self.df[col].mean()
                })
            
            axes[1, 0].axis('tight')
            axes[1, 0].axis('off')
            table_data = [[f"{v:.2f}" if isinstance(v, float) else str(v) for v in row.values()] 
                         for row in numeric_summary]
            table = axes[1, 0].table(cellText=table_data,
                                    colLabels=['Column', 'Min', 'Max', 'Mean'],
                                    cellLoc='center', loc='center',
                                    colWidths=[0.3, 0.2, 0.2, 0.2])
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 2)
            axes[1, 0].set_title('Numeric Columns Summary', fontsize=12, fontweight='bold', pad=10)
        else:
            axes[1, 0].text(0.5, 0.5, 'No numeric columns', ha='center', va='center',
                           transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Numeric Columns Summary', fontsize=12, fontweight='bold')
        
        # 4. Categorical columns summary
        cat_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        if cat_cols:
            cat_summary = []
            for col in cat_cols[:5]:  # Limit to 5 columns
                cat_summary.append({
                    'Column': col,
                    'Unique': self.df[col].nunique(),
                    'Top Value': str(self.df[col].mode().values[0])[:15]
                })
            
            axes[1, 1].axis('tight')
            axes[1, 1].axis('off')
            table_data = [[v for v in row.values()] for row in cat_summary]
            table = axes[1, 1].table(cellText=table_data,
                                    colLabels=['Column', 'Unique', 'Top Value'],
                                    cellLoc='center', loc='center',
                                    colWidths=[0.4, 0.2, 0.4])
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 2)
            axes[1, 1].set_title('Categorical Columns Summary', fontsize=12, fontweight='bold', pad=10)
        else:
            axes[1, 1].text(0.5, 0.5, 'No categorical columns', ha='center', va='center',
                           transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Categorical Columns Summary', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        self._save_figure(fig, '02_data_types_analysis', dpi=150)
    
    def plot_cardinality_analysis(self):
        """Analyze column cardinality"""
        print("Generating cardinality analysis...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Unique values count
        unique_counts = self.df.nunique().sort_values(ascending=True)
        colors = ['#2ca02c' if x < len(self.df) * 0.5 else '#ff7f0e' for x in unique_counts.values]
        axes[0].barh(range(len(unique_counts)), unique_counts.values, 
                    color=colors, edgecolor='black', alpha=0.8)
        axes[0].set_yticks(range(len(unique_counts)))
        axes[0].set_yticklabels(unique_counts.index)
        axes[0].set_xlabel('Unique Values', fontweight='bold')
        axes[0].set_title('Column Cardinality (Unique Values)', fontsize=12, fontweight='bold')
        axes[0].grid(axis='x', alpha=0.3)
        
        # Cardinality ratio
        cardinality_ratio = self.df.nunique() / len(self.df)
        ratio_colors = [self._get_quality_color(x * 100) for x in cardinality_ratio.values]
        axes[1].bar(range(len(cardinality_ratio)), cardinality_ratio.values * 100,
                   color=ratio_colors, edgecolor='black', alpha=0.8)
        axes[1].set_xticks(range(len(cardinality_ratio)))
        axes[1].set_xticklabels(cardinality_ratio.index, rotation=45)
        axes[1].set_ylabel('Cardinality Ratio (%)', fontweight='bold')
        axes[1].set_title('Cardinality Ratio (Unique/Total)', fontsize=12, fontweight='bold')
        axes[1].axhline(y=50, color='orange', linestyle='--', alpha=0.5)
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        self._save_figure(fig, '03_cardinality_analysis', dpi=150)
    
    def plot_numeric_distributions(self):
        """Plot distributions of numeric columns"""
        print("Generating numeric distributions...")
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            print("  No numeric columns found, skipping...")
            return
        
        n_cols = min(len(numeric_cols), 4)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for idx, col in enumerate(numeric_cols[:4]):
            ax = axes[idx]
            self.df[col].hist(bins=30, ax=ax, color='steelblue', edgecolor='black', alpha=0.8)
            ax.set_title(f'Distribution of {col}', fontsize=11, fontweight='bold')
            ax.set_xlabel(col, fontweight='bold')
            ax.set_ylabel('Frequency', fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            # Add stats
            mean_val = self.df[col].mean()
            median_val = self.df[col].median()
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
            ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
            ax.legend(fontsize=8)
        
        # Hide unused subplots
        for idx in range(n_cols, 4):
            axes[idx].axis('off')
        
        plt.tight_layout()
        self._save_figure(fig, '04_numeric_distributions', dpi=150)
    
    def plot_categorical_analysis(self):
        """Analyze categorical columns"""
        print("Generating categorical analysis...")
        
        cat_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        if not cat_cols:
            print("  No categorical columns found, skipping...")
            return
        
        n_cols = min(len(cat_cols), 4)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for idx, col in enumerate(cat_cols[:4]):
            ax = axes[idx]
            value_counts = self.df[col].value_counts().head(10)
            value_counts.plot(kind='barh', ax=ax, color='steelblue', edgecolor='black', alpha=0.8)
            ax.set_title(f'Top Values in {col}', fontsize=11, fontweight='bold')
            ax.set_xlabel('Count', fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
        
        # Hide unused subplots
        for idx in range(n_cols, 4):
            axes[idx].axis('off')
        
        plt.tight_layout()
        self._save_figure(fig, '05_categorical_analysis', dpi=150)
    
    def plot_data_quality_scorecard(self):
        """Create data quality scorecard"""
        print("Generating data quality scorecard...")
        
        fig = plt.figure(figsize=(14, 8))
        
        # Calculate quality metrics
        completeness = (self.df.notna().sum() / len(self.df)) * 100
        duplicates_pct = (self.df.duplicated().sum() / len(self.df)) * 100
        overall_completeness = completeness.mean()
        
        # Create scorecard data
        metrics = {
            'Column': self.df.columns.tolist(),
            'Completeness %': completeness.values,
            'Quality Grade': [self._get_quality_grade(x) for x in completeness.values]
        }
        
        # Main scorecard
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        scorecard_text = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                    DATA QUALITY SCORECARD                            ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Dataset: {self.filename:<52} ║
║ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<42} ║
╠═══════════════════════════════════════════════════════════════════════╣
║ DATASET METRICS                                                       ║
║   • Total Rows: {self.df.shape[0]:>50,} ║
║   • Total Columns: {self.df.shape[1]:>46} ║
║   • Total Cells: {self.df.shape[0] * self.df.shape[1]:>47,} ║
║   • Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024 / 1024:>41.2f} MB ║
╠═══════════════════════════════════════════════════════════════════════╣
║ DATA QUALITY METRICS                                                  ║
║   • Overall Completeness: {overall_completeness:>38.2f}% ║
║   • Missing Cells: {self.df.isnull().sum().sum():>43} ║
║   • Duplicate Rows: {self.df.duplicated().sum():>43} ║
║   • Duplicate Rows %: {duplicates_pct:>40.2f}% ║
╠═══════════════════════════════════════════════════════════════════════╣
║ COLUMN-LEVEL QUALITY ASSESSMENT                                       ║
║"""
        
        for col, comp in zip(self.df.columns, completeness.values):
            grade = self._get_quality_grade(comp)
            scorecard_text += f"║   {col:<30} {comp:>6.2f}%  [{grade:>8}]  ║\n"
        
        scorecard_text += f"""║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════╝

QUALITY GRADES:
  ★★★★★ EXCELLENT (95-100%)  │  ★★★☆☆ GOOD (80-94%)  │  ★★☆☆☆ FAIR (60-79%)  │  ★☆☆☆☆ POOR (<60%)
"""
        
        ax.text(0.05, 0.95, scorecard_text, transform=ax.transAxes,
               fontfamily='monospace', fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8, pad=1))
        
        plt.tight_layout()
        self._save_figure(fig, '06_quality_scorecard', dpi=150)
    
    def plot_summary_statistics(self):
        """Generate summary statistics visualization"""
        print("Generating summary statistics...")
        
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Prepare statistics
        stats_text = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║              COMPREHENSIVE DATA ANALYSIS SUMMARY                          ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<49} ║
║ Dataset File: {self.filename:<59} ║
╠════════════════════════════════════════════════════════════════════════════╣
║ SHAPE & SIZE                                                              ║
║   Shape: {self.df.shape[0]:,} rows × {self.df.shape[1]} columns
║   Cells: {self.df.shape[0] * self.df.shape[1]:,}
║   Memory: {self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
╠════════════════════════════════════════════════════════════════════════════╣
║ DATA QUALITY                                                              ║
║   Complete Rows: {(self.df.notna().all(axis=1).sum() / len(self.df) * 100):.2f}%
║   Missing Cells: {self.df.isnull().sum().sum()}
║   Duplicate Rows: {self.df.duplicated().sum()}
║   Unique Row %: {((len(self.df) - self.df.duplicated().sum()) / len(self.df) * 100):.2f}%
╠════════════════════════════════════════════════════════════════════════════╣
║ COLUMN INFORMATION                                                        ║
"""
        
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            unique = self.df[col].nunique()
            missing = self.df[col].isnull().sum()
            missing_pct = (missing / len(self.df)) * 100
            
            stats_text += f"║   {col:<25} Type: {dtype:<10} Unique: {unique:>6} Missing: {missing_pct:>5.1f}%\n"
        
        stats_text += f"""║                                                                              ║
╠════════════════════════════════════════════════════════════════════════════╣
║ VISUALIZATIONS GENERATED                                                  ║
║   ✓ Missing Values Analysis         ✓ Data Types Analysis                 ║
║   ✓ Cardinality Analysis            ✓ Numeric Distributions               ║
║   ✓ Categorical Analysis            ✓ Data Quality Scorecard              ║
║   ✓ Summary Statistics              ✓ HTML Report                         ║
║   ✓ JSON Report                                                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║ RECOMMENDATIONS                                                           ║
"""
        
        # Generate recommendations
        if self.df.isnull().sum().sum() > 0:
            stats_text += "║   • Address missing values in columns with >5% missing data\n"
        if self.df.duplicated().sum() > 0:
            stats_text += "║   • Consider removing or investigating duplicate rows\n"
        
        # Check for object columns
        cat_cols = self.df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            stats_text += "║   • Review data type conversions for categorical columns\n"
        
        stats_text += "║   • Generate visualizations for deeper analysis\n"
        
        stats_text += f"""║                                                                              ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
        
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
               fontfamily='monospace', fontsize=8.5, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8, pad=1.5))
        
        plt.tight_layout()
        self._save_figure(fig, '07_summary_statistics', dpi=150)
    
    def _get_quality_grade(self, percentage: float) -> str:
        """Get quality grade based on percentage"""
        if percentage >= 95:
            return '★★★★★'
        elif percentage >= 80:
            return '★★★★☆'
        elif percentage >= 60:
            return '★★★☆☆'
        elif percentage >= 40:
            return '★★☆☆☆'
        else:
            return '★☆☆☆☆'
    
    def generate_html_report(self):
        """Generate an HTML report"""
        print("Generating HTML report...")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Analysis Report - {self.filename}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 40px;
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            font-size: 1.1em;
            margin-bottom: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .section {{
            margin: 40px 0;
            padding: 20px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .section h2 {{
            color: #667eea;
            margin-top: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .excellent {{ color: #2ca02c; font-weight: bold; }}
        .good {{ color: #ff7f0e; font-weight: bold; }}
        .fair {{ color: #ff9800; font-weight: bold; }}
        .poor {{ color: #d62728; font-weight: bold; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #999;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Data Analysis Report</h1>
        <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Rows</div>
                <div class="metric-value">{self.df.shape[0]:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Columns</div>
                <div class="metric-value">{self.df.shape[1]}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Memory Usage</div>
                <div class="metric-value">{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Completeness</div>
                <div class="metric-value">{(self.df.notna().sum() / len(self.df) * 100).mean():.1f}%</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Column Information</h2>
            <table>
                <thead>
                    <tr>
                        <th>Column Name</th>
                        <th>Data Type</th>
                        <th>Unique Values</th>
                        <th>Missing</th>
                        <th>Missing %</th>
                        <th>Quality</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        completeness = (self.df.notna().sum() / len(self.df)) * 100
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            unique = self.df[col].nunique()
            missing = self.df[col].isnull().sum()
            missing_pct = (missing / len(self.df)) * 100
            comp = completeness[col]
            
            quality_class = 'excellent' if comp >= 95 else 'good' if comp >= 80 else 'fair' if comp >= 60 else 'poor'
            
            html_content += f"""
                    <tr>
                        <td>{col}</td>
                        <td>{dtype}</td>
                        <td>{unique:,}</td>
                        <td>{missing:,}</td>
                        <td>{missing_pct:.2f}%</td>
                        <td class="{quality_class}">{self._get_quality_grade(comp)}</td>
                    </tr>
"""
        
        html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📈 Data Quality Summary</h2>
            <ul>
                <li><strong>Complete Rows:</strong> {(self.df.notna().all(axis=1).sum() / len(self.df) * 100):.2f}%</li>
                <li><strong>Missing Cells:</strong> {self.df.isnull().sum().sum():,}</li>
                <li><strong>Duplicate Rows:</strong> {self.df.duplicated().sum():,}</li>
                <li><strong>Overall Completeness:</strong> {completeness.mean():.2f}%</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📊 Visualizations Generated</h2>
            <ul>
                <li>✓ Missing Values Analysis</li>
                <li>✓ Data Types Analysis</li>
                <li>✓ Cardinality Analysis</li>
                <li>✓ Numeric Distributions</li>
                <li>✓ Categorical Analysis</li>
                <li>✓ Data Quality Scorecard</li>
                <li>✓ Summary Statistics</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>This report was automatically generated by the Agentic Data Pipeline</p>
            <p>Dataset: {self.filename}</p>
        </div>
    </div>
</body>
</html>
"""
        
        html_file = self.output_dir / f"{self.filename}_report_{self.timestamp}.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        size_kb = html_file.stat().st_size / 1024
        print(f"  ✓ {'HTML Report':<40} ({size_kb:>6.1f} KB)")
    
    def generate_json_report(self):
        """Generate a JSON report with all metrics"""
        print("Generating JSON report...")
        
        completeness = (self.df.notna().sum() / len(self.df)) * 100
        
        report_data = {
            'metadata': {
                'filename': self.filename,
                'timestamp': datetime.now().isoformat(),
                'shape': list(self.df.shape),
                'memory_mb': float(self.df.memory_usage(deep=True).sum() / 1024 / 1024)
            },
            'quality_metrics': {
                'complete_rows_pct': float((self.df.notna().all(axis=1).sum() / len(self.df) * 100)),
                'missing_cells': int(self.df.isnull().sum().sum()),
                'duplicate_rows': int(self.df.duplicated().sum()),
                'overall_completeness_pct': float(completeness.mean())
            },
            'columns': {}
        }
        
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            unique = int(self.df[col].nunique())
            missing = int(self.df[col].isnull().sum())
            missing_pct = float((missing / len(self.df)) * 100)
            comp = float(completeness[col])
            
            report_data['columns'][col] = {
                'dtype': dtype,
                'unique_values': unique,
                'missing_count': missing,
                'missing_pct': missing_pct,
                'completeness_pct': comp,
                'quality_grade': self._get_quality_grade(comp)
            }
        
        json_file = self.output_dir / f"{self.filename}_report_{self.timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        size_kb = json_file.stat().st_size / 1024
        print(f"  ✓ {'JSON Report':<40} ({size_kb:>6.1f} KB)")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("COMPREHENSIVE DATA REPORT GENERATOR")
        print("="*70)
        print("\nUsage: python3 generate_comprehensive_report.py <cleaned_csv_file>")
        print("\nExample:")
        print("  python3 generate_comprehensive_report.py data/cleaned/dataset_cleaned_*.csv")
        print("\n" + "="*70 + "\n")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    try:
        generator = ComprehensiveReportGenerator(csv_file)
        generator.generate_all()
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
