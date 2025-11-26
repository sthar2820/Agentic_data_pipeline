#!/usr/bin/env python3
"""
Advanced Visualizations for Data Analysis
Generates detailed charts, reports, and insights
Usage: python3 advanced_visualizations.py <cleaned_csv_file>
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class AdvancedVisualizations:
    """Generate comprehensive data visualizations and analysis"""
    
    def __init__(self, csv_file: str, output_dir: str = "data/visualizations"):
        self.csv_file = csv_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = pd.read_csv(csv_file)
        self.filename = Path(csv_file).stem
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"Dataset loaded: {self.df.shape[0]:,} rows x {self.df.shape[1]} columns")
    
    def generate_all(self):
        """Generate all visualizations"""
        print("\nGenerating advanced visualizations...")
        
        self.plot_missing_values_heatmap()
        self.plot_data_types()
        self.plot_cardinality_analysis()
        self.plot_column_statistics()
        self.plot_text_length_analysis()
        self.plot_unique_values_distribution()
        self.plot_data_quality_scorecard()
        self.plot_summary_report()
        
        print(f"\nAll visualizations saved to: {self.output_dir}/")
    
    def _save_figure(self, fig, name: str):
        """Save figure with consistent naming"""
        output_path = self.output_dir / f"{self.filename}_{name}_{self.timestamp}.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        size_kb = output_path.stat().st_size / 1024
        print(f"  ✓ {name} ({size_kb:.0f} KB)")
        return output_path
    
    def plot_missing_values_heatmap(self):
        """Advanced missing values heatmap"""
        print("  - Missing values heatmap")
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [1, 3]})
        
        # Top: Missing percentage bar chart
        missing_pct = (self.df.isnull().sum() / len(self.df)) * 100
        colors = ['#d62728' if x > 50 else '#ff7f0e' if x > 20 else '#2ca02c' for x in missing_pct]
        missing_pct.plot(kind='barh', ax=axes[0], color=colors)
        axes[0].set_xlabel('Missing Percentage (%)', fontsize=11, fontweight='bold')
        axes[0].set_title('Missing Data by Column', fontsize=12, fontweight='bold')
        axes[0].axvline(x=20, color='orange', linestyle='--', alpha=0.5, label='High (20%)')
        axes[0].axvline(x=50, color='red', linestyle='--', alpha=0.5, label='Critical (50%)')
        axes[0].legend()
        
        # Bottom: Heatmap
        missing_data = self.df.isnull().astype(int)
        sns.heatmap(missing_data, cmap='RdYlGn_r', cbar_kws={'label': 'Missing'}, 
                   ax=axes[1], yticklabels=False)
        axes[1].set_title('Missing Data Pattern', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        self._save_figure(fig, '01_missing_values_heatmap')
    
    def plot_data_types(self):
        """Data type analysis"""
        print("  - Data type analysis")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Data type distribution
        dtype_counts = self.df.dtypes.value_counts()
        dtype_counts.plot(kind='bar', ax=axes[0], color='steelblue', edgecolor='black')
        axes[0].set_title('Data Type Distribution', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Data Type')
        axes[0].set_ylabel('Count')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Column info table
        col_info = []
        for col in self.df.columns:
            col_info.append({
                'Column': col,
                'Type': str(self.df[col].dtype),
                'Non-Null': self.df[col].notna().sum(),
                'Unique': self.df[col].nunique(),
                'Memory': f"{self.df[col].memory_usage(deep=True) / 1024:.1f} KB"
            })
        
        table_df = pd.DataFrame(col_info)
        axes[1].axis('tight')
        axes[1].axis('off')
        table = axes[1].table(cellText=table_df.values, colLabels=table_df.columns,
                            cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        axes[1].set_title('Column Information', fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._save_figure(fig, '02_data_types')
    
    def plot_cardinality_analysis(self):
        """Cardinality analysis"""
        print("  - Cardinality analysis")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        cardinality = self.df.nunique().sort_values(ascending=True)
        colors = ['#1f77b4' if x < 100 else '#ff7f0e' if x < 1000 else '#d62728' 
                 for x in cardinality]
        
        cardinality.plot(kind='barh', ax=ax, color=colors, edgecolor='black')
        ax.set_xlabel('Number of Unique Values', fontsize=11, fontweight='bold')
        ax.set_title('Column Cardinality (Unique Values)', fontsize=13, fontweight='bold')
        
        # Add value labels
        for i, v in enumerate(cardinality):
            ax.text(v + 20, i, str(v), va='center', fontweight='bold')
        
        plt.tight_layout()
        self._save_figure(fig, '03_cardinality_analysis')
    
    def plot_column_statistics(self):
        """Detailed column statistics"""
        print("  - Column statistics report")
        
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111)
        
        stats_text = "DETAILED COLUMN STATISTICS REPORT\n"
        stats_text += "=" * 80 + "\n\n"
        
        for col in self.df.columns:
            stats_text += f"{col.upper()}\n"
            stats_text += "-" * 80 + "\n"
            stats_text += f"  Data Type: {self.df[col].dtype}\n"
            stats_text += f"  Non-Null Count: {self.df[col].notna().sum():,}\n"
            stats_text += f"  Null Count: {self.df[col].isnull().sum()} ({(self.df[col].isnull().sum()/len(self.df)*100):.2f}%)\n"
            stats_text += f"  Unique Values: {self.df[col].nunique()}\n"
            stats_text += f"  Memory Usage: {self.df[col].memory_usage(deep=True) / 1024:.2f} KB\n"
            
            if self.df[col].dtype in ['int64', 'float64']:
                stats_text += f"  Min: {self.df[col].min()}\n"
                stats_text += f"  Max: {self.df[col].max()}\n"
                stats_text += f"  Mean: {self.df[col].mean():.4f}\n"
                stats_text += f"  Median: {self.df[col].median():.4f}\n"
                stats_text += f"  Std Dev: {self.df[col].std():.4f}\n"
            elif self.df[col].dtype == 'object':
                stats_text += f"  Most Common: {self.df[col].value_counts().index[0]}\n"
                stats_text += f"  Frequency: {self.df[col].value_counts().iloc[0]}\n"
                avg_len = self.df[col].astype(str).str.len().mean()
                stats_text += f"  Avg Length: {avg_len:.2f} characters\n"
            
            stats_text += "\n"
        
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontfamily='monospace',
               fontsize=8, verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor='wheat', alpha=0.3))
        ax.axis('off')
        
        plt.tight_layout()
        self._save_figure(fig, '04_column_statistics')
    
    def plot_text_length_analysis(self):
        """Text length analysis for string columns"""
        print("  - Text length analysis")
        
        text_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        if len(text_cols) == 0:
            print("    (No text columns to analyze)")
            return
        
        n_cols = min(len(text_cols), 4)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for idx, col in enumerate(text_cols[:4]):
            text_lengths = self.df[col].astype(str).str.len()
            
            axes[idx].hist(text_lengths, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
            axes[idx].set_title(f'{col} - Text Length Distribution', fontweight='bold')
            axes[idx].set_xlabel('Text Length (characters)')
            axes[idx].set_ylabel('Frequency')
            axes[idx].grid(True, alpha=0.3)
            
            # Add statistics
            stats_text = f"Mean: {text_lengths.mean():.1f}\nMedian: {text_lengths.median():.1f}\nStd: {text_lengths.std():.1f}"
            axes[idx].text(0.97, 0.97, stats_text, transform=axes[idx].transAxes,
                          verticalalignment='top', horizontalalignment='right',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                          fontsize=9)
        
        # Hide unused subplots
        for idx in range(n_cols, 4):
            axes[idx].axis('off')
        
        plt.tight_layout()
        self._save_figure(fig, '05_text_length_analysis')
    
    def plot_unique_values_distribution(self):
        """Distribution of unique values"""
        print("  - Unique values distribution")
        
        fig = plt.figure(figsize=(14, 8))
        
        # Create a 2x2 grid
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. Unique value counts
        ax1 = fig.add_subplot(gs[0, 0])
        unique_counts = self.df.nunique().sort_values()
        unique_counts.plot(kind='barh', ax=ax1, color='coral', edgecolor='black')
        ax1.set_xlabel('Number of Unique Values')
        ax1.set_title('Unique Value Count by Column', fontweight='bold')
        
        # 2. Cardinality ratio
        ax2 = fig.add_subplot(gs[0, 1])
        cardinality_ratio = (self.df.nunique() / len(self.df) * 100).sort_values()
        colors_card = ['green' if x < 10 else 'orange' if x < 50 else 'red' for x in cardinality_ratio]
        cardinality_ratio.plot(kind='barh', ax=ax2, color=colors_card, edgecolor='black')
        ax2.set_xlabel('Cardinality Ratio (%)')
        ax2.set_title('Cardinality Ratio (Unique/Total)', fontweight='bold')
        
        # 3. Data completeness
        ax3 = fig.add_subplot(gs[1, 0])
        completeness = (self.df.notna().sum() / len(self.df) * 100).sort_values(ascending=True)
        colors_comp = ['red' if x < 90 else 'orange' if x < 99 else 'green' for x in completeness]
        completeness.plot(kind='barh', ax=ax3, color=colors_comp, edgecolor='black')
        ax3.set_xlabel('Completeness (%)')
        ax3.set_title('Data Completeness by Column', fontweight='bold')
        
        # 4. Summary statistics
        ax4 = fig.add_subplot(gs[1, 1])
        summary_data = {
            'Total Rows': [len(self.df)],
            'Total Columns': [len(self.df.columns)],
            'Total Cells': [len(self.df) * len(self.df.columns)],
            'Missing Cells': [self.df.isnull().sum().sum()],
            'Missing %': [self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns)) * 100],
            'Avg Unique/Col': [self.df.nunique().mean()],
            'Memory (MB)': [self.df.memory_usage(deep=True).sum() / 1024 / 1024]
        }
        
        summary_text = "DATASET SUMMARY\n" + "=" * 40 + "\n"
        for key, val in summary_data.items():
            if isinstance(val[0], float):
                summary_text += f"{key}: {val[0]:.2f}\n"
            else:
                summary_text += f"{key}: {val[0]:,.0f}\n"
        
        ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes, fontfamily='monospace',
                fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        ax4.axis('off')
        
        plt.suptitle('Data Quality and Uniqueness Analysis', fontsize=14, fontweight='bold', y=0.98)
        self._save_figure(fig, '06_unique_values_distribution')
    
    def plot_data_quality_scorecard(self):
        """Data quality scorecard"""
        print("  - Data quality scorecard")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Calculate scores
        completeness = (self.df.notna().sum() / len(self.df) * 100)
        unique_ratio = (self.df.nunique() / len(self.df) * 100)
        
        # 1. Completeness scorecard
        ax = axes[0, 0]
        colors_comp = completeness.map(lambda x: 'green' if x >= 99 else 'orange' if x >= 90 else 'red')
        completeness.plot(kind='barh', ax=ax, color=colors_comp, edgecolor='black')
        ax.set_xlim([0, 105])
        ax.set_xlabel('Completeness (%)')
        ax.set_title('Data Completeness Score', fontweight='bold')
        ax.axvline(x=99, color='green', linestyle='--', alpha=0.5, label='Excellent (99%)')
        ax.axvline(x=90, color='orange', linestyle='--', alpha=0.5, label='Good (90%)')
        ax.legend(fontsize=8)
        
        # 2. Cardinality scorecard
        ax = axes[0, 1]
        colors_card = unique_ratio.map(lambda x: 'red' if x < 10 else 'orange' if x < 50 else 'green')
        unique_ratio.plot(kind='barh', ax=ax, color=colors_card, edgecolor='black')
        ax.set_xlabel('Cardinality (%)')
        ax.set_title('Cardinality Score', fontweight='bold')
        
        # 3. Overall quality gauge
        ax = axes[1, 0]
        avg_completeness = completeness.mean()
        avg_cardinality = unique_ratio.mean()
        overall_score = (avg_completeness + min(avg_cardinality, 100)) / 2
        
        ax.barh(['Overall Quality'], [overall_score], color='steelblue', edgecolor='black')
        ax.set_xlim([0, 105])
        ax.set_xlabel('Quality Score')
        ax.set_title('Overall Data Quality', fontweight='bold')
        
        # Add rating
        if overall_score >= 90:
            rating = 'EXCELLENT'
            color = 'green'
        elif overall_score >= 80:
            rating = 'GOOD'
            color = 'orange'
        else:
            rating = 'FAIR'
            color = 'red'
        
        ax.text(overall_score/2, 0, f'{overall_score:.1f}\n{rating}', 
               ha='center', va='center', fontweight='bold', fontsize=12, color='white')
        
        # 4. Quality metrics table
        ax = axes[1, 1]
        metrics_data = {
            'Metric': ['Avg Completeness', 'Avg Cardinality', 'Missing Cells', 'Total Rows', 'Total Columns'],
            'Value': [f'{avg_completeness:.1f}%', f'{avg_cardinality:.1f}%', 
                     f'{self.df.isnull().sum().sum()}', f'{len(self.df):,}', f'{len(self.df.columns)}']
        }
        
        metrics_df = pd.DataFrame(metrics_data)
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=metrics_df.values, colLabels=metrics_df.columns,
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        plt.tight_layout()
        self._save_figure(fig, '07_quality_scorecard')
    
    def plot_summary_report(self):
        """Comprehensive summary report"""
        print("  - Summary report")
        
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111)
        
        report_text = f"""
COMPREHENSIVE DATA ANALYSIS REPORT
{'=' * 90}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Dataset: {self.filename}

DATASET OVERVIEW
{'-' * 90}
Shape: {self.df.shape[0]:,} rows x {self.df.shape[1]} columns
Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
Total Cells: {self.df.shape[0] * self.df.shape[1]:,}

DATA QUALITY METRICS
{'-' * 90}
Complete Rows: {(self.df.notna().all(axis=1).sum() / len(self.df) * 100):.2f}%
Average Completeness: {(self.df.notna().sum() / len(self.df) * 100).mean():.2f}%
Total Missing Cells: {self.df.isnull().sum().sum()}
Duplicate Rows: {self.df.duplicated().sum()}

COLUMN ANALYSIS
{'-' * 90}
Column Name                    Type          Non-Null  Unique  Missing%  Quality
{'-' * 90}
"""
        
        for col in self.df.columns:
            missing_pct = (self.df[col].isnull().sum() / len(self.df)) * 100
            quality = max(0, 100 - missing_pct)
            report_text += f"{col[:28]:<28} {str(self.df[col].dtype)[:12]:<12} {self.df[col].notna().sum():>8} {self.df[col].nunique():>7} {missing_pct:>8.2f}% {quality:>7.1f}%\n"
        
        report_text += f"\n{'=' * 90}\n\nGENERATED VISUALIZATIONS:\n"
        report_text += "  1. Missing Values Heatmap\n"
        report_text += "  2. Data Types Analysis\n"
        report_text += "  3. Cardinality Analysis\n"
        report_text += "  4. Column Statistics\n"
        report_text += "  5. Text Length Analysis\n"
        report_text += "  6. Unique Values Distribution\n"
        report_text += "  7. Quality Scorecard\n"
        report_text += "  8. Summary Report\n"
        
        ax.text(0.05, 0.95, report_text, transform=ax.transAxes, fontfamily='monospace',
               fontsize=8.5, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))
        ax.axis('off')
        
        plt.tight_layout()
        self._save_figure(fig, '08_summary_report')


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 advanced_visualizations.py <cleaned_csv_file>")
        print("\nExample:")
        print("  python3 advanced_visualizations.py data/cleaned/us-shein-automotive-4110_cleaned_*.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not Path(csv_file).exists():
        print(f"ERROR: File not found: {csv_file}")
        sys.exit(1)
    
    print("=" * 70)
    print("ADVANCED DATA VISUALIZATIONS")
    print("=" * 70)
    
    viz = AdvancedVisualizations(csv_file)
    viz.generate_all()
    
    print("\n" + "=" * 70)
    print("All visualizations generated successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
