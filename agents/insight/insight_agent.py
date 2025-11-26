import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import os

from orchestrator.types import InsightReport


class InsightAgent:
    """
    Insight Agent - Generates insights and visualizations from clean data
    """
    
    def __init__(self, config: Dict[str, Any], artifacts_path: str):
        self.config = config
        self.artifacts_path = artifacts_path
        self.logger = logging.getLogger(self.__class__.__name__)

        os.makedirs(self.artifacts_path, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def generate_insights(self, data: pd.DataFrame) -> InsightReport:
        """
        Generate comprehensive insights and visualizations from clean data
        """
        self.logger.info("Starting insight generation...")
        
        # Generate summary statistics
        summary_stats = self._generate_summary_statistics(data)
        
        # Correlation analysis
        correlations = self._analyze_correlations(data) if self.config.get('correlation_analysis', True) else None
        
        # Generate plots
        plots_generated = []
        if self.config.get('generate_plots', True):
            plots_generated = self._generate_visualizations(data)
        
        # Extract key insights
        key_insights = self._extract_key_insights(data, summary_stats, correlations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(data, summary_stats, correlations)
        
        report = InsightReport(
            summary_statistics=summary_stats,
            correlations=correlations,
            plots_generated=plots_generated,
            key_insights=key_insights,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        # Generate report files
        self._save_report(report, data)
        
        self.logger.info(f"Insight generation completed. Generated {len(plots_generated)} visualizations")
        return report
    
    def _generate_summary_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""
        stats = {
            'shape': data.shape,
            'memory_usage': data.memory_usage(deep=True).sum(),
            'dtypes': data.dtypes.value_counts().to_dict(),
            'missing_values': data.isnull().sum().to_dict(),
            'unique_values': data.nunique().to_dict()
        }
        
        # Numeric statistics
        numeric_data = data.select_dtypes(include=[np.number])
        if not numeric_data.empty:
            stats['numeric_summary'] = numeric_data.describe().to_dict()
        
        # Categorical statistics
        categorical_data = data.select_dtypes(include=['object', 'category'])
        if not categorical_data.empty:
            stats['categorical_summary'] = {}
            for col in categorical_data.columns:
                stats['categorical_summary'][col] = {
                    'unique_count': data[col].nunique(),
                    'most_frequent': data[col].mode().iloc[0] if not data[col].mode().empty else None,
                    'frequency': data[col].value_counts().head().to_dict()
                }
        
        return stats
    
    def _analyze_correlations(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Analyze correlations between numeric columns"""
        numeric_data = data.select_dtypes(include=[np.number])
        
        if numeric_data.shape[1] < 2:
            return None
        
        return numeric_data.corr()
    
    def _generate_visualizations(self, data: pd.DataFrame) -> List[str]:
        """Generate various visualizations"""
        plots = []
        
        # 1. Data overview plot
        self._create_data_overview_plot(data)
        plots.append('data_overview.png')
        
        # 2. Correlation heatmap
        if data.select_dtypes(include=[np.number]).shape[1] > 1:
            self._create_correlation_heatmap(data)
            plots.append('correlation_heatmap.png')
        
        # 3. Distribution plots for numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns[:6]  # Limit to 6
        if len(numeric_cols) > 0:
            self._create_distribution_plots(data, numeric_cols)
            plots.append('distributions.png')
        
        # 4. Categorical plots
        categorical_cols = data.select_dtypes(include=['object']).columns[:4]  # Limit to 4
        if len(categorical_cols) > 0:
            self._create_categorical_plots(data, categorical_cols)
            plots.append('categorical_analysis.png')
        
        # 5. Interactive plot
        self._create_interactive_plot(data)
        plots.append('interactive_plot.html')
        
        return plots
    
    def _create_data_overview_plot(self, data: pd.DataFrame):
        """Create a comprehensive data overview plot"""
        if data.empty:
            self.logger.warning("Data overview plot skipped: empty DataFrame")
            return
    
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
        # Missing values
        missing = data.isnull().sum()
        axes[0, 0].set_title('Missing Values by Column')
        if missing.sum() > 0:
            missing[missing > 0].plot(kind='bar', ax=axes[0, 0])
            axes[0, 0].tick_params(axis='x', rotation=45)
        else:
            axes[0, 0].text(
                0.5,
                0.5,
                'No Missing Values',
                ha='center',
                va='center',
                transform=axes[0, 0].transAxes,
            )
    
        # Data types
        dtype_counts = data.dtypes.value_counts()
        axes[0, 1].set_title('Data Types Distribution')
        if len(dtype_counts) > 0:
            axes[0, 1].pie(dtype_counts.values, labels=dtype_counts.index, autopct='%1.1f%%')
        else:
            axes[0, 1].text(
                0.5,
                0.5,
                'No Columns',
                ha='center',
                va='center',
                transform=axes[0, 1].transAxes,
            )
    
        # Unique values
        unique_counts = data.nunique()
        axes[1, 0].set_title('Unique Values per Column')
        if len(unique_counts) > 0:
            unique_counts.plot(kind='bar', ax=axes[1, 0])
            axes[1, 0].tick_params(axis='x', rotation=45)
    
        # Memory usage
        memory_usage = data.memory_usage(deep=True)
        axes[1, 1].set_title('Memory Usage by Column')
        if len(memory_usage) > 0:
            memory_usage.plot(kind='bar', ax=axes[1, 1])
            axes[1, 1].tick_params(axis='x', rotation=45)
    
        plt.tight_layout()
        plt.savefig(os.path.join(self.artifacts_path, 'data_overview.png'), dpi=300, bbox_inches='tight')
        plt.close()

    
    def _create_correlation_heatmap(self, data: pd.DataFrame):
        """Create correlation heatmap"""
        numeric_data = data.select_dtypes(include=[np.number])
        correlation = numeric_data.corr()
        
        plt.figure(figsize=(12, 8))
        mask = np.triu(np.ones_like(correlation, dtype=bool))
        sns.heatmap(correlation, mask=mask, annot=True, cmap='coolwarm', center=0,
                    square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig(os.path.join(self.artifacts_path, 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_distribution_plots(self, data: pd.DataFrame, columns: List[str]):
        """Create distribution plots for numeric columns"""
        n_cols = min(3, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        
        # Handle different axes configurations
        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        for i, col in enumerate(columns):
            row, col_idx = divmod(i, n_cols)
            ax = axes[row, col_idx]
            
            data[col].hist(bins=30, alpha=0.7, ax=ax)
            ax.set_title(f'Distribution of {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Frequency')
        
        # Hide empty subplots
        for i in range(len(columns), n_rows * n_cols):
            row, col_idx = divmod(i, n_cols)
            fig.delaxes(axes[row, col_idx])
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.artifacts_path, 'distributions.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_categorical_plots(self, data: pd.DataFrame, columns: List[str]):
        """Create plots for categorical columns"""
        n_cols = min(2, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        
        # Handle different axes configurations
        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        for i, col in enumerate(columns):
            row, col_idx = divmod(i, n_cols)
            ax = axes[row, col_idx]
            
            value_counts = data[col].value_counts().head(10)
            value_counts.plot(kind='bar', ax=ax)
            ax.set_title(f'Top 10 Values in {col}')
            ax.tick_params(axis='x', rotation=45)
        
        # Hide empty subplots
        for i in range(len(columns), n_rows * n_cols):
            row, col_idx = divmod(i, n_cols)
            fig.delaxes(axes[row, col_idx])
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.artifacts_path, 'categorical_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_interactive_plot(self, data: pd.DataFrame):
        """Create an interactive plot using Plotly"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) >= 2:
            # Scatter plot matrix
            fig = px.scatter_matrix(data, dimensions=numeric_cols[:4], title="Interactive Scatter Matrix")
            fig.write_html(os.path.join(self.artifacts_path, 'interactive_plot.html'))
        elif len(numeric_cols) == 1:
            # Histogram
            fig = px.histogram(data, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
            fig.write_html(os.path.join(self.artifacts_path, 'interactive_plot.html'))
        else:
            # Simple data summary
            fig = go.Figure()
            fig.add_annotation(text="No numeric columns available for visualization", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.write_html(os.path.join(self.artifacts_path, 'interactive_plot.html'))
    
    def _extract_key_insights(self, data: pd.DataFrame, summary_stats: Dict[str, Any], 
                            correlations: Optional[pd.DataFrame]) -> List[str]:
        """Extract key insights from the data"""
        insights = []
        
        # Data shape insights
        insights.append(f"Dataset contains {data.shape[0]:,} rows and {data.shape[1]} columns")
        
        # Missing data insights
        total_missing = data.isnull().sum().sum()
        if total_missing > 0:
            missing_pct = (total_missing / (data.shape[0] * data.shape[1])) * 100
            insights.append(f"Dataset has {total_missing:,} missing values ({missing_pct:.1f}% of total data)")
        else:
            insights.append("Dataset has no missing values")
        
        # Data type insights
        if 'dtypes' in summary_stats:
            dtype_info = summary_stats['dtypes']
            insights.append(f"Data types: {', '.join([f'{count} {dtype}' for dtype, count in dtype_info.items()])}")
        
        # Correlation insights
        if correlations is not None and correlations.shape[0] > 1:
            # Find highest correlations (excluding diagonal)
            corr_matrix = correlations.abs()
            np.fill_diagonal(corr_matrix.values, 0)
            max_corr = corr_matrix.max().max()
            if max_corr > 0.8:
                insights.append(f"Found strong correlations (max: {max_corr:.2f}) - consider multicollinearity")
            elif max_corr > 0.5:
                insights.append(f"Found moderate correlations (max: {max_corr:.2f})")
        
        # Unique value insights
        if 'unique_values' in summary_stats:
            unique_vals = summary_stats['unique_values']
            high_cardinality = [col for col, count in unique_vals.items() if count > data.shape[0] * 0.5]
            if high_cardinality:
                insights.append(f"High cardinality columns detected: {high_cardinality}")
        
        return insights
    
    def _generate_recommendations(self, data: pd.DataFrame, summary_stats: Dict[str, Any],
                                correlations: Optional[pd.DataFrame]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Memory optimization
        memory_mb = summary_stats.get('memory_usage', 0) / (1024 * 1024)
        if memory_mb > 100:
            recommendations.append(f"Dataset uses {memory_mb:.1f}MB memory - consider data type optimization")
        
        # Feature engineering suggestions
        categorical_cols = data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            recommendations.append("Consider one-hot encoding for categorical variables if using in ML models")
        
        # Correlation-based recommendations
        if correlations is not None:
            high_corr_pairs = []
            for i in range(len(correlations.columns)):
                for j in range(i+1, len(correlations.columns)):
                    if abs(correlations.iloc[i, j]) > 0.8:
                        high_corr_pairs.append((correlations.columns[i], correlations.columns[j]))
            
            if high_corr_pairs:
                recommendations.append(f"Consider removing redundant features due to high correlation: {high_corr_pairs[:3]}")
        
        # Scaling recommendations
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            scales = []
            for col in numeric_cols:
                if data[col].std() != 0:
                    scale = data[col].max() / data[col].std()
                    scales.append(scale)
            
            if len(scales) > 1 and max(scales) / min(scales) > 100:
                recommendations.append("Consider feature scaling due to different magnitude ranges")
        
        return recommendations
    
    def _save_report(self, report: InsightReport, data: pd.DataFrame):
        """Save comprehensive report to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save HTML report
        html_content = self._generate_html_report(report, data)
        with open(os.path.join(self.artifacts_path, f'insight_report_{timestamp}.html'), 'w') as f:
            f.write(html_content)
        
        # Save correlations to CSV if available
        if report.correlations is not None:
            report.correlations.to_csv(os.path.join(self.artifacts_path, f'correlations_{timestamp}.csv'))
    
    def _generate_html_report(self, report: InsightReport, data: pd.DataFrame) -> str:
        """Generate HTML report"""
        # Build small tables
        missing_table_rows = []
        missing = report.summary_statistics.get("missing_values", {})
        for col, val in missing.items():
            missing_table_rows.append(f"<tr><td>{col}</td><td>{val}</td></tr>")
    
        dtype_table_rows = []
        dtypes = report.summary_statistics.get("dtypes", {})
        for dtype, count in dtypes.items():
            dtype_table_rows.append(f"<tr><td>{dtype}</td><td>{count}</td></tr>")
    
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Insights Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2 {{ color: #333; }}
                .section {{ margin: 20px 0; }}
                .insight {{ background: #f0f8ff; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .recommendation {{ background: #f0fff0; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Data Insights Report</h1>
            <p><strong>Generated:</strong> {report.timestamp}</p>
            
            <div class="section">
                <h2>Dataset Overview</h2>
                <p><strong>Shape:</strong> {data.shape[0]:,} rows × {data.shape[1]} columns</p>
                <p><strong>Memory Usage:</strong> {report.summary_statistics.get('memory_usage', 0) / (1024*1024):.2f} MB</p>
            </div>
    
            <div class="section">
                <h2>Missing Values by Column</h2>
                <table>
                    <tr><th>Column</th><th>Missing Count</th></tr>
                    {''.join(missing_table_rows)}
                </table>
            </div>
    
            <div class="section">
                <h2>Data Types Summary</h2>
                <table>
                    <tr><th>Data Type</th><th>Count</th></tr>
                    {''.join(dtype_table_rows)}
                </table>
            </div>
            
            <div class="section">
                <h2>Key Insights</h2>
                {''.join([f'<div class="insight">• {insight}</div>' for insight in report.key_insights])}
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {''.join([f'<div class="recommendation">• {rec}</div>' for rec in report.recommendations])}
            </div>
            
            <div class="section">
                <h2>Generated Visualizations</h2>
                <ul>
                {''.join([f'<li>{plot}</li>' for plot in report.plots_generated])}
                </ul>
            </div>
        </body>
        </html>
        """
        return html
